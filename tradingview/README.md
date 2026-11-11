# 1PC Headline & Storyline Indicator (TradingView)

`1pc-headline-storyline.pine` (Pine Script v6). The **headline** is the H4 key zone; the **storyline** is what price does when it comes back to it. Three steps:

1. **Key zones (rectangles), H4 only.** An SNR swing level is only marked when price left it with a DBD or RBR:
   - **SNR + DBD → red (resistance / sell zone):** swing high → first drop (≥ 2 × H4 ATR) → base
     (price bounces but stays below the high and retraces at most 80% of the drop) → second drop (an H4 close below the base low).
     The zone is drawn at the swing high, from the wick to the candle body, and is at least 1 × ATR tall.
   - **SNR + RBR → blue (support / buy zone):** the mirror image, drawn at the swing low.
   - **Breakout → grey:** when an H4 candle closes through a zone, the zone turns grey and switches role
     (broken resistance becomes support, broken support becomes resistance). It becomes fresh again, so its first retest can give an entry.
     If price closes back through a grey zone, the zone is removed.
2. **Confirmation on M15 or M30, fresh zones only.** On price's **first approach** to a zone, the indicator watches for one of two patterns:
   - **M (double top)** in a red or grey sell zone. The second top can be lower than the first, but must climb back at least 50% of the dip.
   - **W (double bottom)** in a blue or grey buy zone.

   Both tops or bottoms must be inside the zone. The low between the two tops of an M (the high between the two bottoms of a W) is the **neckline**.
   - **PREPARE** signal: a candle closes through the neckline. Place a limit order at the neckline, with SL and TP shown.
   - **ENTRY** signal: price comes back to retest the neckline. That's your fill. The zone then turns **✓ VALID** and gives no more signals.
   - If the pattern fails (price closes beyond the tops or bottoms, or nothing happens in time), the zone stays **IN PLAY** for the next pattern.
     When price moves 1 × H4 ATR away from the zone without an entry, the zone becomes **TESTED** and is ignored.
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
| Min first drop / rally | 2 × H4 ATR | Size of the first leg away from the swing level. |
| Max base bounce | 0.8 | Fraction of the first leg the base may retrace. |
| H4 swing strength | 3 | Bars on each side for an H4 swing high or low. |
| Min zone height | 1 × H4 ATR | Lower it for thinner zones. |
| Fresh zone: approach ends | 1 × H4 ATR | How far price must move away from a zone before its first approach is over. |
| Entry | Neckline retest | **Neckline break** enters on the close through the neckline; **Second top** enters as soon as the pattern forms. |
| Retest within | 16 bars | After the break, price must retest the neckline within this many candles. |
| Only show zones from the last | 30 days | Keeps only the nearest zones on the left. |
| Max zones per type | 3 | At most 3 red and 3 blue zones; the newest are kept. |
| Pattern pivot left / right bars | 3 / 2 | A top is confirmed `right bars` candles after it forms (no repainting). |
| 2nd top may be higher by | 0.5 × ATR | The second top can be lower than the first, or higher by at most this. |
| 2nd top must climb back | 50% | Share of the dip to the neckline the second top must climb back. |
| Zone touch tolerance | 0.25 × ATR | Allows wicks that poke slightly outside a zone. |
| One trade at a time | on | Skips new signals while a trade is still open. |

D1 and H4 levels only use closed candles (`lookahead_on` with a `[1]` offset), so the zones don't repaint.
