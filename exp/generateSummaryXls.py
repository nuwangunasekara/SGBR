import glob
import subprocess
import argparse
import os
import shutil
import pandas as pd
import numpy as np
import re

parser = argparse.ArgumentParser()
parser.add_argument("-r", "--resultsDir", type=str, help="Results directory",
                    default='./output')
args = parser.parse_args()

random_seed_option = '-Z'

# column_order = ['AGR_a_S', 'AGR_g_S', 'RBF_Bm_S', 'RBF_Bf_S', 'RandomTreeGenerator_S_10', 'elecNormNew', 'airlines', 'LED_a_S', 'LED_g_S', 'RBF_m_S', 'RBF_f_S', 'LED_S_10', 'RandomRBF5_S_10', 'covtypeNorm',]
# column_order = ['AGR_a_S', 'AGR_g_S', 'RBF_Bm_S', 'RBF_Bf_S', 'RandomTreeGenerator_S_10', 'elecNormNew', 'airlines', 'LED_a_S', 'LED_g_S', 'RBF_m_S', 'RBF_f_S', 'LED_S_10', 'covtypeNorm',]
# column_order = ['airlines',]
column_order = ['fried', 'House8L', 'abalone', 'bike', 'elevators', 'MetroTraffic', 'ailerons', 'hyperA', 'FriedmanLea',
                'FriedmanGra', 'FriedmanGsg']
column_order = ['fried', 'House8L', 'abalone', 'bike', 'elevators', 'MetroTraffic', 'ailerons', 'FriedmanLea', 'FriedmanGra', 'FriedmanGsg',  'hyperA']
column_order = ['fried', 'House8L', 'abalone', 'bike', 'elevators', 'MetroTraffic', 'ailerons', 'FriedmanLea', 'FriedmanGra', 'FriedmanGsg',  'hyperA', 'DemandF', 'NZEnergy', 'SUP2I', 'SUP3A', 'SUP3G']

# pv_table_values = {
#     'classifications correct (percent)':{'name': 'Acc', 'ascending': False},
#     'Kappa M Statistic (percent)':{'name': 'KappaM', 'ascending': False},
#     # 'F1 Score (percent)':{'name': 'F1'},
#     # 'Precision (percent)':{'name': 'Precision'},
#     # 'Recall (percent)':{'name': 'Recall'},
#     # 'Recall for class 0 (percent)': {'name': 'Recall0'},
#     # 'Recall for class 1 (percent)': {'name': 'Recall1'},
#     # 'Recall for class 2 (percent)': {'name': 'Recall2'},
#     # 'Recall for class 3 (percent)': {'name': 'Recall3'},
#     # 'Recall for class 4 (percent)': {'name': 'Recall4'},
#     # 'Recall for class 5 (percent)': {'name': 'Recall5'},
#     # 'Recall for class 6 (percent)': {'name': 'Recall6'},
#     'evaluation time (cpu seconds)':{'name': 'Time(s)', 'ascending': True}
# }

pv_table_values = {
    'adjusted coefficient of determination': {'name': 'adjustR2', 'ascending': False},
    'coefficient of determination': {'name': 'R2', 'ascending': False},
    'evaluation time (cpu seconds)': {'name': 'Time(s)', 'ascending': True},
    'evaluation time (wall) (seconds)': {'name': 'TimeWall(s)', 'ascending': True}
}

pv_table_values = {
    'adjusted coefficient of determination': {'name': 'AdjustedR2', 'ascending': False, 'decimal_places': 2},
    'evaluation time (wall) (seconds)': {'name': 'WallTime(s)', 'ascending': True, 'decimal_places': 1}
}

