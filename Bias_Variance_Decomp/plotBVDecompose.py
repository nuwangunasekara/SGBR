import matplotlib.pyplot as plt
import pandas as pd
import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-d", "--dataset", type=str, help="arff dataset", default='ailerons')
parser.add_argument("-r", "--results_dir", type=str, help="results directory", default='RESULTS/')
args = parser.parse_args()

# Read data from CSV file
dfs = []
path = os.path.join(args.results_dir, f'BVDecompose_Results_{args.dataset}.csv')
if os.path.exists(path):
    dfs.append(pd.read_csv(path))
path = os.path.join(args.results_dir, f'BVDecompose_Results_BagB_{args.dataset}.csv')
if os.path.exists(path):
    dfs.append(pd.read_csv(path))
df = pd.concat(dfs, ignore_index=True)

# Plot sqrt_mean_bias and sqrt_mean_var for each method with legends
plt.figure(figsize=(18, 9))

# bv_component = {'sqrt_mean_bias': [':', r'$\sqrt{mean(bias)}$'], 'sqrt_mean_var': ['--', r'$\sqrt{mean(variance)}$']}
# bv_component = {'sqrt_mean_bias': [':', r'$\sqrt{bias}$'], 'sqrt_mean_var': ['--', r'$\sqrt{variance}$']}
bv_component = {'sqrt_mean_bias': [':', r'$\sqrt{bias}$', 'green'], 'sqrt_mean_var': ['--', r'$\sqrt{variance}$', 'red']}
methods = {'B': [r'$SGBT$', 'red'], 'BB': [r'$SGBT(Oza)$', 'green'], 'BagB': [r'$Oza(SGBT)$', 'blue']}
# methods = {'B': 'red'}

for method in df['method'].unique():
    if method in methods.keys():
        subset = df[df['method'] == method]
        for bv_key in bv_component.keys():
            label =f"{methods[method][0]} {bv_component[bv_key][1]}"
            # label = f"{bv_component[bv_key][1]}"
            color = methods[method][1]
            # color = f'{bv_component[bv_key][2]}'
            plt.plot(subset['boosting_iterations'], subset[bv_key], label=label, color=color, linestyle=bv_component[bv_key][0])

plt.xlabel('Boosting Iterations', fontsize=20)
# plt.ylabel('Values')
plt.title(f'{args.dataset}', fontsize=20)
if args.dataset in ['FriedmanGsg', 'fried']:
    plt.legend(prop={'size': 20})
# Show only the x and y axes
ax = plt.gca()
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# ax.spines['left'].set_linewidth(0.05)
# ax.spines['bottom'].set_linewidth(0.05)
ax.spines['left'].set_linewidth(0.5)
ax.spines['bottom'].set_linewidth(0.5)

# plt.savefig(os.path.join(os.path.join(args.results_dir, 'plots'), f'BVDecompose_Results_{args.dataset}_B.pdf'))
plt.savefig(os.path.join(os.path.join(args.results_dir, 'plots'), f'BVDecompose_Results_{args.dataset}.pdf'))
# plt.show()
