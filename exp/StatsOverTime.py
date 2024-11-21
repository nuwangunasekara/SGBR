import matplotlib.pyplot as plt
import subprocess
import argparse
import os
import shutil

import mplcursors
import pandas as pd
import numpy as np
import re

parser = argparse.ArgumentParser()
parser.add_argument("-r", "--resultsDir", type=str, help="Results directory", default='output_stats/')
parser.add_argument("-f", "--imageSaveFileName", type=str, help="File name for the image", default='StatsOverTime.pdf',
                    choices=['StatsOverTime_Acc.pdf', 'StatsOverTime_Size.pdf', 'avgNumNodes.pdf'])
args = parser.parse_args()
baseline_compare = False

csv_files = []
if len(csv_files) == 0:
    command = subprocess.Popen("find " + args.resultsDir + " -iname '*.csv'",
                               shell=True, stdout=subprocess.PIPE)
    for line in command.stdout.readlines():
        csv_files.append(line.decode("utf-8").replace('\n', ''))

cpu_time_with_memory_column_name = 'evaluation time (cpu seconds)_with_memory'

df_final = None
for f in csv_files:
    if os.stat(f).st_size == 0:
        print('WARNING: ZERO size file: {}'.format(f))
        continue
    # print(f)

    df = pd.read_csv(f)

    if f.find('StatsOverTimeRandomTrainS1NoMemory') > -1:
        f_with_memory = f.replace('StatsOverTimeRandomTrainS1NoMemory', 'StatsOverTimeRandomTrainS1')
        f_with_memory = f_with_memory.replace('plot', 'S1Memory')
        if os.path.exists(f_with_memory) and os.stat(f_with_memory).st_size > 0:
            df_with_memory = pd.read_csv(f_with_memory)
            df_joined = df.join(df_with_memory, lsuffix='_caller', rsuffix='_with_memory')
            columns_to_import = ['model cost (RAM-Hours)', 'model serialized size (bytes)', 'evaluation time (cpu seconds)']
            for column_to_import in columns_to_import:
                if column_to_import == 'evaluation time (cpu seconds)':
                    df[cpu_time_with_memory_column_name] = df_joined[column_to_import + '_with_memory']
                else:
                    df[column_to_import] = df_joined[column_to_import + '_with_memory']
            if df_final is not None:
                if cpu_time_with_memory_column_name not in df_final.columns:
                    df_final.insert(0, cpu_time_with_memory_column_name, '')

    if df_final is None:
        columns = [c.lstrip() for c in df.columns]
        df_final = pd.DataFrame(columns=columns)

    dataset_name = f.split('/')[-2]
    learner = f.split('/')[-1]

    df['stream'] = dataset_name
    df['Learner'] = learner
    df_final = pd.concat([df_final, df], ignore_index=True)

items_to_plot = [
    # 'learning evaluation instances',
    'classifications correct (percent)',
    # 'evaluation time (cpu seconds)',
    # cpu_time_with_memory_column_name,
    # 'model cost (RAM-Hours)',
    # 'classified instances',
    # 'Kappa Statistic (percent)',
    # 'Kappa Temporal Statistic (percent)',
    # 'Kappa M Statistic (percent)',
    # 'model training instances',
    # 'model serialized size (bytes)',
    # 'avgNumNodes',
    # 'avgSplitsByConfidence',
    # 'avgSplitsByHBound',
    # 'avgSplitsByHBoundSmallerThanTieThreshold',
    # 'avgTotalSplits'
]

items_to_plot = [
    ["adjusted coefficient of determination", r"$\bar{R}^{2}$"],
    ["evaluation time (wall) (seconds)", r"$WallTime (s)$"],
]

methods = {
    'SGBT(Oza(FIRTDD)).csv': [r'SGB(Oza)', 'red'],
    'SOKNL(FIRTDD).csv': [r'$SOKNL$', 'green'],
    'ARFReg(FIRTDD).csv': [r'$ARFReg$', 'green'],
    'Oza(FIRTDD).csv': [r'$OzaReg$', 'green'],
}

