import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# ─────────────────────────────────────────
# STEP 1 — Download NSE Stock Data
# ─────────────────────────────────────────

tickers = ['RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS', 'ICICIBANK.NS']
data = yf.download(tickers, start='2023-01-01', end='2024-12-31')['Close']

print("Stock Data (first 5 rows):")
print(data.head())

# ─────────────────────────────────────────
# STEP 2 — Calculate Returns
# ─────────────────────────────────────────

returns = data.pct_change().dropna()

print("\nAnnualised Returns:")
print((returns.mean() * 252).round(4))

print("\nAnnualised Volatility:")
print((returns.std() * np.sqrt(252)).round(4))

print("\nSharpe Ratio (Risk-Free Rate = 6.5%):")
sharpe = (returns.mean() * 252 - 0.065) / (returns.std() * np.sqrt(252))
print(sharpe.round(4))

# ─────────────────────────────────────────
# STEP 3 — Correlation Matrix
# ─────────────────────────────────────────

plt.figure(figsize=(10, 8))
sns.heatmap(returns.corr(), annot=True, cmap='RdYlGn', center=0)
plt.title('Stock Return Correlation Matrix - NSE Top 5 Stocks')
plt.tight_layout()
plt.savefig('correlation_matrix.png', dpi=150)
plt.show()

# ─────────────────────────────────────────
# STEP 4 — Moving Average Strategy (Reliance)
# ─────────────────────────────────────────

stock = data['RELIANCE.NS']
stock_df = pd.DataFrame(stock)
stock_df['MA20'] = stock_df['RELIANCE.NS'].rolling(20).mean()
stock_df['MA50'] = stock_df['RELIANCE.NS'].rolling(50).mean()
stock_df['Signal'] = np.where(stock_df['MA20'] > stock_df['MA50'], 1, 0)
stock_df['Position'] = stock_df['Signal'].diff()

plt.figure(figsize=(14, 7))
plt.plot(stock_df.index, stock_df['RELIANCE.NS'], label='Price', linewidth=1)
plt.plot(stock_df.index, stock_df['MA20'], label='20-Day MA', linewidth=1.5)
plt.plot(stock_df.index, stock_df['MA50'], label='50-Day MA', linewidth=1.5)
plt.scatter(stock_df[stock_df['Position'] == 1].index,
            stock_df[stock_df['Position'] == 1]['RELIANCE.NS'],
            marker='^', color='green', s=100, label='Buy Signal')
plt.scatter(stock_df[stock_df['Position'] == -1].index,
            stock_df[stock_df['Position'] == -1]['RELIANCE.NS'],
            marker='v', color='red', s=100, label='Sell Signal')
plt.title('Reliance Industries - Moving Average Strategy (MA20 vs MA50)')
plt.legend()
plt.tight_layout()
plt.savefig('ma_strategy.png', dpi=150)
plt.show()

# ─────────────────────────────────────────
# STEP 5 — User Funnel Simulation
# ─────────────────────────────────────────

np.random.seed(42)
n_users = 10000

funnel_data = pd.DataFrame({
    'user_id': range(n_users),
    'app_downloaded':  [1] * n_users,
    'registered':      np.random.binomial(1, 0.72, n_users),
    'kyc_completed':   np.random.binomial(1, 0.55, n_users),
    'first_deposit':   np.random.binomial(1, 0.38, n_users),
    'first_trade':     np.random.binomial(1, 0.28, n_users),
    'second_trade':    np.random.binomial(1, 0.18, n_users),
    'monthly_active':  np.random.binomial(1, 0.12, n_users)
})

funnel_stages = [
    'app_downloaded', 'registered', 'kyc_completed',
    'first_deposit', 'first_trade', 'second_trade', 'monthly_active'
]

funnel_volumes   = [funnel_data[s].sum() for s in funnel_stages]
funnel_rates     = [v / funnel_volumes[0] * 100 for v in funnel_volumes]
step_conversions = [100] + [
    funnel_volumes[i] / funnel_volumes[i-1] * 100
    for i in range(1, len(funnel_volumes))
]

funnel_df = pd.DataFrame({
    'Stage':               funnel_stages,
    'Users':               funnel_volumes,
    'Overall_Conversion_%': [round(r, 2) for r in funnel_rates],
    'Step_Conversion_%':    [round(s, 2) for s in step_conversions]
})

print("\nUser Funnel Analysis:")
print(funnel_df.to_string(index=False))

drop_offs      = [(funnel_stages[i], step_conversions[i]) for i in range(1, len(step_conversions))]
biggest_dropoff = min(drop_offs, key=lambda x: x[1])
print(f"\nBiggest drop-off: {biggest_dropoff[0]} — only {biggest_dropoff[1]:.1f}% step conversion")
print("Recommendation: Focus product effort here — AI Trade Recommendation Feature")

# ─────────────────────────────────────────
# STEP 6 — Funnel Visualisation
# ─────────────────────────────────────────

plt.figure(figsize=(12, 7))
colors = ['#2196F3', '#4CAF50', '#FFC107', '#FF9800', '#F44336', '#9C27B0', '#607D8B']
bars = plt.barh(range(len(funnel_stages)), funnel_volumes,
                color=colors, edgecolor='white', linewidth=2)

for bar, volume, rate in zip(bars, funnel_volumes, funnel_rates):
    plt.text(bar.get_width() + 50, bar.get_y() + bar.get_height() / 2,
             f'{volume:,} ({rate:.1f}%)', va='center', fontsize=10)

plt.yticks(range(len(funnel_stages)),
           [s.replace('_', ' ').title() for s in funnel_stages])
plt.xlabel('Number of Users')
plt.title('Trading App User Acquisition & Activation Funnel\n(Univest-Style Platform, n=10,000)')
plt.tight_layout()
plt.savefig('user_funnel.png', dpi=150)
plt.show()
