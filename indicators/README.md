# SMC Liquidity MTF Pro (TradingView indicator)

`smc-liquidity-mtf.pine` is a Pine Script v6 indicator for TradingView.

## Install

1. TradingView → open any chart → **Pine Editor** (bottom panel).
2. Paste the whole contents of `smc-liquidity-mtf.pine`, click **Save**, then **Add to chart**.
3. For the signals, use an **M1 chart**. On higher charts the RSI is read from the M1 bars inside each candle.

## What it draws

| Feature | On the chart |
|---|---|
| Market structure | `BOS` (solid line) = trend continuation, `CHoCH` (dashed line) = change of character / reversal |
| Order blocks | `Bull OB` (green) / `Bear OB` (red). They are removed once price closes through them |
| FVG (high-potential only) | `FVG ★`: shown only when the gap overlaps or sits within *1 × ATR* of an order block in the same direction |
| IFVG | When price closes through a shown FVG it flips into `Bull IFVG` / `Bear IFVG` (cyan / magenta). It is removed if price closes back through it |
| Liquidity | `BSL` blue dashed lines above swing highs, `SSL` orange dashed lines below swing lows. `EQH` / `EQL` (thicker) = equal highs/lows. When price wicks through and closes back, the chart shows `BSL swept` / `SSL swept` |
| Buy / sell area | The current dealing range is split at `EQ 50%`: **SELL AREA · Premium** above, **BUY AREA · Discount** below. The side matching the H4/H1 direction is shaded stronger |
| M15 reversal | `M15↺` diamond when M15 structure flips (CHoCH) |
| Dashboard | H4 and H1 trend, the trade direction, M15 reversal, M5 confirmation, M1 RSI, price area and the last signal |

## Signals

1. **Raw hit** (small triangle): M1 RSI reaches **15 or lower** (buy) or **80 or higher** (sell).
   Turn on *Strict band* to count only 10–15 and 80–95.
2. **Setup** (faded label): the raw hit also passes the SMC filters:
   - direction: H4 and H1 both bullish for a buy, both bearish for a sell (changeable to H4 only or H1 only)
   - area: price is in the Discount area or inside a bullish OB/FVG for a buy, or in Premium or a bearish OB/FVG for a sell
3. **Confirmed** (solid `BUY ✔` / `SELL ✔` label): M5 structure is in the same direction, either at the setup or within
   the next 15 bars.

Every filter can be turned off in the settings. Alerts are available for confirmed and setup signals, raw RSI hits,
CHoCH, BOS, liquidity sweeps and M15 reversals. Use *Once per bar close* when creating them.

## Notes

- Higher-timeframe trends use the last **closed** H4/H1/M15/M5 candle, so they do not repaint.
- With *Signals on bar close only* on (the default), signals appear only when the candle closes.
- On charts above M1, the M1 RSI history is limited by TradingView's intrabar limit, so older bars show no signals.
- For education only. This is not financial advice. Backtest and forward-test before you trade with real money.
