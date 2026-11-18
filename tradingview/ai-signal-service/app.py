"""1PC AI signal service.

TradingView sends the 1PC Headline & Storyline indicator's alerts here (webhook, JSON
alerts turned on in the indicator). For every PREPARE alert, Claude reviews the setup - the
zone, the indicator's proposed limit price and the last candles - and answers with its own
decision and an exact entry price inside the zone. Results are shown on the service's page
and, if configured, sent to Telegram.

Environment:
  ANTHROPIC_API_KEY   your Anthropic API key (required unless DRY_RUN=1)
  WEBHOOK_TOKEN       a secret of your choice; TradingView calls /webhook?token=<it>,
                      and the page is /?token=<it>
  CLAUDE_MODEL        optional, default claude-opus-5-5
  CLAUDE_EFFORT       optional, default high (low | medium | high | xhigh | max)
  TELEGRAM_BOT_TOKEN  optional, with TELEGRAM_CHAT_ID: also send each verdict to Telegram
  TELEGRAM_CHAT_ID
  DATA_FILE           optional, default signals.jsonl (history kept across restarts)
  DRY_RUN             optional, 1 = don't call Claude, answer with a test verdict
"""

from __future__ import annotations

import collections
import hmac
import html
import json
import logging
import os
import threading
import time
import urllib.parse
import urllib.request

import anthropic
from fastapi import BackgroundTasks, FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse

log = logging.getLogger("1pc-ai")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

MODEL = os.environ.get("CLAUDE_MODEL", "claude-opus-5-5")
EFFORT = os.environ.get("CLAUDE_EFFORT", "high")
TOKEN = os.environ.get("WEBHOOK_TOKEN", "")
DRY_RUN = os.environ.get("DRY_RUN") == "1"
DATA_FILE = os.environ.get("DATA_FILE", "signals.jsonl")
TG_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TG_CHAT = os.environ.get("TELEGRAM_CHAT_ID", "")

if not TOKEN:
    raise SystemExit("Set WEBHOOK_TOKEN to a secret of your choice before starting the service.")

client = None if DRY_RUN else anthropic.Anthropic(max_retries=3)

SIGNALS: collections.deque[dict] = collections.deque(maxlen=200)
LOCK = threading.Lock()

SYSTEM_PROMPT = """You review trade setups for a discretionary gold / FX trader who uses the \
"1PC Headline & Storyline" method:

- Headline: a fresh key zone on H4, H1 or M30. Zone types:
  * "SNR (DBD)" / "SNR (RBR)": a swing high (low) that price left with drop-base-drop \
(rally-base-rally); red = supply / sell zone, blue = demand / buy zone.
  * "base (DBD)" / "base (RBR)": the base between the two legs.
  * "breakout": a swing level or zone that price closed through; it now plays the opposite \
role (broken support is now resistance and vice versa).
  Fresh means price is coming back to the zone for the first time.
- Storyline: what price does at the zone on M15 / M30. The trader enters with a limit order \
inside the zone after price shows a rejection there (a "smart" entry), or after an M / W \
pattern breaks its neckline and retests it.
- Risk is fixed by the trader: the stop loss and take profit are a fixed number of points \
from the entry (given in the setup). Do not change them; only the entry price matters.

You get the setup the indicator found (side, its proposed limit price, the zone, ATR values \
and the most recent candles as [time_ms, open, high, low, close], oldest first). Decide:

- "take": the setup is sound; give the exact limit price you would use. It must be inside \
the zone (between zone bottom and top) and on the right side of the current price (above it \
for a sell limit, below it for a buy limit) unless you choose a market entry.
- "wait": the idea is right but the entry is premature; give the price you would wait for.
- "skip": the setup is weak or invalid (for example price already closed through the zone, \
momentum is strongly against the trade, or the zone is too far away / already used).

Judge from the candles: the reaction inside the zone (wicks, closes back through the zone \
edge, engulfing), momentum into the zone, where liquidity sits (recent equal highs / lows \
just beyond the zone), and whether the fixed stop is likely to survive normal noise at the \
current ATR. Prefer an entry that improves the price versus the indicator's limit when the \
candles support it; otherwise keep the indicator's price. Keep the reasoning to 2-4 short \
sentences a trader can read on a phone. This is decision support, not financial advice."""

