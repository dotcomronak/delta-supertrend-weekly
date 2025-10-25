"""delta exchange weekly SuperTrend scanner
df[["open", "high", "low", "close", "volume"]] = df[["open", "high", "low", "close", "volume"]].astype(float)
return df




def compute_supertrend(df, period=ATR_PERIOD, multiplier=ATR_MULTIPLIER):
"""Compute SuperTrend columns and return a DataFrame with `supertrend` column."""
df = df.copy().reset_index(drop=True)
atr = ta.volatility.AverageTrueRange(high=df["high"], low=df["low"], close=df["close"], window=period).average_true_range()


hl2 = (df["high"] + df["low"]) / 2.0
basic_ub = hl2 + multiplier * atr
basic_lb = hl2 - multiplier * atr


final_ub = basic_ub.copy()
final_lb = basic_lb.copy()


for i in range(1, len(df)):
if df["close"].iloc[i - 1] <= final_ub.iloc[i - 1]:
final_ub.iloc[i] = min(basic_ub.iloc[i], final_ub.iloc[i - 1])
else:
final_ub.iloc[i] = basic_ub.iloc[i]


if df["close"].iloc[i - 1] >= final_lb.iloc[i - 1]:
final_lb.iloc[i] = max(basic_lb.iloc[i], final_lb.iloc[i - 1])
else:
final_lb.iloc[i] = basic_lb.iloc[i]


# build supertrend
supertrend = pd.Series(index=df.index, dtype=float)
supertrend.iloc[0] = final_lb.iloc[0]


for i in range(1, len(df)):
if df["close"].iloc[i] > final_ub.iloc[i - 1]:
supertrend.iloc[i] = final_lb.iloc[i]
elif df["close"].iloc[i] < final_lb.iloc[i - 1]:
supertrend.iloc[i] = final_ub.iloc[i]
else:
supertrend.iloc[i] = supertrend.iloc[i - 1]


df["final_ub"] = final_ub
df["final_lb"] = final_lb
df["supertrend"] = supertrend
return df




def main():
products = get_products()
breakeven = []
breakthrough = []


for p in products:
symbol = p.get("symbol")
try:
df = get_candles(symbol)
except Exception:
continue
if df is None or len(df) < ATR_PERIOD + 2:
continue


df = compute_supertrend(df)


prev_close = df["close"].iloc[-2]
prev_st = df["supertrend"].iloc[-2]
last_close = df["close"].iloc[-1]
last_st = df["supertrend"].iloc[-1]


# Breakeven: crossed below ST
if prev_close > prev_st and last_close < last_st:
breakeven.append(symbol)


# Breakthrough: crossed above ST
if prev_close < prev_st and last_close > last_st:
breakthrough.append(symbol)


print("\n=== Results (Weekly SuperTrend 10,3) ===")
print("Breakeven coins (crossed below ST):", breakeven)
print("Breakthrough coins (crossed above ST):", breakthrough)




if __name__ == "__main__":
main()