# row_order = [
#     [
#         'meta.OzaBag_-s_10_-l_(meta.StreamingGradientBoostedTrees_-t_-L_1.0_-m_75_-s_10_-l_(trees.FIMTDD_-s_VarianceReductionSplitCriterion_-g_50_-c_0.01_-e)).csv',
#         'Oza(SGBT(FIRTDD))'],
#     [
#         'meta.OzaBag_-p_0.9_-s_10_-l_(meta.StreamingGradientBoostedTrees_-t_-L_1.0_-m_75_-s_10_-l_(trees.FIMTDD_-s_VarianceReductionSplitCriterion_-g_50_-c_0.01_-e)).csv',
#         'OzaP0.9(SGBT(FIRTDD))'],
#     [
#         'meta.OzaBag_-p_0.8_-s_10_-l_(meta.StreamingGradientBoostedTrees_-t_-L_1.0_-m_75_-s_10_-l_(trees.FIMTDD_-s_VarianceReductionSplitCriterion_-g_50_-c_0.01_-e)).csv',
#         'OzaP0.8(SGBT(FIRTDD))'],
#     [
#         'meta.OzaBag_-T_-s_10_-l_(meta.StreamingGradientBoostedTrees_-t_-L_1.0_-m_75_-s_10_-l_(trees.FIMTDD_-s_VarianceReductionSplitCriterion_-g_50_-c_0.01_-e)).csv',
#         'Oza_T(SGBT(FIRTDD))'],
#     [
#         'meta.OzaBag_-p_0.9_-T_-s_10_-l_(meta.StreamingGradientBoostedTrees_-t_-L_1.0_-m_75_-s_10_-l_(trees.FIMTDD_-s_VarianceReductionSplitCriterion_-g_50_-c_0.01_-e)).csv',
#         'OzaP0.9_T(SGBT(FIRTDD))'],
#     [
#         'meta.OzaBag_-p_0.8_-T_-s_10_-l_(meta.StreamingGradientBoostedTrees_-t_-L_1.0_-m_75_-s_10_-l_(trees.FIMTDD_-s_VarianceReductionSplitCriterion_-g_50_-c_0.01_-e)).csv',
#         'OzaP0.8_T(SGBT(FIRTDD))'],
#     [
#         'meta.StreamingRandomPatches_-s_10_-l_(meta.StreamingGradientBoostedTrees_-t_-L_1.0_-m_75_-s_10_-l_(trees.FIMTDD_-s_VarianceReductionSplitCriterion_-g_50_-c_0.01_-e)).csv',
#         'SRP(SGBT(FIRTDD))'],
#     [
#         'meta.StreamingRandomPatches_-T_-s_10_-l_(meta.StreamingGradientBoostedTrees_-t_-L_1.0_-m_75_-s_10_-l_(trees.FIMTDD_-s_VarianceReductionSplitCriterion_-g_50_-c_0.01_-e)).csv',
#         'SRP_T(SGBT(FIRTDD))'],
#     [
#         'meta.StreamingGradientBoostedTrees_-t_-L_1.0_-m_75_-s_10_-l_(meta.OzaBag_-s_10_-l_(trees.FIMTDD_-s_VarianceReductionSplitCriterion_-g_50_-c_0.01_-e)).csv',
#         'SGBT(Oza(FIRTDD))'],
#     [
#         'meta.StreamingGradientBoostedTrees_-t_-L_1.0_-m_75_-s_10_-l_(meta.OzaBag_-p_0.9_-s_10_-l_(trees.FIMTDD_-s_VarianceReductionSplitCriterion_-g_50_-c_0.01_-e)).csv',
#         'SGBT(OzaP0.9(FIRTDD))'],
#     [
#         'meta.StreamingGradientBoostedTrees_-t_-L_1.0_-m_75_-s_10_-l_(meta.OzaBag_-p_0.8_-s_10_-l_(trees.FIMTDD_-s_VarianceReductionSplitCriterion_-g_50_-c_0.01_-e)).csv',
#         'SGBT(OzaP0.8(FIRTDD))'],
#     [
#         'meta.StreamingGradientBoostedTrees_-t_-L_1.0_-m_75_-s_10_-l_(meta.OzaBag_-T_-s_10_-l_(trees.FIMTDD_-s_VarianceReductionSplitCriterion_-g_50_-c_0.01_-e)).csv',
#         'SGBT(Oza_T(FIRTDD))'],
#     [
#         'meta.StreamingGradientBoostedTrees_-t_-L_1.0_-m_75_-s_10_-l_(meta.OzaBag_-p_0.9_-T_-s_10_-l_(trees.FIMTDD_-s_VarianceReductionSplitCriterion_-g_50_-c_0.01_-e)).csv',
#         'SGBT(OzaP0.9_T(FIRTDD))'],
#     [
#         'meta.StreamingGradientBoostedTrees_-t_-L_1.0_-m_75_-s_10_-l_(meta.OzaBag_-p_0.8_-T_-s_10_-l_(trees.FIMTDD_-s_VarianceReductionSplitCriterion_-g_50_-c_0.01_-e)).csv',
#         'SGBT(OzaP0.8_T(FIRTDD))'],
#     [
#         'meta.StreamingGradientBoostedTrees_-t_-L_1.0_-m_75_-s_10_-l_(meta.AdaptiveRandomForestRegressor_-s_10_-x_(ADWINChangeDetector_-a_0.001)_-p_(ADWINChangeDetector_-a_0.01)).csv',
#         'SGBT(ARF(FIRTDD))'],
#     [
#         'meta.StreamingGradientBoostedTrees_-t_-L_1.0_-m_75_-s_10_-l_(SOKNL_-f_-s_10_-l_(SelfOptimisingBaseTree_-s_VarianceReductionSplitCriterion_-g_50_-c_0.01)_-x_(ADWINChangeDetector_-a_0.001)_-p_(ADWINChangeDetector_-a_0.01)).csv',
#         'SGBT(SOKNLnoSelfO(FIRTDD))'],
#     [
#         'meta.StreamingGradientBoostedTrees_-t_-L_1.0_-m_75_-s_10_-l_(SOKNL_-s_10_-l_(SelfOptimisingBaseTree_-s_VarianceReductionSplitCriterion_-g_50_-c_0.01)_-x_(ADWINChangeDetector_-a_0.001)_-p_(ADWINChangeDetector_-a_0.01)).csv',
#         'SGBT(SOKNL(FIRTDD))'],
#     [
#         'meta.StreamingGradientBoostedTrees_-t_-L_1.0_-m_75_-s_10_-l_(meta.StreamingRandomPatches_-s_10_-l_(trees.FIMTDD_-s_VarianceReductionSplitCriterion_-g_50_-c_0.01_-e)).csv',
#         'SGBT(SRP(FIRTDD))'],
#     [
#         'meta.StreamingGradientBoostedTrees_-t_-L_1.0_-m_75_-s_10_-l_(meta.StreamingRandomPatches_-T_-s_10_-l_(trees.FIMTDD_-s_VarianceReductionSplitCriterion_-g_50_-c_0.01_-e)).csv',
#         'SGBT(SRP_T(FIRTDD))'],
#     ['meta.OzaBag_-s_100_-l_(trees.FIMTDD_-s_VarianceReductionSplitCriterion_-g_50_-c_0.01_-e).csv', 'Oza(FIRTDD))'],
#     ['meta.OzaBag_-p_0.9_-s_100_-l_(trees.FIMTDD_-s_VarianceReductionSplitCriterion_-g_50_-c_0.01_-e).csv',
#      'OzaP0.9(FIRTDD))'],
#     ['meta.OzaBag_-p_0.8_-s_100_-l_(trees.FIMTDD_-s_VarianceReductionSplitCriterion_-g_50_-c_0.01_-e).csv',
#      'OzaP0.8(FIRTDD))'],
#     ['meta.OzaBag_-T_-s_100_-l_(trees.FIMTDD_-s_VarianceReductionSplitCriterion_-g_50_-c_0.01_-e).csv',
#      'Oza_T(FIRTDD))'],
#     ['meta.OzaBag_-p_0.9_-T_-s_100_-l_(trees.FIMTDD_-s_VarianceReductionSplitCriterion_-g_50_-c_0.01_-e).csv',
#      'OzaP0.9_T(FIRTDD))'],
#     ['meta.OzaBag_-p_0.8_-T_-s_100_-l_(trees.FIMTDD_-s_VarianceReductionSplitCriterion_-g_50_-c_0.01_-e).csv',
#      'OzaP0.8_T(FIRTDD))'],
#     ['meta.AdaptiveRandomForestRegressor_-s_100_-x_(ADWINChangeDetector_-a_0.001)_-p_(ADWINChangeDetector_-a_0.01).csv',
#      'ARF(FIRTDD))'],
#     [
#         'SOKNL_-f_-s_100_-l_(SelfOptimisingBaseTree_-s_VarianceReductionSplitCriterion_-g_50_-c_0.01)_-x_(ADWINChangeDetector_-a_0.001)_-p_(ADWINChangeDetector_-a_0.01).csv',
#         'SOKNLnoSelfO(FIRTDD)'],
#     [
#         'SOKNL_-s_100_-l_(SelfOptimisingBaseTree_-s_VarianceReductionSplitCriterion_-g_50_-c_0.01)_-x_(ADWINChangeDetector_-a_0.001)_-p_(ADWINChangeDetector_-a_0.01).csv',
#         'SOKNL(FIRTDD)'],
#     ['meta.StreamingRandomPatches_-s_100_-l_(trees.FIMTDD_-s_VarianceReductionSplitCriterion_-g_50_-c_0.01_-e).csv',
#      'SRP(FIRTDD))'],
#     ['meta.StreamingRandomPatches_-T_-s_100_-l_(trees.FIMTDD_-s_VarianceReductionSplitCriterion_-g_50_-c_0.01_-e).csv',
#      'SRP_T(FIRTDD))'],
#     ['trees.FIMTDD_-s_VarianceReductionSplitCriterion_-g_50_-c_0.01_-e.csv', 'FIRTDD'],
#     [
#         'trees.HoeffdingAdaptiveRegressionTree_-k_-n_HoeffdingNumericAttributeClassObserver_-d_HoeffdingNominalAttributeClassObserver.csv',
#         'HTAR'],
#     [
#         'trees.HoeffdingRegressionTree_-k_-n_HoeffdingNumericAttributeClassObserver_-d_HoeffdingNominalAttributeClassObserver.csv',
#         'HTR'],
#     ['trees.StreamingGradientTreePredictor.csv', 'SGT'],
#     [
#         'meta.StreamingGradientBoostedTrees_-t_-L_1.0_-m_75_-s_100_-l_(trees.FIMTDD_-s_VarianceReductionSplitCriterion_-g_50_-c_0.01_-e).csv',
#         'SGBT(FIRTDD)'],
#     [
#         'meta.StreamingGradientBoostedTrees_-t_-L_1.0_-m_75_-s_100_-l_(trees.HoeffdingAdaptiveRegressionTree_-k_-n_HoeffdingNumericAttributeClassObserver_-d_HoeffdingNominalAttributeClassObserver).csv',
#         'SGBT(HTAR)'],
#     [
#         'meta.StreamingGradientBoostedTrees_-t_-L_1.0_-m_75_-s_100_-l_(trees.HoeffdingRegressionTree_-k_-n_HoeffdingNumericAttributeClassObserver_-d_HoeffdingNominalAttributeClassObserver).csv',
#         'SGBT(HTR)'],
#     ['meta.StreamingGradientBoostedTrees_-t_-L_1.0_-m_75_-s_100_-l_(trees.StreamingGradientTreePredictor).csv',
#      'SGBT(SGT)'],
# ]

