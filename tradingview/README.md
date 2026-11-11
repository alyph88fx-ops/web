# KZ Pattern Entry — TradingView indicator

`kz-pattern-entry.pine` (Pine Script v6). Three steps:

1. **Key zones (rectangles), H4 only.** An SNR swing level is only marked when price left it with a DBD or RBR:
   - **SNR + DBD → red (resistance / sell zone):** swing high → first drop (≥ 2 × H4 ATR) → base
     (price bounces but stays below the high and retraces at most 70% of the drop) → second drop (an H4 close below the base low).
     The zone is drawn at the swing high, from the wick to the candle body, and is at least 1 × ATR tall.
   - **SNR + RBR → blue (support / buy zone):** the mirror image, drawn at the swing low.
   - **Breakout → grey:** when an H4 candle closes through a zone, the zone turns grey and switches role
     (broken resistance becomes support, broken support becomes resistance). It becomes fresh again, so its first retest can give an entry.
     If price closes back through a grey zone, the zone is removed.
2. **Confirmation on M30, fresh zones only.** Each zone has a status:
   - **FRESH:** price hasn't come back to the zone yet.
   - **IN PLAY:** price is on its first approach. The approach starts when price first reaches the zone, and ends when price moves 1 × H4 ATR away from it.
   - **✓ VALID:** a double top (red zone, **SELL**) or double bottom (blue zone, **BUY**) formed during that first approach,
     with both peaks inside the zone. This is the entry. The zone gets a bold border and gives no more signals.
   - **TESTED:** the first approach ended with no pattern. The zone fades with a dotted border and is ignored from then on.
   - Patterns are only scanned when the chart is on **30m**.
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
| Min first drop / rally | 2 × H4 ATR | Size of the first leg away from the swing level. |
| Max base bounce | 0.7 | Fraction of the first leg the base may retrace. |
| H4 swing strength | 3 | Bars on each side for an H4 swing high or low. |
| Min zone height | 1 × H4 ATR | Lower it for thinner zones. |
| Fresh zone: approach ends | 1 × H4 ATR | How far price must move away from a zone before its first approach is over. |
| Signal trigger | Second peak confirmed | Choose **Neckline break** for a stricter signal, which waits for a close through the neckline. |
| Max zones kept | 10 | Older zones are removed after this. |
| Pattern pivot left / right bars | 5 / 3 | Signals appear `right bars` candles after the second peak (they don't repaint). |
| Peak equality tolerance | 0.5 × ATR | Sets how close the two tops/bottoms must be. |
| Zone touch tolerance | 0.25 × ATR | Allows wicks that poke slightly outside a zone. |
| One trade at a time | on | Skips new signals while a trade is still open. |

D1 and H4 levels only use closed candles (`lookahead_on` with a `[1]` offset), so the zones don't repaint.
