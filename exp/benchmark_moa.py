import json
import os
import csv
import threading
import time
import subprocess
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-f", "--jason_config", type=str, help="jason config file", default=None)
args = parser.parse_args()

exp_config_str = '{'\
                 '"moa_jar": "./moa.jar",'\
                 '"java_options":"-Xmx96g -Xms50m -Xss1g moa.DoTask",'\
                 '"output_dir":"./output/",'\
                 '"evaluator": "EvaluatePrequentialRegression -e BasicRegressionPerformanceEvaluator",'\
                 '"dataset_dir":"./RDatasets/",'\
                 '"datasets":["House8L","MetroTraffic"],'\
                 '"streams": {"<dataset_name>": "stream_command","random_seed_options": ["-r"]},'\
                 '"random_seeds": [1],'\
                 '"learners":['\
                 '  ["name1", "random_seed_option", "command1"],'\
                 '  ["FIRTDD", "",  "trees.FIMTDD -s VarianceReductionSplitCriterion -g 50 -c 0.01 -e"],'\
                 '  ["HAT", "",  "trees.HoeffdingAdaptiveRegressionTree -k -n HoeffdingNumericAttributeClassObserver -d HoeffdingNominalAttributeClassObserver"],'\
                 '  ["HT", "",  "trees.HoeffdingRegressionTree -k -n HoeffdingNumericAttributeClassObserver -d HoeffdingNominalAttributeClassObserver"],'\
                 '  ["SGT", "",  "trees.StreamingGradientTreePredictor"]'\
                 ']'\
                 '}'

def stream_to_file(stream, file):
    with open(file, 'a') as f:
        while True:
            line = stream.readline()
            if not line:
                break
            f.write(line.decode())
            f.flush()

def execute_command(command, logfile):
    start_time = time.time()
    start_cpu_time = time.process_time()

    # process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # _, _ = process.communicate()

    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # File paths to write the outputs
    stdout_file = logfile + '.stdout'
    stderr_file = logfile + '.stderr'
    if os.path.exists(stdout_file):
        os.remove(stdout_file)
    if os.path.exists(stderr_file):
        os.remove(stderr_file)

    # Create threads to read stdout and stderr in real-time
    stdout_thread = threading.Thread(target=stream_to_file, args=(process.stdout, stdout_file))
    stderr_thread = threading.Thread(target=stream_to_file, args=(process.stderr, stderr_file))

    # Start the threads
    stdout_thread.start()
    stderr_thread.start()

    # Wait for the process to complete
    process.wait()

    # Wait for the threads to complete
    stdout_thread.join()
    stderr_thread.join()

    end_time = time.time()
    end_cpu_time = time.process_time()

    wallclock_time = end_time - start_time
    cpu_time = end_cpu_time - start_cpu_time

    return wallclock_time, cpu_time


def get_n_th_line(file, n=2):
    if os.path.exists(file):
        with open(file, 'r') as f:
            lines = f.readlines()
            i = 0
            for line in lines:
                i += 1
                if i == n:
                    return line.strip()
    return None


def main(exp_config_file = None):
    if exp_config_file is not None:
        with open(exp_config_file, "r") as json_file:
            exp = json.load(json_file)
    else:
        exp = json.loads(exp_config_str)

    output_dir = exp['output_dir']
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    final_results_file = os.path.join(output_dir, 'final_results.csv')
    with open(final_results_file, 'a', newline='') as final_results_csv:
        write_header = True
        header_line_from_1st_valid_csv = None
        header = 'learner, dataset, wallclock, cpu_time'

        moa_jar_path = os.path.realpath(exp['moa_jar'])
        java_command = f"java -classpath {moa_jar_path} {exp['java_options']} "
        evaluator = exp['evaluator']

        for random_seed in exp['random_seeds']:
            for dataset_idx, dataset in enumerate(exp['datasets']):
                if dataset in exp['streams']:
                    # generate stream command
                    pass
                else:
                    dataset_dir = os.path.realpath(exp['dataset_dir'])
                    dataset_path = os.path.join(dataset_dir, dataset + '.arff')
                    stream_command = f'ArffFileStream -f {dataset_path}'

                output_dir = os.path.join(exp['output_dir'], f'{random_seed}/{dataset}')
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)

                for learner in exp['learners']:
                    learner_name = learner[0]
                    learner_random_seed_option = learner[1]
                    learner_cmd_str = learner[2]

                    if len(learner_random_seed_option) > 0:
                        learner_cmd = learner_cmd_str + f' -{learner_random_seed_option} {random_seed}'
                    else:
                        learner_cmd = learner_cmd_str

                    output_file = os.path.join(output_dir, f'{learner_name}.csv')

                    if os.path.exists(output_file):
                        os.remove(output_file)

                    command = f'{java_command} "{evaluator} -s ({stream_command}) -l ({learner_cmd}) -d {output_file}"'
                    print('Running command:', command)
                    wallclock_time, cpu_time = execute_command(command, output_file.replace('.csv', ''))

                    if write_header:
                        header_line_from_1st_valid_csv = get_n_th_line(output_file, n=1)
                        if header_line_from_1st_valid_csv is not None:  # valid header is available
                            header = f'{header}, {header_line_from_1st_valid_csv}'
                            print(header, file=final_results_csv, flush=True)
                            write_header = False

                    write_results = True
                    line_2_from_csv = get_n_th_line(output_file, n=2)
                    if line_2_from_csv is None:  # experiment seems to have failed. write '' for all columns
                        if header_line_from_1st_valid_csv is not None:
                            line_2_from_csv = ', '.join(['' for _ in header_line_from_1st_valid_csv.split(',')])
                        else:
                            write_results = False
                    if write_results:
                        row = f'{learner_name}, {dataset}, {wallclock_time}, {cpu_time}, {line_2_from_csv}'
                        print(row, file=final_results_csv, flush=True)


if __name__ == "__main__":
    main(args.jason_config)
