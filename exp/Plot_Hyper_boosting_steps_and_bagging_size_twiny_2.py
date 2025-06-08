import pandas as pd
import matplotlib.pyplot as plt
import os
# import mplcursors

# df = pd.read_csv('output_sgbt_oza_para_search/final_results.txt')
results_dir='./output_sgbt_oza_para_search/'

measurements = [
    ["adjusted coefficient of determination", r"average mean $\bar{R}^{2}$", "b", "avg stdAdjustedR2", r'$\bar{R}^{2}$'],
    ["evaluation time (wall) (seconds)", r"average mean $WallTime$ $(s)$", "r", "avg stdWallTime(s)", 'Wall Time'],
]
# Read multiple sheets by name
sheets_dict = pd.read_excel(os.path.join(results_dir,'Results_.xlsx'), sheet_name=[i[3] for i in measurements])

for sheet in sheets_dict.values():
    sheet['boosting_iterations'] = sheet['method'].apply(lambda x: int(x.split(',')[0]))
    sheet['bagging_ensemble_size'] = sheet['method'].apply(lambda x: int(x.split(',')[-1]))
    sheet.rename(columns={'avg': 'mean', 'std_for_all': 'std'}, inplace=True)

df = pd.read_csv(os.path.join(results_dir,'final_results.txt'))
df['boosting_iterations'] = df['learner'].apply(lambda x: int(x.split('(')[0].split('_')[1]))
df['bagging_ensemble_size'] = df['learner'].apply(lambda x: int(x.split(')')[0].split('_')[-1]))
df['evaluation time (wall) (seconds)'] = df['evaluation time (wall) (seconds)']

points = ['boosting_iterations', 'bagging_ensemble_size']
experiment = 'learner'

# Generate some data
p1 = points[0]
m1 = measurements[0]
s = m1[3]
x1 = sheets_dict[s]['boosting_iterations']
y1_mean = sheets_dict[s]['mean']
y1_std = sheets_dict[s]['std']

m2 = measurements[1]
s = m2[3]
x2 = sheets_dict[s][p1]
y2_mean = sheets_dict[s]['mean']
y2_std = sheets_dict[s]['std']

# Create a figure and axis
fig, ax1 = plt.subplots()

# Plot on the first y-axis (left)
x_field = p1.replace('_', ' ')
y_field = points[1].replace('_', ' ')
ax1.set_title(f"{x_field} x {y_field} = 100")
line1, =  ax1.plot(x1, y1_mean, marker = 'o', color=m1[2], linestyle='-', label=m1[4])
ax1.set_xlabel(f'{x_field} ({x_field}, {y_field})') # Bottom x-axis label
ax1.set_ylabel(m1[1], color=m1[2])
ax1.tick_params(axis='y', labelcolor=m1[2])

# Annotating specific points
annotations = [ (x1[i], y1_mean[i]) for i, _ in enumerate(x1) if x1[i] not in [4, 5] ]

for point in annotations:
    ax1.annotate(f'({point[0]}, {100//point[0]})', xy=point,
                 xytext=(5, 0),
                 fontsize=6,
                 color=m1[2],
                 textcoords='offset points',
                 )

# Create a second y-axis (right) sharing the same x-axis
ax2 = ax1.twinx()
line2, =  ax2.plot(x2, y2_mean, marker = 'o', label=m2[4], color=m2[2], linestyle=':')
ax2.set_ylabel(m2[1], color=m2[2])
ax2.tick_params(axis='y', labelcolor=m2[2])
# Annotating specific points
annotations = [ (x2[i], y2_mean[i]) for i, _ in enumerate(x2) if x2[i] not in [] ]

for point in annotations:
    ax2.annotate(f'({point[0]}, {100//point[0]})', xy=point,
                 xytext=(-20, 1),
                 fontsize=6,
                 color=m2[2],
                 textcoords='offset points',
                 )

# Combine legends
lines = [line1, line2]
labels = [line.get_label() for line in lines]
plt.legend(lines, labels, loc='upper right')

plt.tight_layout()
plt.savefig(os.path.join(results_dir, f'ParaSearch.pdf'))
plt.show()
