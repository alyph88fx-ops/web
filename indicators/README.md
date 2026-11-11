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
| 5 | Entry on M5 CHoCH | Dashed line + `M5 CHoCH`, then a `BUY` / `SELL` label. **A+** = the CHoCH came after price tapped an H1/H4 zone of the same direction *and* H4 + H1 trend agree. The entry, stop loss (the M5 order block extreme) and a 2R take profit are drawn |

The dashboard shows the H4 and H1 trend, the trade direction, M5 structure, whether an H1/H4 zone was just tapped,
and the last entry.

## Settings worth knowing

- **Show entries**: `Every M5 CHoCH` (default), `After H1/H4 zone tap`, `With H4 & H1 trend`, or `Zone tap + trend`
  (A+ only).
- **Max distance FVG ↔ OB**: 0 means the FVG must touch the OB. Raise it to see more zones.
- **Take profit (R multiple)**: default 2R.

## Alerts

BUY / SELL entry, BUY / SELL A+, M5 BOS, new H1/H4 zone, and price tapping a bullish / bearish H1/H4 zone. Or pick
**Any alert() function call** to get the detailed entry message. Use *Once per bar close*.

## Notes

- H4, H1 and M5 values come from the last **closed** candle of that timeframe, so nothing repaints. Signals appear when
  the M5 candle closes.
- For education only. This is not financial advice. Backtest and forward-test before you trade with real money.
