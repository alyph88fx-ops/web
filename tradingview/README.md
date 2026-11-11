# KZ Pattern Entry — TradingView indicator

`kz-pattern-entry.pine` (Pine Script v6). Three steps:

1. **Key zones (rectangles) from D1 and H4**
   - **SNR**: swing-high resistance (red) and swing-low support (blue). Each zone runs from the wick to the candle body.
   - **DBD**: drop-base-drop supply (red). **RBR**: rally-base-rally demand (blue). Each zone covers the base candles.
   - **Breakout (grey)**: when a D1/H4 candle closes through a zone, the zone turns grey and switches role
     (broken resistance becomes support, broken support becomes resistance). If price closes back through a grey zone, the zone is removed.
2. **Confirmation on M30**: a **double top** with both peaks inside a red (sell) zone gives **SELL**.
   A **double bottom** with both lows inside a blue (buy) zone gives **BUY**. Grey zones also count, in their new role.
   Patterns are only scanned when the chart is on **30m**.
3. **Risk**: the indicator draws **600-point SL** and **1000-point TP** boxes from the entry (the signal candle's close),
   marks each trade "TP ✓" or "SL ✗" when one is hit, and shows wins, losses and win rate in a table.

## Install

1. In TradingView, open **Pine Editor** (bottom panel), then **New → Indicator**.
2. Delete the template code, paste in the full contents of `kz-pattern-entry.pine`, and click **Add to chart**.
3. Switch the chart to **30m**.

## Alerts

Create Alert → Condition: **KZ-DTB** → choose **KZ Buy**, **KZ Sell**, or **Any alert() function call**.
The last option sends the full message: side, zone, entry, SL and TP.

## Settings worth knowing

| Setting | Default | Notes |
|---|---|---|
| Point size override | 0 (= symbol min tick) | 600 points = 600 × min tick. Examples: EURUSD (0.00001) gives 60 pips; XAUUSD (0.01) gives $6.00. Set it here if your broker's point is different. |
| Signal trigger | Second peak confirmed | Choose **Neckline break** for a stricter signal, which waits for a close through the neckline. |
| SNR swing strength | 5 | A higher value gives fewer, stronger D1/H4 levels. |
| Max zones per timeframe | 8 | Older zones are removed after this. |
| Pattern pivot left / right bars | 5 / 3 | Signals appear `right bars` candles after the second peak (they don't repaint). |
| Peak equality tolerance | 0.5 × ATR | Sets how close the two tops/bottoms must be. |
| Zone touch tolerance | 0.25 × ATR | Allows wicks that poke slightly outside a zone. |
| One trade at a time | on | Skips new signals while a trade is still open. |

D1 and H4 levels only use closed candles (`lookahead_on` with a `[1]` offset), so the zones don't repaint.
