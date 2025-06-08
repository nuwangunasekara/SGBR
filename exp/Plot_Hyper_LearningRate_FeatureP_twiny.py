import os

import pandas as pd
import matplotlib.pyplot as plt

from exp.StatsOverTime import linestyle

# Load Excel data from the "RawData" sheet
results_dir='./output_sgbt_oza_para_search_lr_fp/'
df = pd.read_excel(os.path.join(results_dir,'Results_.xlsx'), sheet_name="RawData")

# Desired method order
method_order = ["0.5,25", "0.5,75", "0.5,100",
                "1.0,25", "1.0,75", "1.0,100",
                "1.5,25", "1.5,75", "1.5,100"]

# Filter and aggregate the data
agg_df = df[df['method'].isin(method_order)].groupby('method').agg({
    'adjusted coefficient of determination': 'mean',
    'evaluation time (wall) (seconds)': 'mean'
}).reindex(method_order)

# Plotting
fig, ax1 = plt.subplots(figsize=(10, 6))

# Blue line for adjusted R²
color1 = 'tab:blue'
ax1.set_xlabel('(Learning rate, Feature %)')
ax1.set_ylabel( r"average mean $\bar{R}^{2}$", color=color1)

dfp = pd.read_excel(os.path.join(results_dir,'Results_.xlsx'), sheet_name="Avg AdjustedR2")
dfp = dfp[dfp['method'].isin(method_order)].groupby('method').agg({'avg': 'mean'}).reindex(method_order)

line1, =  ax1.plot(dfp.index, dfp['avg'], color=color1, marker='o', linewidth=2, label=r'$\bar{R}^{2}$', linestyle='-')
ax1.tick_params(axis='y', labelcolor=color1)
ax1.set_xticks(range(len(method_order)))
ax1.set_xticklabels(method_order, rotation=45)

# Annotate adjusted R² values
for i, (method, value) in enumerate(dfp['avg'].items()):
    ax1.annotate(f"{value:.2f}", xy=(i, value), xytext=(0, 5), textcoords="offset points", ha='center', color=color1, fontsize=9)

# Red line for evaluation time
ax2 = ax1.twinx()
color2 = 'tab:red'
ax2.set_ylabel(r"average mean $WallTime$ $(s)$", color=color2)

dfp = pd.read_excel(os.path.join(results_dir,'Results_.xlsx'), sheet_name="Avg WallTime(s)")
dfp = dfp[dfp['method'].isin(method_order)].groupby('method').agg({'avg': 'mean'}).reindex(method_order)

line2, = ax2.plot(dfp.index, dfp['avg'], color=color2, marker='s', linewidth=2, label='Wall Time', linestyle=':')
ax2.tick_params(axis='y', labelcolor=color2)

# Combine legends
lines = [line1, line2]
labels = [line.get_label() for line in lines]
plt.legend(lines, labels, loc='upper left')

plt.title(r'Performance of $SGB(Oza)$ $(10,10)$ by Learning rate and Feature %')
plt.tight_layout()
plt.savefig(os.path.join(results_dir, f'ParaSearch_lr_fp.pdf'))
plt.legend()
plt.show()
