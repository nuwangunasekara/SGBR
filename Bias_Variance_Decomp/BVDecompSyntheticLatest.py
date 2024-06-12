import math
import os

import numpy as np
from scipy.io import arff
from sklearn.model_selection import KFold
from mlxtend.evaluate import bias_variance_decomp
from sklearn.datasets import load_diabetes

from SKCapyMOARegressor import SKCapyMOARegressor
from moa.classifiers.meta import StreamingGradientBoostedTrees, OzaBag
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-d", "--dataset", type=str, help="arff dataset", default='House8L')
parser.add_argument("-x", "--dataset_dir", type=str, help="arff dataset directory ", default='../exp/RDatasets/')
args = parser.parse_args()

def get_data(dir, f_name):
    # Load the ARFF file
    file_path = os.path.join(dir, f_name)
    data, meta = arff.loadarff(file_path)

    # Convert the loaded data to a numpy array
    data_np = np.array(data.tolist(), dtype=np.float32)

    # Split data into X and y
    X = data_np[:, :-1]  # All rows, all columns except the last
    y = data_np[:, -1]  # All rows, only the last column

    print(f'Loading {file_path}, done')

    return X, y


def compute_BVDecomp_with_CV(CLI, X, y, MOA_regressor=StreamingGradientBoostedTrees, dir=None, synth_dataset=None):
    model = SKCapyMOARegressor(MOA_regressor=MOA_regressor, CLI=CLI)

    # Lists to store results
    biases = []
    variances = []
    errors = []

    if synth_dataset is None:
        # Set up cross-validation
        kf = KFold(n_splits=10)
        # Perform cross-validation
        for train_index, test_index in kf.split(X):
            X_train, X_test = X[train_index], X[test_index]
            y_train, y_test = y[train_index], y[test_index]

            avg_expected_loss, avg_bias, avg_var = bias_variance_decomp(
                model, X_train, y_train, X_test, y_test, loss='mse', random_seed=42, num_rounds=10
            )

            biases.append(avg_bias)
            variances.append(avg_var)
            errors.append(avg_expected_loss)
    else:
        for f in [f'{synth_dataset}_{i}' for i in range(1, 11)]:
            X_train, y_train = get_data(dir, f)
            X_test, y_test = get_data(dir, f'{synth_dataset}_{12}')
            avg_expected_loss, avg_bias, avg_var = bias_variance_decomp(
                model, X_train, y_train, X_test, y_test, loss='mse', random_seed=42, num_rounds=10
            )

            biases.append(avg_bias)
            variances.append(avg_var)
            errors.append(avg_expected_loss)


    # Calculate mean values
    mean_bias = np.mean(biases)
    mean_variance = np.mean(variances)
    mean_error = np.mean(errors)

    return mean_error, math.sqrt(mean_bias), math.sqrt(mean_variance)


# data = load_diabetes()
# X, y = data.data, data.target

# dataset_dir = '/Scratch/ng98/datasets/RDatasets/'
# datasets=["House8L","MetroTraffic","abalone","ailerons","bike","elevators","fried"]
# datasets=["House8L"]

dataset = args.dataset
synth_dataset = dataset if dataset in ['FriedmanGra', 'FriedmanGsg', 'FriedmanLea'] else None
dataset_dir = args.dataset_dir

print(f'Synthetic Dataset: {synth_dataset}')

with open(f"BVDecompose_Results_BagB_{dataset}.csv", "w") as file:
    file.write(f'dataset,method,boosting_iterations,mean_error,sqrt_mean_bias,sqrt_mean_var\n')
    file.flush()

    X, y = get_data(dataset_dir, f'{dataset}.arff')

    for b in range(5,105, 5):
        print(f'Boosting iteration {b}')

        # CLI = f'-t -L 1.0 -m 75 -s {b} -l (trees.FIMTDD -s VarianceReductionSplitCriterion -g 50 -c 0.01 -e)'
        # mean_error, sqrt_mean_bias, sqrt_mean_var = compute_BVDecomp_with_CV(CLI, X, y, MOA_regressor=StreamingGradientBoostedTrees, dir=dataset_dir)
        # file.write(f'{dataset},B,{b},{mean_error},{sqrt_mean_bias},{sqrt_mean_var}\n')
        # file.flush()
        #
        # CLI = f'-t -L 1.0 -m 75 -s {b} -l (meta.OzaBag -s 5 -l (trees.FIMTDD -s VarianceReductionSplitCriterion -g 50 -c 0.01 -e))'
        # mean_error, sqrt_mean_bias, sqrt_mean_var = compute_BVDecomp_with_CV(CLI, X, y, MOA_regressor=StreamingGradientBoostedTrees, dir=dataset_dir)
        # file.write(f'{dataset},BB,{b},{mean_error},{sqrt_mean_bias},{sqrt_mean_var}\n')
        # file.flush()

        CLI = f'-s 5 -l (meta.StreamingGradientBoostedTrees -t -L 1.0 -m 75 -s {b} -l (trees.FIMTDD -s VarianceReductionSplitCriterion -g 50 -c 0.01 -e))'
        mean_error, sqrt_mean_bias, sqrt_mean_var = compute_BVDecomp_with_CV(CLI, X, y, MOA_regressor=OzaBag, dir=dataset_dir)
        file.write(f'{dataset},BagB,{b},{mean_error},{sqrt_mean_bias},{sqrt_mean_var}\n')
        file.flush()


