# 88 Sharingan (TradingView indicator, Pine Script v6)

A multi-timeframe setup assistant built for **XAUUSD**. It is meant to make chart reading consistent, not to replace discretionary judgement.

> Direction (Daily / H4) → Key zone (H4 / H1) → Lower-timeframe confirmation (M30 / M15 / M5 / M1) → Entry
> **No confirmation, no entry.**

Source: [`88_sharingan.pine`](88_sharingan.pine)

## Install

1. In TradingView, open **Pine Editor** and create a new indicator. Paste the contents of `88_sharingan.pine`, save, then click **Add to chart**.
2. Use an **M1 chart** to get all four confirmation timeframes, or an **M5 chart** for M5/M15/M30. The chart must be H1 or lower. Any confirmation timeframe below the chart timeframe shows as **N/A**.
3. Alerts: create an alert on the indicator and choose **"Any alert() function call"**. This alert's message includes the confirmation type, timeframe, zone and bias. The two `alertcondition`s ("88 Sharingan BUY/SELL") send a short fixed message instead.

---

## 1. Your stated strategy vs. my coding assumptions

| Area | Your rule (as stated) | How it is coded (my assumption, adjustable) |
|---|---|---|
| Direction | Daily = broader context, H4 = working direction; show both; flag conflicts | Bias comes from candle-close BOS of confirmed swings. **2-break rule** (your choice): bias = direction of the last two breaks if they agree; one counter-break (CHoCH) means **Neutral**. Alignment is **Relaxed** (your choice): H4 must be directional and Daily must not be opposite. D vs H4 opposite = **MIXED**, no signals. |
| H1 | Refine the H4 setup; show H1 alignment separately | H1 zones are used for setups. H1 bias is shown separately and is **display-only** by default; it can be set to "not opposite" or "must agree". |
| Zones | S/R, supply/demand, breakouts, rejections/engulfing on H4 and H1 | S/R = wick-to-body area of a confirmed swing candle. S/D = base + impulse. Close beyond = breakout (zone flips once). Wick beyond with close back inside = sweep. Engulfing/rejection = markers only. |
| Zone eligibility | Price reaches a relevant support/demand (resistance/supply) zone | **Any H4 or H1 zone** on the correct side (your choice). Alternatives: "H1 inside H4" or "H4 only". |
| Confirmation | Breakout, Chart Pattern, Price Action; any one enabled TF is enough | Breakout and patterns trigger. Price action is an optional *filter* (off by default) and never triggers an entry by itself. |
| Breakout | Close beyond a local structure level; close or retest entry | Level = latest confirmed LTF swing. Retest area = level → base (your choice). |
| Patterns | DT, DB, H&S, inverse H&S; developing vs confirmed; neckline close, optional retest | Built from confirmed alternating swings, with ATR-based tolerances. |
| Signal hygiene | No chasing, closed candles only, no repeats, defined invalidation | Setup state machine (section 4). |

## 2. Objective definitions

**Swing high / low.** A pivot with *N* lower highs (or higher lows) on **both** sides. It is known only *N* candles after it forms. Swing length is set separately for Daily, H4, H1 and LTF.

**Break of structure (BOS).** A candle **close** beyond the latest *unbroken* confirmed swing high or low. Each swing can only be broken once. A wick beyond it is not a break.

**Bias.** With the 2-break rule: Bullish = the last two breaks were both up; Bearish = both down; otherwise Neutral. This includes "no breaks yet", which happens during warm-up.

**ATR.** ATR(14) of the relevant timeframe. Zone sizes use the zone timeframe's ATR. Distances to zones use the **last closed H1 ATR**. LTF thresholds use that LTF's ATR. ATR keeps the settings meaningful as gold volatility changes.

**Base.** 1 to *Base max* (default 3) consecutive candles immediately before an impulse or breakout candle. Each base candle has a **body ≤ 50% of its range** *or* a **range ≤ 0.5 × ATR**.

**Support / resistance zone (H4, H1).** Made from a confirmed swing candle. The zone runs from the swing's wick extreme to its body edge. Height is clamped between *Min* (0.10 × ATR) and *Max* (1.0 × ATR).

**Demand / supply zone (H4, H1).** An impulse candle has a body ≥ 1.0 × ATR, and that body is ≥ 60% of its range. When it closes beyond the base high (demand) or base low (supply), a zone is created:
- **Demand:** from the base's lowest low to its highest body edge.
- **Supply:** mirrored.

Zones taller than 1.5 × ATR are ignored. A new zone that overlaps an existing same-side zone on the same timeframe is skipped, to keep the chart clean. At most *N* zones are kept per side per timeframe; when the limit is exceeded, the oldest is removed.