VERDICT_SCHEMA = {
    "type": "object",
    "properties": {
        "decision": {"type": "string", "enum": ["take", "wait", "skip"]},
        "side": {"type": "string", "enum": ["buy", "sell"]},
        "entry_type": {"type": "string", "enum": ["limit", "market"]},
        "entry_price": {"type": "number"},
        "invalidation_price": {
            "type": "number",
            "description": "Price at which the idea is wrong (beyond the zone).",
        },
        "confidence": {"type": "integer", "description": "0-100"},
        "reasoning": {"type": "string"},
    },
    "required": ["decision", "side", "entry_type", "entry_price", "invalidation_price", "confidence", "reasoning"],
    "additionalProperties": False,
}


# ── storage ────────────────────────────────────────────────────────────────────
def _load_history() -> None:
    # The file is append-only: a record is written when it arrives and again when Claude's
    # verdict is in. Keep the last line for each id.
    latest: dict[str, dict] = {}
    try:
        with open(DATA_FILE, encoding="utf-8") as fh:
            for line in fh:
                if line.strip():
                    rec = json.loads(line)
                    latest[rec.get("id", str(len(latest)))] = rec
    except FileNotFoundError:
        return
    except Exception:  # a corrupt history file should not stop the service
        log.exception("could not read %s", DATA_FILE)
    for rec in sorted(latest.values(), key=lambda r: r.get("received_at", 0))[-SIGNALS.maxlen:]:
        if rec.get("status") == "analysing":  # the service restarted before Claude answered
            rec.update(status="error", error="service restarted before the verdict arrived")
        SIGNALS.appendleft(rec)


def _save(record: dict) -> None:
    with LOCK:
        SIGNALS.appendleft(record)
        try:
            with open(DATA_FILE, "a", encoding="utf-8") as fh:
                fh.write(json.dumps(record) + "\n")
        except OSError:
            log.exception("could not write %s", DATA_FILE)


def _update(record: dict) -> None:
    with LOCK:
        try:
            with open(DATA_FILE, "a", encoding="utf-8") as fh:
                fh.write(json.dumps(record) + "\n")
        except OSError:
            log.exception("could not write %s", DATA_FILE)


# ── Claude ─────────────────────────────────────────────────────────────────────
def ask_claude(setup: dict) -> dict:
    if DRY_RUN:
        zone = setup.get("zone") or {}
        return {
            "decision": "take",
            "side": setup.get("side", "sell"),
            "entry_type": "limit",
            "entry_price": setup.get("entry"),
            "invalidation_price": zone.get("top") if setup.get("side") == "sell" else zone.get("bottom"),
            "confidence": 50,
            "reasoning": "Test verdict (DRY_RUN=1): Claude was not called.",
        }

    user_text = (
        "New setup from the indicator. Review it and give your verdict.\n\n"
        + json.dumps(setup, separators=(",", ":"))
    )
    response = client.beta.messages.create(
        model=MODEL,
        max_tokens=16000,
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",  # if a safety classifier declines, the API retries on a fallback model
        output_config={"effort": EFFORT, "format": {"type": "json_schema", "schema": VERDICT_SCHEMA}},
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_text}],
    )
    if response.stop_reason == "refusal":
        category = response.stop_details.category if response.stop_details else None
        raise RuntimeError(f"Claude declined to review this setup (category: {category})")
    if response.stop_reason == "max_tokens":
        raise RuntimeError("Claude's answer was cut off (max_tokens)")
    text = next(b.text for b in response.content if b.type == "text")
    verdict = json.loads(text)
    verdict["model"] = response.model
    return verdict


def check_verdict(setup: dict, verdict: dict) -> list[str]:
    """Sanity checks on Claude's price; returned as warnings shown next to the verdict."""
    notes = []
    zone = setup.get("zone") or {}
    top, bot = zone.get("top"), zone.get("bottom")
    entry = verdict.get("entry_price")
    if isinstance(entry, (int, float)) and isinstance(top, (int, float)) and isinstance(bot, (int, float)):
        if not (bot <= entry <= top) and verdict.get("decision") != "skip":
            notes.append(f"entry {entry} is outside the zone {bot}-{top}")
    if verdict.get("side") != setup.get("side"):
        notes.append("Claude's side differs from the indicator's")
    if not 0 <= int(verdict.get("confidence", 0)) <= 100:
        notes.append("confidence out of range")
    return notes


