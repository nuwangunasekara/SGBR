import os
import shutil

# Usage:
#
#     Place this script in the topmost directory containing the subdirectories 1, 2, 3, 4, 5.
#     Run the script. It will move the specified folders from each subdirectory to the topmost directory with the appropriate postfix.


# Define the topmost directory
from_dir = './output'
to_dir = './post_hoc_new'

# List of subdirectories
random_seeds = ['1', '2', '3', '4', '5']

# List of folders to move
datasets_to_copy = [
    'FriedmanGra', 'FriedmanGsg', 'FriedmanLea', 'House8L', 'MetroTraffic',
    'abalone', 'ailerons', 'bike', 'elevators', 'fried', 'hyperA'
]

datasets_to_copy = [
    'FriedmanGra', 'FriedmanGsg', 'FriedmanLea', 'House8L', 'MetroTraffic',
    'abalone', 'ailerons', 'bike', 'elevators', 'fried', 'hyperA', 'DemandF', 'NZEnergy', 'SUP2I', 'SUP3A', 'SUP3G'
]

algo_to_copy = [
    ['Oza(SGBT(FIRTDD)).csv', 'Oza(SGBT).csv'],
    ['SGBT(Oza(FIRTDD)).csv', 'SGBT(Oza).csv'],
    ['SGBT(ARFReg(FIRTDD)).csv', 'SGBT(ARF).csv'],
    ['Oza(FIRTDD).csv', 'OzaReg.csv'],
    ['ARFReg(FIRTDD).csv', 'ARFReg.csv'],
    ['SOKNL(FIRTDD).csv', 'SOKNL.csv'],
]


# row_order = [
#     ['Oza(SGBT(FIRTDD)).csv', '\\acrshort{ozasgbt}'],
#     ['SRP(SGBT(FIRTDD)).csv', '\\acrshort{srpsgbt}'],
#     ['SGBT(Oza(FIRTDD)).csv', '\\acrshort{sgbtoza}'],
#     ['SGBT(ARFReg(FIRTDD)).csv', '\\acrshort{sgbtarf}'],
#     ['SGBT(SRP(FIRTDD)).csv', '\\acrshort{sgbtsrp}'],
#     ['SGBT(FIRTDD).csv', '\\acrshort{sgbt}'],
#     ['AXGBr.csv', '\\acrshort{axgb}'],
#     ['Oza(FIRTDD).csv', '\\acrshort{ozareg}'],
#     ['ARFReg(FIRTDD).csv', '\\acrshort{arfreg}'],
#     ['SOKNL(FIRTDD).csv', '\\acrshort{soknl}'],
#     ['SRP(FIRTDD).csv', '\\acrshort{srpreg}'],
#     ['FIRTDD.csv', '\\acrshort{firtdd}'],
#     ['HT.csv', '\\acrshort{htr}'],
# ]

# Iterate over each subdirectory
for r in random_seeds:
    r_dir_path = os.path.join(from_dir, r)

    # Check if the subdirectory exists
    if os.path.exists(r_dir_path) and os.path.isdir(r_dir_path):
        # Iterate over each folder to move
        for d in datasets_to_copy:
            original_folder_path = os.path.join(r_dir_path, d)
            new_folder_name = f"{d}_{r}"
            new_folder_path = os.path.join(to_dir, new_folder_name)

            # Create new dir
            os.makedirs(new_folder_path, exist_ok=True)
            for algo in algo_to_copy:
                exp_file = os.path.join(original_folder_path, algo[0])
                if os.path.exists(exp_file) and os.stat(exp_file).st_size > 0:
                    new_exp_file = os.path.join(new_folder_path, algo[1])
                    shutil.copy(exp_file, new_exp_file)
            # copy selected files in original_folder_path to new_folder_path with a given name

            # if os.path.exists(original_folder_path) and os.path.isdir(original_folder_path):
            #     # Move the folder to the topmost directory with the new name
            #     shutil.move(original_folder_path, new_folder_path)
            #     print(f"Moved: {original_folder_path} -> {new_folder_path}")
            # else:
            #     print(f"Folder does not exist: {original_folder_path}")

print("All folders have been copied.")
