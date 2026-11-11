# SMC HTF Zones + M5 CHoCH Entry (TradingView indicator)

`smc-htf-zones-m5-entry.pine` is a Pine Script v6 indicator for TradingView.

## Install

1. TradingView → open a chart → **Pine Editor** (bottom panel).
2. Paste the whole contents of `smc-htf-zones-m5-entry.pine`, click **Save**, then **Add to chart**.
3. Use an **M5 chart** (M1 also works). On charts higher than M5 the M5 events cannot all be shown, and the dashboard
   says so.

## What it shows

| # | Feature | On the chart |
|---|---|---|
| 1 | SMC concept | Structure (BOS / CHoCH), order blocks (last opposite candle before the move that broke structure) and fair value gaps, worked out on H4, H1 and M5 |
| 2 | FVG near OB, **H1 and H4 only** | `H4 FVG ★` + `H4 Bull/Bear OB`, `H1 FVG ★` + `H1 Bull/Bear OB`. An FVG is shown only when it touches or sits within 0.5 × ATR of an order block in the same direction. H4 zones are shaded strongest. A zone is removed when price closes through it |
| 3 | M5 BOS | Solid line + `M5 BOS` label |
| 4 | M5 FVG near OB | `M5 FVG ★` + `M5 Bull/Bear OB` (lightest shading) |
| 5 | Entry on M5 CHoCH | `BUY @ price` / `SELL @ price` label naming the zone it came from (e.g. `H4 zone · M5 CHoCH`). **A+** = also with the H4 + H1 trend. The entry, stop loss (the M5 swing low / high) and a 2R take profit are drawn |

The dashboard shows the H4 and H1 trend, the trade direction, M5 structure, whether an H1/H4 zone was just tapped,
and the last entry.

## Signals at CMP (current market price)

**Signal timing** is `Live at CMP` by default. The dotted **BUY trigger** and **SELL trigger** lines on the last bar
mark the M5 levels that would flip structure (CHoCH). The signal fires as soon as the live price crosses one of them,
and the entry is the price at that moment. Switch to `M5 candle close` to wait for the M5 candle to close beyond the
level instead (fewer false breaks, later entry).

Because live signals fire inside the candle, a break can still fail if price closes back. On past bars the indicator
shows where the level was crossed (entry at the level).

## NOW call at CMP

On the latest bar a box sits next to the current price and says what the indicator sees **right now**:

| Box | Meaning |
|---|---|
| `BUY NOW @ CMP` / `SELL NOW @ CMP` | H4 + H1 agree, M5 structure already turned the same way, price reacted from an H1/H4 zone of that direction in the last 30 bars, and the stop fits the max stop size. Shows entry (current price), SL (M5 swing low / high) and TP (2R), with dashed SL / TP lines |
| `BUY OPEN` / `SELL OPEN` | The last signal is still running (neither SL nor TP hit). Shows the result so far in R |
| `WAIT · BUY above X` / `WAIT · SELL below X` | Trend is set but M5 has not flipped yet. X is the price that would trigger the entry |
| `WAIT · BUY bias` / `WAIT · SELL bias` | Trend is set; wait for price to come back to an H1/H4 zone |
| `NO TRADE` | H4 and H1 disagree |

The same text is in the dashboard (`NOW (CMP)`), and the alerts `NOW: BUY at CMP` / `NOW: SELL at CMP` fire when the
box turns to BUY NOW / SELL NOW. The box updates with every tick.

## How an entry is chosen (precise mode)

With **Show entries = Zone reaction + trend (A+ only)** (the default) a BUY needs all of these:

1. Price reacts from a bullish **H1 or H4** FVG + OB zone: the M5 swing low that the move starts from sits inside the
   zone (within 0.25 × M5 ATR).
2. Price then breaks the M5 CHoCH level by at least 0.1 × M5 ATR (no one-tick touches).
3. The stop (that M5 swing low) is no wider than 3 × M5 ATR.
4. **Each zone gives one signal only**, each CHoCH level fires once, and same-side signals are at least 10 bars apart.
5. H4 and H1 trend are both bullish.

SELL is the mirror image. `Zone reaction` drops rule 5 (more signals, also counter-trend). `Every M5 CHoCH` drops
the zone rule too (many more signals).

## Focus on recent prices

Only the last **300 bars** get zones, structure lines and signals (*Draw only the last*), and H1/H4/M5 zones more than
**1 %** away from the current price are hidden (*Hide zones further than*). Each timeframe keeps at most 3 zones.

## Settings worth knowing

- **Show entries**: `Zone reaction + trend (A+ only)` (default), `Zone reaction`, or `Every M5 CHoCH`.
- **Zone tolerance**, **Break buffer**, **Max stop size**, **Min bars between signals**: tighten or loosen the entry
  rules above.
- **Max distance FVG ↔ OB**: 0 means the FVG must touch the OB. Raise it to see more zones.
- **Take profit (R multiple)**: default 2R.

## Alerts

BUY / SELL entry, BUY / SELL A+, M5 BOS, new H1/H4 zone, and price tapping a bullish / bearish H1/H4 zone. Or pick
**Any alert() function call** to get the detailed entry message with price and stop. For live CMP signals set the
alert to *Once per bar*; for `M5 candle close` timing use *Once per bar close*.

## Notes

- H4, H1 and M5 zones and trends come from the last **closed** candle of that timeframe, so they do not repaint.
- For education only. This is not financial advice. Backtest and forward-test before you trade with real money.