**Zone breakout vs. sweep.** Both are judged on the zone's *own* timeframe candle:
- **Breakout:** the candle **closes** beyond the far edge. The zone flips once (S→R / R→S) if enabled, otherwise it is removed.
- **Sweep:** the candle wicks beyond and closes back inside. It is marked "sweep", and the zone stays valid.

**LTF breakout (category A).**
- **Breakout close:** an M30/M15/M5/M1 candle **closes** beyond the latest confirmed local swing high (buy) or low (sell), plus an optional ATR buffer.
- **Retest + reaction:** after the breakout candle, a retest area is defined from the broken level to the base's near body edge, ± 0.25 × ATR. Price must trade into that area, and then a candle must close in the trade direction and back beyond the broken level. The sequence fails if:
  - price closes beyond the base's far wick (with "Level only": 1 × ATR back through the level);
  - no reaction arrives within 20 bars;
  - a newer breakout replaces it.

**Chart patterns (category B).** Built from a zig-zag of confirmed, alternating swings.
- **Double Top:** swing H1 → L → H2.
  - The two tops must be within 0.5 × ATR of each other.
  - Both tops must stand at least 1.0 × ATR above the trough.
  - The pattern must span ≤ 60 bars.
  - Neckline = the trough. Double Bottom is mirrored.
- **Head & Shoulders:** swings LS → N1 → Head → N2 → RS.
  - The head must be beyond both shoulders by at least 0.3 × ATR.
  - The shoulders must be within 0.5 × ATR of each other.
  - The shoulders must clear the neckline by at least 0.5 × the minimum height.
  - The pattern must span ≤ 60 bars.
  - Neckline = the line through N1 and N2, so it may slope. Inverse H&S is mirrored.
- **Developing:** the pattern's last swing (H2 or RS) is confirmed and the neckline is unbroken. The dashed drawing and the "DT M15 ?" label appear at that point.
- **Confirmed (neckline close):** a candle **closes** beyond the neckline.
- **Confirmed (neckline retest):** after that close, price returns to within 0.25 × ATR of the neckline, and a candle closes away from it in the pattern direction.
- **Invalid:** a close beyond the pattern extreme (top, bottom or head); a newer top/bottom replaces the pattern; or no break or retest arrives in time.

**Price action (category C, OFF by default; proposal for your approval).**
- **Bullish engulfing:**
  - a bullish candle after a bearish one;
  - its body covers the previous body, and is ≥ 1.0 × that body;
  - its body is ≥ 50% of its range;
  - its range is ≥ 0.3 × ATR.
- **Bullish rejection:**
  - the lower wick is ≥ 2 × the body;
  - the lower wick is ≥ 50% of the range;
  - the range is ≥ 0.3 × ATR.
- Bearish versions are mirrored.
- **When the filter is on:** a breakout or pattern confirmation on a timeframe also needs one of these candles on *that same timeframe* within the last 3 bars. That candle's wick must have reached within the max distance of the armed zone.

## 3. Signal flow

**Buy:** Bullish alignment (D/H4, plus H1 if required) → price touches an eligible support or demand zone → any enabled LTF confirms → **BUY**.

The confirmation is either a bullish breakout (close or retest) or a bullish pattern (Double Bottom or inverse H&S). The confirmation candle must close within the max distance (default 1 × H1 ATR) of the zone.

**Sell** is the mirror image.

## 4. Setup lifecycle (per side)

| State | Enter when | Leave when |
|---|---|---|
| **Idle** | start / after reset | a closed chart candle touches an eligible zone (± touch tolerance) while bias is aligned → **Armed** |
| **Armed** (label "buy setup · H4 Demand") | zone touched | any enabled LTF confirms → **signal** → Consumed. Resets to Idle if: the armed zone breaks on its own TF; alignment is lost; price closes more than the max distance away without confirming (no chasing); or no new touch for the expiry time (24 h) |
| **Consumed** | after a signal | resets to Idle once price leaves (beyond max distance), the zone breaks, or alignment is lost. Touching a **different** zone re-arms immediately. |

There is one signal per setup. Re-touching the same zone without first leaving it does not produce another signal.

## 5. Timing, repainting and confirmation delays

- **Closed candles only.** Each timeframe is requested as `expr[1]` with `lookahead_on`, which returns the last closed candle and never the forming one. The chart's own candle is read as `[1]`.
  - A signal is evaluated on the first tick after the confirmation candle closes, and is labelled on that closed candle.
  - Alerts fire at that same moment (`once per bar`).
  - Nothing changes in hindsight.