row_order = [
    ['Oza(SGBT(FIRTDD)).csv', 'Oza(SGBT(FIRTDD))'],
    ['Oza_T(SGBT(FIRTDD)).csv', 'Oza_T(SGBT(FIRTDD))'],
    ['SRP(SGBT(FIRTDD)).csv', 'SRP(SGBT(FIRTDD))'],
    ['SRP_T(SGBT(FIRTDD)).csv', 'SRP_T(SGBT(FIRTDD))'],
    ['SGBT(Oza(FIRTDD)).csv', 'SGBT(Oza(FIRTDD))'],
    ['SGBT(Oza_T(FIRTDD)).csv', 'SGBT(Oza_T(FIRTDD))'],
    ['SGBT(ARFReg(FIRTDD)).csv', 'SGBT(ARFReg(FIRTDD))'],
    ['SGBT(SOKNL_noOp(FIRTDD)).csv', 'SGBT(SOKNL_noOp(FIRTDD))'],
    ['SGBT(SOKNL(FIRTDD)).csv', 'SGBT(SOKNL(FIRTDD))'],
    ['SGBT(SRP(FIRTDD)).csv', 'SGBT(SRP(FIRTDD))'],
    ['SGBT(SRP_T(FIRTDD)).csv', 'SGBT(SRP_T(FIRTDD))'],
    ['Oza(FIRTDD).csv', 'Oza(FIRTDD)'],
    ['Oza_T(FIRTDD).csv', 'Oza_T(FIRTDD)'],
    ['ARFReg(FIRTDD).csv', 'ARFReg(FIRTDD)'],
    ['SOKNL_noOp(FIRTDD).csv', 'SOKNL_noOp(FIRTDD)'],
    ['SOKNL(FIRTDD).csv', 'SOKNL(FIRTDD)'],
    ['SRP(FIRTDD).csv', 'SRP(FIRTDD)'],
    ['SRP_T(FIRTDD).csv', 'SRP_T(FIRTDD)'],
    ['FIRTDD.csv', 'FIRTDD'],
    ['HAT.csv', 'HAT'],
    ['HT.csv', 'HT'],
    ['SGT.csv', 'SGT'],
    ['SGBT(FIRTDD).csv', 'SGBT(FIRTDD)'],
    ['SGBT(HAT).csv', 'SGBT(HAT)'],
    ['SGBT(HT).csv', 'SGBT(HT)'],
    ['SGBT(SGT).csv', 'SGBT(SGT)'],
]

