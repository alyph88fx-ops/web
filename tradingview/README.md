# 1PC Headline & Storyline Indicator (TradingView)

`1pc-headline-storyline.pine` (Pine Script v6). The **headline** is the fresh H4 / H1 / M30 supply & demand zone; the **storyline** is what price does when it comes back to it. Three steps:

1. **Fresh key zones (rectangles) on H4, H1 and M30** (H4 solid border, H1 dashed, M30 dotted), labelled in the middle of the box:
   - **H4 / H1 / M30 SNR (DBD)**, red supply: a swing high that price left with drop → base → second drop.
     **SNR (RBR)**, blue demand: a swing low that price left with rally → base → second rally.
     The zone runs from the swing wick to the candle body and is at least 1 × ATR tall. The first leg must be ≥ 2 × ATR and the base may retrace at most 80% of it.
   - **M30 / H1 base (DBD / RBR)**, grey: the base itself, the sideways part between the two drops or rallies (red label for DBD, blue for RBR).
     On M30, the drop into the base is measured from the highest high of the last 20 candles, and the second drop needs a candle body of at least 0.5 × ATR.
   - **H4 / H1 breakout**: a swing high or low that a candle of its timeframe has closed through (or any zone that got broken).
     It's coloured by its new role (red = now resistance, blue = now support) and has a dashed midline. It's fresh again until its retest.
     If price closes back through a breakout zone, the zone is removed.
   - **Near current price:** only the 2 zones nearest above price and the 2 nearest below are shown (plus a zone price is inside), so the chart shows what matters on the right edge. Change it with *Show only the nearest zones to current price*; 0 shows all.
   - **Fresh only:** a zone is removed once price has come back to it and then moved 1 × ATR away again
     (or once it gave its entry and price moved away). A grey breakout zone is fresh again until its retest.
     Turn off *Only fresh zones* to keep tested zones on the chart (faded).
   - **Overlaps:** the higher timeframe wins (H4 > H1 > M30), then breakout > SNR > base. Zones overlap when they share at least 30% of their height.
2. **Confirmation on M15 or M30, fresh zones only.** On price's **first approach** to a zone, the indicator watches for one of two patterns:
   - **M (double top)** in a red or grey sell zone. The second top can be lower than the first, but must climb back at least 50% of the dip.
   - **W (double bottom)** in a blue or grey buy zone.

   Both tops or bottoms must be inside the zone. The low between the two tops of an M (the high between the two bottoms of a W) is the **neckline**.
   - **PREPARE** signal: a candle closes through the neckline. Place a limit order at the neckline, with SL and TP shown.
   - **ENTRY** signal: price comes back to retest the neckline. That's your fill. The zone then turns **✓ VALID** and gives no more signals.
   - If the pattern fails (price closes beyond the tops or bottoms, or nothing happens in time), the zone stays **IN PLAY** for the next pattern.
     When price moves 1 × ATR away from the zone without an entry, the zone becomes **TESTED** and is ignored.
   - Under **Entry**, choose **Neckline break** to enter on the break itself, or **Second top** to enter as soon as the pattern forms.
3. **Risk**: the indicator draws **600-point SL** and **1000-point TP** boxes from the entry (the signal candle's close),
   marks each trade "TP ✓" or "SL ✗" when one is hit, and shows wins, losses and win rate in a table.

## Install

1. In TradingView, open **Pine Editor** (bottom panel), then **New → Indicator**.
2. Delete the template code, paste in the full contents of `1pc-headline-storyline.pine`, and click **Add to chart**.
3. Switch the chart to **15m** or **30m**.

## Alerts

Create Alert → Condition: **1PC H&S** → **Any alert() function call**. That sends both messages, each with zone, price, SL and TP:
- `1PC PREPARE SELL XAUUSD (M / double top in H4 SNR · RBR · BRK zone, neckline broken) | SELL LIMIT 4055.00 | SL 4061.00 | TP 4045.00`
- `1PC ENTRY SELL XAUUSD (...) | Entry 4055.00 | SL 4061.00 | TP 4045.00`

There are also separate conditions: **1PC Prepare Buy / Sell** and **1PC Entry Buy / Sell**.

## Settings worth knowing

| Setting | Default | Notes |
|---|---|---|
| Point size override | 0 (= symbol min tick) | 600 points = 600 × min tick. Examples: EURUSD (0.00001) gives 60 pips; XAUUSD (0.01) gives $6.00. Set it here if your broker's point is different. |
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
