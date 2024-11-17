import pandas as pd
import matplotlib.pyplot as plt
import os
# import mplcursors

# df = pd.read_csv('output_sgbt_oza_para_search/final_results.txt')
results_dir='./output_sgbt_oza_para_search/'

measurements = [
    ["adjusted coefficient of determination", r"average mean $\bar{R}^{2}$", "b", "avg stdAdjustedR2"],
    ["evaluation time (wall) (seconds)", r"average mean $WallTime$ $(s)$", "r", "avg stdWallTime(s)"],
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
# df['evaluation time (wall) (seconds)'] = df['evaluation time (wall) (seconds)']/100

# print(df)

#######################################################################################
# Group the data by subject, experiment, and point, then calculate the mean and standard error
# measurements = ['adjusted coefficient of determination', 'evaluation time (wall) (seconds)']
#
# measurements = [
#     ["adjusted coefficient of determination", r"average mean $\bar{R}^{2}$", "b"],
#     ["evaluation time (wall) (seconds)", r"average mean $WallTime$ $(s)$", "r"],
# ]

# measurement = 'adjusted coefficient of determination'
# measurement = 'evaluation time (wall) (seconds)'
points = ['boosting_iterations', 'bagging_ensemble_size']
# subject = 'bagging_ensemble_size'
experiment = 'learner'

def get_grouped_and_sorted_data(point, measurement):
    grouped_data = df.groupby([point]).agg(
        mean=(measurement[0], 'mean'),
        std=(measurement[0], 'sem')
    ).reset_index()

    grouped_data_sorted = grouped_data.sort_values(by=point)
    latex_table = grouped_data_sorted.to_latex(index=False, float_format="%.2f")
    print(latex_table)
    return grouped_data_sorted


# Generate some data
p1 = points[0]
m1 = measurements[0]
grouped_data_1 = get_grouped_and_sorted_data(p1, m1)
x1 = grouped_data_1[p1]
y1_mean = grouped_data_1['mean']
y1_std = grouped_data_1['std']
s = m1[3]
x1 = sheets_dict[s]['boosting_iterations']
y1_mean = sheets_dict[s]['mean']
y1_std = sheets_dict[s]['std']

m2 = measurements[1]
grouped_data_2 = get_grouped_and_sorted_data(p1, m2)
x2 = grouped_data_2[p1]
y2_mean = grouped_data_2['mean']
y2_std = grouped_data_2['std']
s = m2[3]
x2 = sheets_dict[s][p1]
y2_mean = sheets_dict[s]['mean']
y2_std = sheets_dict[s]['std']

# Create a figure and axis
fig, ax1 = plt.subplots()

# Plot on the first y-axis (left)
x_field = p1.replace('_', ' ')
y_field = points[1].replace('_', ' ')
title = f"{x_field} x {y_field} = 100"
ax1.set_title(f'{title}')
ax1.plot(x1, y1_mean, marker = 'o', color=m1[2])
# ax1.fill_between(x1, y1_mean - y1_std, y1_mean + y1_std, alpha=0.1, color=m1[2])
ax1.set_xlabel(f'({x_field}, {y_field})') # Bottom x-axis label
ax1.set_ylabel(m1[1], color=m1[2])
ax1.tick_params(axis='y', labelcolor=m1[2])
# ax1.axvline(x=5, color='grey', linestyle=':', label='boosting 5, bagging ensemble size 20')
# ax1.axvline(x=10, color='grey', linestyle=':', label='boosting 10, bagging ensemble size 10')

# Annotating specific points
annotations = [ (x1[i], y1_mean[i]) for i, _ in enumerate(x1) if x1[i] not in [4, 5] ]

for point in annotations:
    ax1.annotate(f'({point[0]}, {100//point[0]})', xy=point,
                 xytext=(5, 0),
                 fontsize=6,
                 color=m1[2],
                 textcoords='offset points',
                 # arrowprops=dict(arrowstyle='-', lw=1.5)
                 )



# ax1.legend(loc='upper center',)

# Create a second y-axis (right) sharing the same x-axis
ax2 = ax1.twinx()
ax2.plot(x2, y2_mean, marker = 'o', label=m2[1], color=m2[2])
# ax2.fill_between(x2, y2_mean - y2_std, y2_mean + y2_std, alpha=0.1, color=m2[2])
ax2.set_ylabel(m2[1], color=m2[2])
ax2.tick_params(axis='y', labelcolor=m2[2])
# Annotating specific points
annotations = [ (x2[i], y2_mean[i]) for i, _ in enumerate(x2) if x2[i] not in [] ]
# annotations = []

for point in annotations:
    ax2.annotate(f'({point[0]}, {100//point[0]})', xy=point,
                 xytext=(-20, 1),
                 fontsize=6,
                 color=m2[2],
                 textcoords='offset points',
                 # arrowprops=dict(arrowstyle='-', lw=1.5)
                 )
# ax2.legend(loc='lower center',)

# Create a second x-axis on the top
# p2=points[1]
# ax3 = ax1.twiny()
# ax3.set_xlabel(p2.replace('_', ' ')) # Top x-axis label
# print(ax1.get_xlim())
# ax3.set_xlim(reversed(ax1.get_xlim()))  # Ensure the top x-axis has the same range
# # x2 = x1[::-1]
# x3 = list(reversed(x1))
# print(x3)
# ax3.set_xticks([1, 100])  # Set different tick marks for the top axis
# # ax3.set_xticklabels(x3)  # Different labels for the top axis

# Show the plot
# plt.legend()
plt.tight_layout()
plt.savefig(os.path.join(results_dir, f'ParaSearch.pdf'))
plt.show()