row_order = [
    ['Oza(SGBT(FIRTDD)).csv', '\\acrshort{ozasgbt}'],
    ['SRP(SGBT(FIRTDD)).csv', '\\acrshort{srpsgbt}'],
    ['SGBT(Oza(FIRTDD)).csv', '\\acrshort{sgbtoza}'],
    ['SGBT(ARFReg(FIRTDD)).csv', '\\acrshort{sgbtarf}'],
    ['SGBT(SRP(FIRTDD)).csv', '\\acrshort{sgbtsrp}'],
    ['SGBT(FIRTDD).csv', '\\acrshort{sgbt}'],
    ['AXGBr.csv', '\\acrshort{axgb}'],
    ['Oza(FIRTDD).csv', '\\acrshort{ozareg}'],
    ['ARFReg(FIRTDD).csv', '\\acrshort{arfreg}'],
    ['SOKNL(FIRTDD).csv', '\\acrshort{soknl}'],
    ['SRP(FIRTDD).csv', '\\acrshort{srpreg}'],
    ['FIRTDD.csv', '\\acrshort{firtdd}'],
    ['HT.csv', '\\acrshort{htr}'],
]

row_order = [
    ['Oza_1(SGBT_100).csv', '1,100'],
    ['Oza_2(SGBT_50).csv', '2,50'],
    ['Oza_4(SGBT_25).csv', '4,25'],
    ['Oza_5(SGBT_20).csv', '5,20'],
    ['Oza_10(SGBT_10).csv', '10,10'],
    ['Oza_20(SGBT_5).csv', '20,5'],
    ['Oza_25(SGBT_4).csv', '25,4'],
    ['Oza_50(SGBT_2).csv', '50,2'],
    ['Oza_100(SGBT_1).csv', '100,1'],
]

