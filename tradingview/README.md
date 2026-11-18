# 1PC Headline & Storyline Indicator (TradingView)

`1pc-headline-storyline.pine` (Pine Script v6). The **headline** is the fresh H4 / H1 / M30 supply & demand zone; the **storyline** is what price does when it comes back to it.

1. **Fresh key zones (rectangles) on H4, H1 and M30** (H4 solid border, H1 dashed, M30 dotted), labelled in the middle of the box:
   - **H4 / H1 / M30 SNR (DBD)**, red supply: a swing high that price left with drop → base → second drop.
     **SNR (RBR)**, blue demand: a swing low that price left with rally → base → second rally.
     The zone runs from the swing wick to the candle body and is at least 1 × ATR tall. The first leg must be ≥ 2 × ATR and the base may retrace at most 80% of it.
   - **H4 / H1 / M30 base (DBD / RBR)**, grey: the base itself, the sideways part between the two drops or rallies (red label for DBD, blue for RBR).
     On M30, the drop into the base is measured from the highest high of the last 20 candles, and the second drop needs a candle body of at least 0.5 × ATR.
   - **H4 / H1 / M30 breakout**: a swing high or low that a candle of its timeframe has closed through (or any zone that got broken).
     It's coloured by its new role (red = now resistance, blue = now support) and has a dashed midline. It's fresh again until its retest.
     If price closes back through a breakout zone, the zone is removed.
   - **Plain SNR levels**: every H4 / H1 / M30 swing high (*resistance*, red) and swing low (*support*, blue) that price reacted from by at least 1 × ATR (*SNR level: min reaction*).
     When a DBD / RBR forms from the same swing, the SND zone replaces the plain level.
   - **Every timeframe is drawn**: H4, H1 and M30 zones all show, even where they overlap. Labels sit in the middle (H4), on the right (H1) or on the left (M30) of the box.
     Only duplicates (same kind, same timeframe) are merged. Turn on *Hide lower-TF zones under higher-TF zones* for a cleaner chart.
   - **Recent and fresh only:** zones from the last 4 trading days that price hasn't tested yet. All of them are shown by default; set *Nearest zones to current price, per timeframe* to 1 or 2 to keep only the closest ones.
   - **Fresh only:** a zone is removed once price has come back to it and then moved 1 × ATR away again
     (or once it gave its entry and price moved away). A grey breakout zone is fresh again until its retest.
     Turn off *Only fresh zones* to keep tested zones on the chart (faded).
2. **Entry on M1, M5, M15 or M30, fresh zones only.** When price reaches a fresh zone for the first time, the indicator works out an exact limit price inside the zone. Choose the method under **Entry method**:
   - **Smart zone entry**: the indicator follows the extreme that price makes inside the zone.
     When a candle closes back through the candle that made the extreme (below its low for a sell, above its high for a buy), the rejection is confirmed.
     The limit price is placed at 50% of that rejection move, kept inside the zone (*Smart entry: retracement*).
     It comes with a **score from 0 to 100**, which adds up:
     - the zone's timeframe and type;
     - the rejection wick;
     - the size of the rejection candle;
     - first touch;
     - another timeframe's zone in the same place.
   - **M / W pattern**: a double top in a sell zone or a double bottom in a buy zone.
     The neckline break gives the limit price at the neckline, and the retest fills it.
   - Default: both.
   - **PREPARE** alert: the limit price is known, for example `SELL LIMIT 3792.40 · score 78`. Place the order then.
     **ENTRY** alert: the limit is filled. The zone then turns ✓ valid and gives no more signals.
   - If the zone breaks or nothing happens in time, the setup is cancelled.
     When price moves 1 × ATR away from the zone without an entry, the zone counts as tested and is removed.
   - Under **Entry**, choose **Neckline break** to enter on the break itself, or **Second top** to enter as soon as an M / W forms.
3. **Risk**: the indicator draws **600-point SL** and **1000-point TP** boxes from the entry price,
   marks each trade "TP ✓" or "SL ✗" when one is hit, and shows wins, losses and win rate in a table.
4. **AI second opinion (optional):** with **Send alerts as JSON for the AI service** turned on and a webhook to the [1PC AI signal service](ai-signal-service/README.md),
   Claude reviews every PREPARE setup. It sends back take / wait / skip with its own exact entry price inside the zone, shown on the service's page (and Telegram if set up).

