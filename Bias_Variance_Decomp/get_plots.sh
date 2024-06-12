dd=('House8L' 'MetroTraffic' 'abalone' 'ailerons' 'bike' 'elevators' 'fried' 'FriedmanGra' 'FriedmanGsg' 'FriedmanLea')
for dataset in "${dd[@]}"; do
#  echo "Processing $dataset"
  python plotBVDecompose.py -d ${dataset} &
done