row_order = [
    ['SGBT_1(Oza_100).csv', '1,100'],
    ['SGBT_2(Oza_50).csv', '2,50'],
    ['SGBT_4(Oza_25).csv', '4,25'],
    ['SGBT_5(Oza_20).csv', '5,20'],
    ['SGBT_10(Oza_10).csv', '10,10'],
    ['SGBT_20(Oza_5).csv', '20,5'],
    ['SGBT_25(Oza_4).csv', '25,4'],
    ['SGBT_50(Oza_2).csv', '50,2'],
    ['SGBT_100(Oza_1).csv', '100,1'],
]

row_order = [
    ['SGBT_5(Oza_20).csv', '\\acrshort{sgbtoza}(5,20)'],
    ['SGBT_10(Oza_10).csv', '\\acrshort{sgbtoza}(10,10)'],
    ['SOKNL(FIRTDD).csv', '\\acrshort{soknl}'],
    ['Oza(FIRTDD).csv', '\\acrshort{ozareg}'],
    ['ARFReg(FIRTDD).csv', '\\acrshort{arfreg}'],
]

row_order = [
    ['Oza(SGBT(FIRTDD)).csv', '\\acrshort{ozasgbt}'],
    ['SGBT(Oza(FIRTDD)).csv', '\\acrshort{sgbtoza}'],
]

row_order = [
    ['SGBT_10_0.5_25(Oza_10).csv', '0.5,25'],
    ['SGBT_10_0.5_75(Oza_10).csv', '0.5,75'],
    ['SGBT_10_0.5_100(Oza_10).csv', '0.5,100'],
    ['SGBT_10_1.0_25(Oza_10).csv', '1.0,25'],
    ['SGBT_10_1.0_75(Oza_10).csv', '1.0,75'],
    ['SGBT_10_1.0_100(Oza_10).csv', '1.0,100'],
    ['SGBT_10_1.5_25(Oza_10).csv', '1.5,25'],
    ['SGBT_10_1.5_75(Oza_10).csv', '1.5,75'],
    ['SGBT_10_1.5_100(Oza_10).csv', '1.5,100'],
]

row_order = [
    ['Oza(SGBT(FIRTDD)).csv', '\\acrshort{ozasgbt}'],
    ['SRP(SGBT(FIRTDD)).csv', '\\acrshort{srpsgbt}'],
    ['SGBT(Oza(FIRTDD)).csv', '\\acrshort{sgbtoza}'],
    ['SGBT(ARFReg(FIRTDD)).csv', '\\acrshort{sgbtarf}'],
    ['SGBT(SRP(FIRTDD)).csv', '\\acrshort{sgbtsrp}'],
    ['SGBT(FIRTDD).csv', '\\acrshort{sgbt}'],
    ['AXGBr.csv', '\\acrshort{axgb}'],
    ['Oza(FIRTDD).csv', '\\acrshort{ozareg}'],
    ['ARFReg(FIRTDD).csv', '\\acrshort{arfreg}'],
    ['SOKNL(FIRTDD).csv', '\\acrshort{soknl}'],
    ['SRP(FIRTDD).csv', '\\acrshort{srpreg}'],
    ['FIRTDD.csv', '\\acrshort{firtdd}'],
    ['HT.csv', '\\acrshort{htr}'],
]

