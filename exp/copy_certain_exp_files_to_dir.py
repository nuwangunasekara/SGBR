import os
import shutil

def find_and_copy_files(src_dir, dst_dir, file_name):
    for root, dirs, files in os.walk(src_dir):
        if file_name in files:
            # Construct the full source file path
            src_file_path = os.path.join(root, file_name)

            # Create the destination directory structure
            relative_path = os.path.relpath(root, src_dir)
            dest_folder_path = os.path.join(dst_dir, relative_path)
            # print(f'MKDIR: {dest_folder_path}')
            os.makedirs(dest_folder_path, exist_ok=True)

            # Construct the full destination file path
            dest_file_path = os.path.join(dest_folder_path, file_name)

            # Copy the file to the new destination path
            shutil.copy2(src_file_path, dest_file_path)
            print(f"Copied {src_file_path} to {dest_file_path}")

# Usage
source_directory = './output_baseline_comparision'
destination_directory = './output_SGBT_5(OZA 20)_with_best_baseline_comparision'

find_and_copy_files('./output_baseline_comparision', destination_directory, 'SOKNL(FIRTDD).csv')
find_and_copy_files('./output_baseline_comparision', destination_directory, 'Oza(FIRTDD).csv')
find_and_copy_files('./output_baseline_comparision', destination_directory, 'ARFReg(FIRTDD).csv')
find_and_copy_files('./output_sgbt_oza_para_search', destination_directory, 'SGBT_5(Oza_20).csv')
find_and_copy_files('./output_sgbt_oza_para_search', destination_directory, 'SGBT_10(Oza_10).csv')