## Live signal at current price

At the right edge of the chart, next to the price, a line and label always show what to do now. It updates on every tick:
- **IN TRADE SELL @ …**: the trade you're in, with SL, TP and the points so far.
- **ACTIVE SELL LIMIT …**: a limit order is waiting for its fill (smart entry or M / W), with SL, TP and score.
- **SELL LIMIT … / BUY LIMIT …**: otherwise, the plan at the nearest zone above price (sell) and below (buy).
  It shows the exact price (*Live plan entry price*: the zone's 50% or its near edge), SL, TP and how far away it is.
  It says **SELL NOW / BUY NOW** when price is already there.
  Once price reacts inside the zone, the smart entry replaces the plan with the exact rejection-based price.

Old signals are removed from the chart when a new one starts. Turn on **Keep past signals on the chart** to see the history.

## Install

1. In TradingView, open **Pine Editor** (bottom panel), then **New → Indicator**.
2. Delete the template code, paste in the full contents of `1pc-headline-storyline.pine`, and click **Add to chart**.
3. Use the chart timeframe you trade:
   - **M1, M5, M15 or M30:** H4, H1 and M30 zones, plus signals.
   - **H1:** H4 and H1 zones only.
   - **H4:** H4 zones only. Signals need a chart of 30m or lower.

## Alerts

Create Alert → Condition: **1PC H&S** → **Any alert() function call**. That sends both messages, each with zone, price, SL and TP:
- `1PC PREPARE SELL XAUUSD (smart zone entry in M30 base (DBD) zone · score 78) | SELL LIMIT 3792.40 | SL 3798.40 | TP 3782.40`
- `1PC ENTRY SELL XAUUSD (smart zone entry in M30 base (DBD) zone) | Entry 3792.40 | SL 3798.40 | TP 3782.40`

For the AI service, turn on **Send alerts as JSON for the AI service** and add the service's webhook URL to the alert (see [ai-signal-service/README.md](ai-signal-service/README.md)).

There are also separate conditions: **1PC Prepare Buy / Sell** and **1PC Entry Buy / Sell**.

## Settings worth knowing

| Setting | Default | Notes |
|---|---|---|
| Point size override | 0 (= auto) | Gold (XAU / GOLD): 1 point = 0.01, so 600 points = $6 and 1000 points = $10 (sell at 3783 → SL 3789, TP 3773), even when the feed quotes 3 decimals. Other symbols: 1 point = the smallest price step (EURUSD 0.00001: 600 points = 60 pips). |
| H4 / H1 / M30 zones | on / on / on | Turn any timeframe off. M30 zones need a 15m or 30m chart, H1 zones a chart of 1h or lower. |
| Only fresh zones | on | Removes a zone once it has been tested. |
| Min first drop / rally | 2 × ATR | Size of the first leg away from the swing level. |
| Max base bounce | 0.8 | Fraction of the first leg the base may retrace. |
| Swing strength | 3 | Bars on each side for a swing high or low (H4 or H1 candles). |
| Min zone height | 1 × ATR | Lower it for thinner zones. |
| Fresh zone: approach ends | 1 × ATR | How far price must move away from a zone before its first approach is over. |
| Entry | Neckline retest | **Neckline break** enters on the close through the neckline; **Second top** enters as soon as the pattern forms. |
| Retest within | 16 bars | After the break, price must retest the neckline within this many candles. |
| Only show zones from the last | 4 trading days | A zone is removed once its swing is older than this (weekends don't count). |
| Max zones per type and TF | 3 | At most 3 red and 3 blue zones on each of H4, H1 and M30; the newest are kept. |
| Pattern pivot left / right bars | 3 / 2 | A top is confirmed `right bars` candles after it forms (no repainting). |
| 2nd top may be higher by | 0.5 × ATR | The second top can be lower than the first, or higher by at most this. |
| 2nd top must climb back | 50% | Share of the dip to the neckline the second top must climb back. |
| Zone touch tolerance | 0.25 × ATR | Allows wicks that poke slightly outside a zone. |
| One trade at a time | on | Skips new signals while a trade is still open. |

D1 and H4 levels only use closed candles (`lookahead_on` with a `[1]` offset), so the zones don't repaint.