# row_order = [
#     ['FIRTDD.csv', '\\acrshort{firtdd}'],
#     ['HT.csv', '\\acrshort{htr}'],
#     ['SGT.csv', '\\acrshort{sgt}\\cite{pmlr-v101-gouk19a}'],
#     ['SGBT(FIRTDD).csv', '\\acrshort{sgbt}'],
# ]
#
# row_order = [
#     ["SGBT_1(Oza_100)", "Z",  "meta.StreamingGradientBoostedTrees -t -L 1.0 -m 75 -s 1 -l (meta.OzaBag -s 100 -l (trees.FIMTDD -s VarianceReductionSplitCriterion -g 50 -c 0.01 -e))"],
#     ["SGBT_2(Oza_50)", "Z",  "meta.StreamingGradientBoostedTrees -t -L 1.0 -m 75 -s 2 -l (meta.OzaBag -s 50 -l (trees.FIMTDD -s VarianceReductionSplitCriterion -g 50 -c 0.01 -e))"],
#     ["SGBT_4(Oza_25)", "Z",  "meta.StreamingGradientBoostedTrees -t -L 1.0 -m 75 -s 4 -l (meta.OzaBag -s 25 -l (trees.FIMTDD -s VarianceReductionSplitCriterion -g 50 -c 0.01 -e))"],
#     ["SGBT_5(Oza_20)", "Z",  "meta.StreamingGradientBoostedTrees -t -L 1.0 -m 75 -s 5 -l (meta.OzaBag -s 20 -l (trees.FIMTDD -s VarianceReductionSplitCriterion -g 50 -c 0.01 -e))"],
#     ["SGBT_10(Oza_10)", "Z",  "meta.StreamingGradientBoostedTrees -t -L 1.0 -m 75 -s 10 -l (meta.OzaBag -s 10 -l (trees.FIMTDD -s VarianceReductionSplitCriterion -g 50 -c 0.01 -e))"],
#     ["SGBT_20(Oza_5)", "Z",  "meta.StreamingGradientBoostedTrees -t -L 1.0 -m 75 -s 20 -l (meta.OzaBag -s 5 -l (trees.FIMTDD -s VarianceReductionSplitCriterion -g 50 -c 0.01 -e))"],
#     ["SGBT_25(Oza_4)", "Z",  "meta.StreamingGradientBoostedTrees -t -L 1.0 -m 75 -s 25 -l (meta.OzaBag -s 4 -l (trees.FIMTDD -s VarianceReductionSplitCriterion -g 50 -c 0.01 -e))"],
#     ["SGBT_50(Oza_2)", "Z",  "meta.StreamingGradientBoostedTrees -t -L 1.0 -m 75 -s 50 -l (meta.OzaBag -s 2 -l (trees.FIMTDD -s VarianceReductionSplitCriterion -g 50 -c 0.01 -e))"],
#     ["SGBT_100(Oza_1)", "Z",  "meta.StreamingGradientBoostedTrees -t -L 1.0 -m 75 -s 100 -l (meta.OzaBag -s 1 -l (trees.FIMTDD -s VarianceReductionSplitCriterion -g 50 -c 0.01 -e))"]
# ]
#
# row_order = [
#     ['SGBT_1(Oza_100)', '\\acrshort{sgbt}_100(\\acrshort{oza}_1)'],
#     ['SGBT_2(Oza_50)', '\\acrshort{sgbt}_50(\\acrshort{oza}_2)'],
#     ['SGBT_4(Oza_25)', '\\acrshort{sgbt}_25(\\acrshort{oza}_4)'],
#     ['SGBT_5(Oza_20)', '\\acrshort{sgbt}_20(\\acrshort{oza}_5)'],
#     ['SGBT_10(Oza_10)', '\\acrshort{sgbt}_10(\\acrshort{oza}_10)'],
#     ['SGBT_20(Oza_5)', '\\acrshort{sgbt}_5(\\acrshort{oza}_20)'],
#     ['SGBT_25(Oza_4)', '\\acrshort{sgbt}_4(\\acrshort{oza}_25)'],
#     ['SGBT_50(Oza_2)', '\\acrshort{sgbt}_2(\\acrshort{oza}_50)'],
#     ['SGBT_100(Oza_1)', '\\acrshort{sgbt}_1(\\acrshort{oza}_100)']
# ]

PRINT_STD = True