def fixed_risk(setup: dict, entry: float, side: str) -> tuple[float | None, float | None]:
    point, slp, tpp = setup.get("point"), setup.get("sl_points"), setup.get("tp_points")
    if not all(isinstance(v, (int, float)) for v in (entry, point, slp, tpp)):
        return None, None
    d = 1 if side == "buy" else -1
    return round(entry - d * slp * point, 5), round(entry + d * tpp * point, 5)


def analyse(record: dict) -> None:
    setup = record["setup"]
    try:
        verdict = ask_claude(setup)
        sl, tp = fixed_risk(setup, verdict.get("entry_price"), verdict.get("side", setup.get("side")))
        record.update(status="done", verdict=verdict, ai_sl=sl, ai_tp=tp, notes=check_verdict(setup, verdict))
    except anthropic.RateLimitError:
        record.update(status="error", error="Claude rate limit reached - try again shortly")
    except anthropic.APIStatusError as exc:
        record.update(status="error", error=f"Claude API error {exc.status_code}: {exc.message}")
    except anthropic.APIConnectionError:
        record.update(status="error", error="Could not reach the Claude API")
    except (RuntimeError, ValueError, StopIteration, json.JSONDecodeError) as exc:
        record.update(status="error", error=str(exc) or exc.__class__.__name__)
    record["done_at"] = time.time()
    _update(record)
    notify(record)