plt.rc('xtick', labelsize=8)    # fontsize of the tick labels
plt.rc('ytick', labelsize=8)    # fontsize of the tick labels
fig, axs = plt.subplots(len(items_to_plot), 1)
# fig.tight_layout(pad=5.0)
# Paper
# fig.set_figwidth(5)
# fig.set_figheight(2)
# # Thesis
fig.set_figwidth(8)
fig.set_figheight(6)
# fig.suptitle(args.resultsDir.split('/')[-1])

rows = ['learning evaluation instances']
learners_to_plot = list(df_final['Learner'].unique())
streams = list(df_final['stream'].unique())

for learner_to_plot in learners_to_plot:
    df_learner = df_final[df_final['Learner'] == learner_to_plot]

    if baseline_compare:
        pass
    else:
        linestyle = 'solid'
    for stream in streams:
        df_learner_stream = df_learner[df_learner['stream'] == stream]
        i = 0
        for plot_item in items_to_plot:
            pd_plot = pd.pivot_table(df_learner_stream, values=plot_item[0], index=rows, columns='Learner', aggfunc=np.mean, fill_value=0)
            if pd_plot.empty:
                continue
            pd_plot['learning evaluation instances'] = pd_plot.index


            if len(items_to_plot) == 1:
                tmp_axs = axs
            else:
                tmp_axs = axs[i]
            label = methods[pd_plot.columns[0]][0]
            # tmp_axs.plot(pd_plot['learning evaluation instances'], pd_plot[plot_item], color=color,
            #             linestyle=linestyle, marker=m, label=label.replace('_', ' '), lw=0.5, mew=0.05, ms=0.05)
            tmp_axs.plot(pd_plot['learning evaluation instances'], pd_plot[pd_plot.columns[0]],label=label, lw=0.5, mew=0.05, ms=0.05)

            i += 1


def plot_drifts(ax):
    for x in (125000, 250000, 375000):
        ax.axvline(x=x, color='grey', linestyle='--', lw=0.5)
        # plt.axvline(x=x+50, color='grey', linestyle='--')
        # ax.axvline(x=x - 50000, color='grey', linestyle='--', lw=0.5)
        # ax.axvline(x=x + 50000, color='grey', linestyle='--', lw=0.5)


if len(items_to_plot) == 1:
    plot_drifts(axs)
else:
    for ax in axs:
        plot_drifts(ax)


for i in range(len(items_to_plot)):
    if len(items_to_plot) == 1:
        tmp_axs = axs
        if baseline_compare:
            tmp_axs.legend(loc='lower left', fontsize=6)
        else:
            tmp_axs.legend(loc='center right', fontsize=6)
    else:
        tmp_axs = axs[i]
        tmp_axs.legend(loc='upper left', fontsize=6)
    tmp_axs.spines['top'].set_visible(False)
    tmp_axs.spines['right'].set_visible(False)
    tmp_axs.spines['bottom'].set_linewidth(0.1)
    tmp_axs.spines['left'].set_linewidth(0.1)
    # tmp_axs.spines['bottom'].set_visible(False)
    # tmp_axs.spines['left'].set_visible(False)

    ylabel = items_to_plot[i][1]

    tmp_axs.set_ylabel(ylabel, fontsize=8)
    tmp_axs.set_xlabel('# instances seen', fontsize=8)
    # if not baseline_compare:
        # tmp_axs.set_xlim([0,1300000])

# ax.set_ylim(y_min, y_max)
# ax.set_title(args.resultsDir.split('/')[-1])
# axs[0].set_title('classifications correct (percent)')
# axs[1].set_title('Average # nodes in a single FIMTDD')
# mplcursors.cursor(hover=True)

# set the spacing between subplots
plt.subplots_adjust(
    left=0.1,
    bottom=0.17,
    right=0.9,
    top=0.83,
    wspace=0.0,
    hspace=0.0
)

plt.savefig(os.path.join(args.resultsDir, args.imageSaveFileName))
# plt.legend()
plt.show()