def get_matching_index(item_to_find):
    for idx, item in enumerate(row_order):
        if item[0] == item_to_find:
            return idx + 10, item[1]
    return 100, item_to_find


def get_raw_id(s: str, learner_string: str):
    skip_csv = False
    id, label = get_matching_index(learner_string)
    # label = learner_string
    return id, label, skip_csv


def add_ranks(df: pd.DataFrame, skip_cols, ascending: bool):
    cols = df.columns.copy()
    value_cols = []
    rank_cols = []
    for c in cols:
        if c not in skip_cols:
            value_cols.append(c)
            rank_cols.append(c + '_rank')
            df[c + '_rank'] = df[c].rank(ascending=ascending)
    return rank_cols, value_cols, df


csv_files = []
if len(csv_files) == 0:
    matching_files = glob.glob(f"{args.resultsDir}/**/*.csv", recursive=True)
    for full_file_name in matching_files:
        id, label = get_matching_index(full_file_name.split('/')[-1])
        if id == 100:
            pass
        else:
            csv_files.append(full_file_name)

    # command = subprocess.Popen("find -L " + args.resultsDir + " -iname '*.csv'",
    #                            shell=True, stdout=subprocess.PIPE)
    # for line in command.stdout.readlines():
    #     file_name = line.decode("utf-8").replace('\n', '')
    #     id, label = get_matching_index(file_name.split('/')[-1])
    #     if id == 100:
    #         pass
    #     else:
    #         csv_files.append(file_name)

pattern = re.compile(r'_' + random_seed_option + '_\d+')

df_final = None
for f in csv_files:
    if os.stat(f).st_size == 0:
        print('WARNING: ZERO size file: {}'.format(f))
        continue
    df = pd.read_csv(f)

    if df_final is None:
        columns = [c.lstrip() for c in df.columns]
        df_final = pd.DataFrame(columns=columns)

    dataset_name = f.split('/')[-2]
    learner_cmd = f.split('/')[-1]

    df['Learner'] = learner_cmd = re.sub(pattern, '', learner_cmd)

    raw_id, raw_label, skip = get_raw_id(f, df.iloc[0]['Learner'])

    if skip:
        continue
    # print('{} : {}'.format(f, raw_id))
    df['raw_id'] = str(raw_id)
    df['method'] = str(raw_label)
    df['stream'] = dataset_name

    df_final = pd.concat([df_final, df], ignore_index=True)


def highlight_max(s, props='color:red;'):
    return np.where(s == np.nanmax(s.values), props, '')


def highlight_min(s, props='color:red;'):
    return np.where(s == np.nanmin(s.values), props, '')


index_cols = ['raw_id', 'method']
for pv_key, pv_table_data in pv_table_values.items():
    try:
        pd_avg = pd.pivot_table(
            df_final, values=pv_key, index=index_cols, columns=['stream'], aggfunc=np.mean, fill_value=0)
    except:
        print('Hi')
    pd_avg = pd_avg[column_order]
    pd_avg = pd_avg.sort_values(by='raw_id', ascending=1)
    rank_cols, value_cols, pd_avg = add_ranks(pd_avg, index_cols, ascending=pv_table_values[pv_key]['ascending'])
    new_col_name = f"avg"
    pd_avg[new_col_name] = pd_avg[value_cols].mean(axis=1).round(pv_table_values[pv_key]['decimal_places'])
    new_col_name = f"avgRank"
    pd_avg[new_col_name] = pd_avg[rank_cols].mean(axis=1).round(pv_table_values[pv_key]['decimal_places'])
    pd_avg = pd_avg.round(pv_table_values[pv_key]['decimal_places'])
    pv_table_data['avg'] = pd_avg

    pd_std = pd.pivot_table(
        df_final, values=pv_key, index=index_cols, columns=['stream'], aggfunc=np.std, fill_value=0)
    if pd_std.shape[0] > 0:
        pd_std = pd_std[column_order]
    # pd_std = pd_std.sort_values(by ='Learner', ascending = 1)
    pd_std = pd_std.sort_values(by='raw_id', ascending=1)
    std_for_all_datasets = pd.pivot_table(df_final, values=pv_key, index=index_cols, columns=[], aggfunc=np.std, fill_value=0)
    pd_std[f"for_all"] = std_for_all_datasets.round(pv_table_values[pv_key]['decimal_places'])
    pd_std.rename(columns={f'{c}': f'std_{c}' for c in pd_std.columns}, inplace=True)
    pv_table_data['std'] = pd_std
    # pv_table_data['std'] = pd_std.round(pv_table_values[pv_key]['decimal_places'])

    pd_count = pd.pivot_table(
        df_final, values=pv_key, index=index_cols, columns=['stream'], aggfunc=np.count_nonzero, fill_value=0)
    pd_count = pd_count[column_order]
    # pd_count = pd_count.sort_values(by ='Learner', ascending = 1)
    pd_count = pd_count.sort_values(by='raw_id', ascending=1)
    pv_table_data['count'] = pd_count