# ── Telegram (optional) ───────────────────────────────────────────────────────
def notify(record: dict) -> None:
    if not (TG_TOKEN and TG_CHAT):
        return
    s, v = record["setup"], record.get("verdict") or {}
    zone = s.get("zone") or {}
    if record["status"] == "done":
        text = (
            f"1PC AI · {s.get('symbol')} {str(v.get('side', '')).upper()} · {str(v.get('decision', '')).upper()}\n"
            f"AI entry: {v.get('entry_type')} {v.get('entry_price')}  (indicator: {s.get('entry')})\n"
            f"SL {record.get('ai_sl')} · TP {record.get('ai_tp')} · confidence {v.get('confidence')}\n"
            f"Zone: {zone.get('name')} {zone.get('bottom')}-{zone.get('top')}\n{v.get('reasoning')}"
        )
    else:
        text = f"1PC AI · {s.get('symbol')}: no verdict ({record.get('error')})"
    data = urllib.parse.urlencode({"chat_id": TG_CHAT, "text": text}).encode()
    try:
        urllib.request.urlopen(f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage", data=data, timeout=10).read()
    except Exception:
        log.exception("Telegram message failed")


# ── web app ────────────────────────────────────────────────────────────────────
app = FastAPI(title="1PC AI signal service")
_load_history()


def _check_token(token: str) -> None:
    if not hmac.compare_digest(token or "", TOKEN):
        raise HTTPException(status_code=403, detail="wrong token")


@app.get("/health")
def health() -> dict:
    return {"ok": True, "model": MODEL, "dry_run": DRY_RUN}


@app.post("/webhook")
async def webhook(request: Request, background: BackgroundTasks, token: str = "") -> dict:
    _check_token(token)
    raw = (await request.body()).decode("utf-8", "replace")
    try:
        setup = json.loads(raw)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Body is not JSON. Turn on 'Send alerts as JSON for the AI service' in the indicator.")
    if not isinstance(setup, dict):
        raise HTTPException(status_code=400, detail="Expected a JSON object")
    record = {"id": f"{time.time():.6f}", "received_at": time.time(), "setup": setup}
    if setup.get("event") == "prepare":
        record["status"] = "analysing"
        _save(record)
        background.add_task(analyse, record)  # reply to TradingView at once; Claude runs after
    else:
        record["status"] = "info"
        _save(record)
    return {"ok": True}


def _fmt_time(ts: float | None) -> str:
    return time.strftime("%d %b %H:%M", time.gmtime(ts)) + " UTC" if ts else ""


@app.get("/", response_class=HTMLResponse)
def page(token: str = "") -> str:
    _check_token(token)
    rows = []
    with LOCK:
        items = list(SIGNALS)
    for r in items[:60]:
        s, v = r.get("setup", {}), r.get("verdict") or {}
        zone = s.get("zone") or {}
        side = str(v.get("side") or s.get("side") or "").upper()
        cls = "sell" if side == "SELL" else "buy"
        if r.get("status") == "info":
            rows.append(
                f"<div class='card info'><div class='head'><span><b>{html.escape(str(s.get('symbol')))}</b> "
                f"{html.escape(str(s.get('event')))} {html.escape(str(s.get('side', '')).upper())} @ "
                f"{html.escape(str(s.get('entry')))}</span><span class='t'>{_fmt_time(r.get('received_at'))}</span></div></div>"
            )
            continue
        if r.get("status") == "analysing":
            verdict = "<p class='muted'>Claude is analysing…</p>"
        elif r.get("status") == "error":
            verdict = f"<p class='err'>No verdict: {html.escape(str(r.get('error')))}</p>"
        else:
            notes = "".join(f"<li>{html.escape(n)}</li>" for n in r.get("notes") or [])
            verdict = (
                f"<p class='big'>{html.escape(str(v.get('decision', '')).upper())} · {html.escape(str(v.get('entry_type')))} "
                f"<b>{html.escape(str(v.get('entry_price')))}</b></p>"
                f"<p>SL {html.escape(str(r.get('ai_sl')))} · TP {html.escape(str(r.get('ai_tp')))} · "
                f"confidence {html.escape(str(v.get('confidence')))} · invalid beyond {html.escape(str(v.get('invalidation_price')))}</p>"
                f"<p>{html.escape(str(v.get('reasoning')))}</p>"
                + (f"<ul class='err'>{notes}</ul>" if notes else "")
            )
        rows.append(
            f"<div class='card {cls}'><div class='head'><b>{html.escape(str(s.get('symbol')))} {side}</b>"
            f"<span class='t'>{_fmt_time(r.get('received_at'))}</span></div>"
            f"<p class='muted'>Indicator: {html.escape(str(s.get('method')))} limit {html.escape(str(s.get('entry')))} · "
            f"score {html.escape(str(s.get('score')))} · {html.escape(str(zone.get('name')))} "
            f"{html.escape(str(zone.get('bottom')))}-{html.escape(str(zone.get('top')))}</p>{verdict}</div>"
        )
    body = "".join(rows) or "<p class='muted'>No signals yet. They appear here when a PREPARE alert arrives.</p>"
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><meta http-equiv="refresh" content="20">
<title>1PC AI signals</title><style>
:root {{ --bg:#f6f7f9; --card:#fff; --fg:#1b1d21; --muted:#6b7280; --sell:#f23645; --buy:#2962ff; --err:#b42318; }}
@media (prefers-color-scheme: dark) {{ :root {{ --bg:#0f1115; --card:#181b21; --fg:#e8eaed; --muted:#9aa0a6; }} }}
body {{ margin:0; padding:16px; background:var(--bg); color:var(--fg); font:15px/1.45 system-ui, sans-serif; }}
h1 {{ font-size:18px; margin:0 0 12px; }} .card {{ background:var(--card); border-radius:10px; padding:12px 14px; margin:0 0 10px;
border-left:4px solid var(--muted); }} .sell {{ border-color:var(--sell); }} .buy {{ border-color:var(--buy); }}
.head {{ display:flex; justify-content:space-between; gap:8px; }} .t, .muted {{ color:var(--muted); font-size:13px; }}
.big {{ font-size:17px; margin:6px 0; }} .err {{ color:var(--err); }} p {{ margin:4px 0; }} .info {{ font-size:13px; }}
</style></head><body><h1>1PC AI signals · {html.escape(MODEL)}{' · DRY RUN' if DRY_RUN else ''}</h1>{body}
<p class="muted">Refreshes every 20 s. Decision support only, not financial advice.</p></body></html>"""