- **Swing delay.** A swing is usable only *N* bars after it forms, because *N* bars on the right are required. With defaults:

  | Timeframe | Swing length | Delay |
  |---|---|---|
  | Daily | 2 | 2 days |
  | H4 | 3 | 12 h |
  | H1 | 3 | 3 h |
  | LTF | 3 | 3 bars |

  The consequences:
  - BOS, bias and S/R zones always lag the actual swing by that amount.
  - A pattern can only become *developing* when its last swing is confirmed. If price had already broken the neckline by then, the pattern confirms on that same bar (late, never back-dated). The no-chase filter then decides whether it still qualifies.
  - Pattern drawings connect the historical swing points (that is geometry, not a signal). The label and signal sit on the bar where confirmation actually became known.
- **Higher-timeframe values** update only when that candle closes. For example, the H4 bias changes on the first chart bar after the H4 close.
- **Lower timeframes.** A confirmation TF below the chart TF is disabled (N/A), not approximated. Requesting a lower TF from a higher chart only returns the last intrabar, which would be wrong.

## 6. Settings reference

**1 · Direction:** Daily / H4 / H1 swing length · structure breaks needed for bias (1 or 2) · Daily/H4 alignment (Relaxed / Strict) · H1 alignment (display / not opposite / must agree) · H4 BOS markers.

**2 · Key zones:** show H4 / H1 zones · zones that can arm a setup · S/R on/off · S/D on/off · flip broken zones · max zones per side · min/max zone height · impulse body (× ATR and % of range) · base definition (max candles, body %, range × ATR) · breakout/sweep markers · engulfing/rejection markers.

**3 · Setup rules:** touch tolerance · max distance from zone (no-chase) · expiry hours · armed-setup labels.

**4 · Confirmation timeframes:** M30 / M15 / M5 / M1 toggles · LTF swing length.

**4A · Breakout:** on/off · entry mode (close / retest + reaction / either) · close buffer · retest area (level + base / level only) · retest tolerance · retest window · level-only failure distance.

**4B · Chart patterns:** on/off · confirmation (neckline close / retest / either) · similarity tolerance · min height · head prominence · max length · show developing · keep confirmed drawings (signals only / all / none).

**4C · Price-action filter:** off by default · lookback bars · engulfing ratio and min body % · rejection wick/body ratio and wick % of range · min candle range.

**5 · Display:** BUY/SELL labels · dashboard on/off, position and text size · colours.

**6 · Alerts:** BUY · SELL · setup armed · developing pattern.

## 7. Chart legend

| What you see | Meaning |
|---|---|
| Solid box "H4 Demand" / dashed box "H1 Resistance" | Active zone. Green = buy side, red = sell side. "flip" = a broken zone that changed role |
| "H4 BO▲", "H1 sweep" (grey, tiny) | Zone breakout (close) / wick sweep on that timeframe |
| "H4 Eng▲", "H1 Rej▼" (grey, tiny) | Engulfing / rejection candle at a zone (information only) |
| "buy setup · H4 Demand" | Setup armed (developing), waiting for LTF confirmation |
| Dashed polyline + "DB M15 ?" | Developing pattern with its neckline. "✓" = neckline confirmed |
| **BUY / SELL** label | Confirmed entry, listing every timeframe and type that confirmed |
| Dotted line "M5 BO" | The local level whose break confirmed the signal |

The dashboard shows Daily, H4 and the D/H4 alignment (Aligned / MIXED / Not aligned), H1 and its relation, the current setup state, each LTF's status and last event, and the last signal.

## 8. Limitations

- **Not discretionary trading.** These are fixed rules. Context such as news, session behaviour, "quality" of a zone and confluence you read by eye is not captured. Use the signals as prompts to look, not as instructions.
- **History depth.** On an M1 chart TradingView loads a limited number of bars. Daily and H4 structure may then have few swings and can show "Neutral" during warm-up. If Daily looks too empty, use M5.
- **Zone rules are simplified.** There is no zone-strength scoring, no tracking of first vs. repeated tests, and overlapping same-side zones are skipped rather than merged.
- **Pattern detection** uses only the most recent swings. A swing length that is too small finds noisy patterns; one that is too large adds delay.
- **The breakout level is the latest local swing**, not necessarily the most significant one.
- **Broker feeds differ.** Daily candle boundaries and session gaps vary between XAUUSD feeds, which changes swings and zones slightly.
- **TradingView limits** cap how many drawings are kept on screen; older ones are removed.
- **Not yet compiled in TradingView.** The script was written for Pine v6 and checked structurally, but it has not been compiled in the Pine Editor from this environment. If the editor reports an error, send me the line and message.