new_col_order = []
for c in column_order:
    new_col_order.append(c)
    new_col_order.append(f'std_{c}')


def print_cell(df, idx, col, h_min, print_std=True, end_str=" & ", d=1):
    if h_min:
        best_d_idx = df[col].idxmin()
    else:
        best_d_idx = df[col].idxmax()

    value = df.at[idx, col]
    if value > 1000 or value < -100:
        value = f"{value:.1e}"  # Scientific notation with 1 decimal places
    else:
        value = f"{value:.{d}f}" # Fixed-point with d decimal places

    std = ' '
    if print_std:
        std = df.at[idx, f'std_{col}']
        if std > 1000:
            std = f"{std:.1e}"  # Scientific notation with 1 decimal places
        else:
            std = f"{std:.{d}f}" # Fixed-point with d decimal places
        std = f' $\\pm$ {std}'

    if best_d_idx == idx:
        print(f"\\textbf{{ {value} }}{std}", end=end_str)
    else:
        print(f"{value}{std}", end=end_str)


def print_df(df, datasets, t_info, print_std):
    # Print column headers
    avg_colm = f"avg"
    rank_colm = f"avgRank"

    print("\\begin{tabular}{l|", end="")
    for col in datasets:
        print(f"c", end="")
    print("|c|c}", end="")

    print()
    print('\\toprule')

    print("method", end=" & ")
    for col in datasets:
        print(f"{col}", end=" & ")
    print(f"\\textbf{{{avg_colm}}}", end=" & ")
    print(f"\\textbf{{{rank_colm}}}", end=" \\\\ ")
    print()
    print('\\midrule')

    if t_info['ascending']:
        h_min = True
    else:
        h_min = False

    # Print each row with row index and cell values
    for idx in df.index:
        print(f"{idx[1]} ", end=" & ")
        for d in datasets:
            print_cell(df, idx, d, h_min, print_std=print_std, end_str=" & ", d=t_info['decimal_places'])
        print_cell(df, idx, avg_colm, h_min, print_std=False, end_str=" & ", d=t_info['decimal_places'])
        print_cell(df, idx, rank_colm, True, print_std=False, end_str=" \\\\ ")
        print()
    print('\\bottomrule')
    print('\end{tabular} %')

with pd.ExcelWriter(args.resultsDir + '/Results_' + '.xlsx', engine='openpyxl') as writer:
    for pv_key, pv_table_data in pv_table_values.items():
        avg_col = f"avg"
        rank_col = f"avgRank"
        func = highlight_min if pv_table_values[pv_key]['ascending'] else highlight_max

        pv_table_data['avg'].style. \
            apply(lambda x: func(x), subset=column_order, axis=0). \
            apply(lambda x: func(x), subset=[avg_col], axis=0). \
            apply(lambda x: highlight_min(x), subset=[rank_col], axis=0). \
            to_excel(writer, sheet_name='Avg ' + pv_table_data['name'], index=True)

        if pv_table_data['std'].shape[0] > 0:
            tmp_cols = [c for c in new_col_order]
            tmp_cols.append(avg_col)
            tmp_cols.append(rank_col)
            tmp_cols.append("std_for_all")
            pv_table_data['std'].to_excel(writer, sheet_name='Std ' + pv_table_data['name'], index=True)
            pd_concat = pd.concat([pv_table_data['avg'], pv_table_data['std']], axis=1, ignore_index=False)

            print(pd_concat.shape)
            print_df(pd_concat, column_order, pv_table_values[pv_key], PRINT_STD)
            pd_concat[tmp_cols].style. \
                apply(lambda x: func(x), subset=column_order, axis=0). \
                apply(lambda x: func(x), subset=[avg_col], axis=0). \
                apply(lambda x: highlight_min(x), subset=[rank_col], axis=0). \
                to_excel(writer, sheet_name='avg std' + pv_table_data['name'], index=True)
            # print(pd_concat[tmp_cols].style.apply(lambda x: func(x), subset=column_order, axis=0).to_latex())
        pv_table_data['count'].to_excel(writer, sheet_name='Count ' + pv_table_data['name'], index=True)
    df_final.to_excel(writer, sheet_name='RawData', index=True)
