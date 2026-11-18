# 1PC AI signal service (Claude second opinion)

When the **1PC Headline & Storyline** indicator sends a **PREPARE** alert (it has a limit price inside a zone), TradingView forwards the alert to this service.
The service asks Claude (`claude-opus-5-5`) to review the zone, the indicator's limit price and the last candles. Claude answers with:

- a decision: **take**, **wait** or **skip**;
- its own exact entry price inside the zone;
- an invalidation price, a confidence score and a short reason.

The stop loss and take profit always use your fixed points (600 / 1000 by default) from Claude's entry.
Results appear on the service's page, which works on a phone and refreshes every 20 s. If you set it up, they're also sent to Telegram.

TradingView can't receive messages back, so Claude's answer can't appear as a TradingView alert. The indicator's own PREPARE / ENTRY alerts still come through TradingView as usual.

## What you need

- A TradingView plan that supports **webhook alerts** (Essential or higher).
- An **Anthropic API key** from console.anthropic.com. Each review is one Claude request.
- Somewhere to run the service. The steps below use [Render](https://render.com); any host that runs Python works.

## Deploy on Render

1. In Render choose **New → Web Service**, connect GitHub and pick this repository (branch `claude/gracious-davinci-z4fg66`, or `main` once it's merged).
2. Fill in:
   - **Root directory:** `tradingview/ai-signal-service`
   - **Runtime:** Python
   - **Build command:** `pip install -r requirements.txt`
   - **Start command:** `uvicorn app:app --host 0.0.0.0 --port $PORT`
   - **Health check path:** `/health`
3. Under **Environment**, add:
   - `ANTHROPIC_API_KEY`: your key.
   - `WEBHOOK_TOKEN`: any long random secret, for example `1pc-` followed by 20 random letters. It protects the webhook and the page.
4. After the deploy, open `https://<your-service>.onrender.com/health`. It should show `{"ok":true,...}`.
5. Your page is `https://<your-service>.onrender.com/?token=<WEBHOOK_TOKEN>`. Bookmark it on your phone.

Free Render services fall asleep when idle, and the first alert after a pause can take up to a minute to arrive. A paid instance stays awake.

## Connect TradingView

1. In the indicator settings, open **4 · AI second opinion (webhook)** and turn on **Send alerts as JSON for the AI service**.
2. Create an alert:
   - **Condition:** **1PC H&S** → **Any alert() function call**.
   - **Notifications:** tick **Webhook URL** and enter `https://<your-service>.onrender.com/webhook?token=<WEBHOOK_TOKEN>`.
3. Keep your normal (non-JSON) alerts if you like. Add the indicator a second time with JSON turned off, and create its alert without a webhook.

## Optional: Telegram

Set `TELEGRAM_BOT_TOKEN` (from @BotFather) and `TELEGRAM_CHAT_ID` on the service. Each verdict is then also sent to that chat.

## Test without Claude

Set `DRY_RUN=1` to check that the TradingView webhook reaches the service. The page then shows a test verdict and Claude isn't called.

To run it locally:

```bash
pip install -r requirements.txt
```

```bash
WEBHOOK_TOKEN=test DRY_RUN=1 uvicorn app:app --port 8000
```

## Settings

| Variable | Default | Meaning |
|---|---|---|
| `CLAUDE_MODEL` | `claude-opus-5-5` | Claude model that reviews the setup |
| `CLAUDE_EFFORT` | `high` | `low`, `medium`, `high`, `xhigh` or `max`. Higher effort means a more thorough review, but it's slower and costs more. |
| `DATA_FILE` | `signals.jsonl` | Where the history is kept |

The service is decision support. Claude can be wrong, so always check the chart before placing an order.
