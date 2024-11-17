package moa.classifiers.meta;

import com.github.javacliparser.FlagOption;
import com.github.javacliparser.FloatOption;
import com.github.javacliparser.IntOption;
import com.github.javacliparser.MultiChoiceOption;
import moa.capabilities.Capabilities;
import moa.classifiers.AbstractClassifier;
import moa.classifiers.MultiClassClassifier;
import moa.classifiers.Regressor;
import moa.core.Utils;
import com.yahoo.labs.samoa.instances.Instance;
import moa.core.Measurement;
import moa.classifiers.core.driftdetection.ADWIN;
import ml.dmlc.xgboost4j.java.*;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;

public class AdaptiveXGBoostClassifier extends AbstractClassifier implements MultiClassClassifier, Regressor {
    private static final long serialVersionUID = 1L;

    public IntOption nEstimators = new IntOption("nEstimators", 's', "The number of models.", 30, 1, Integer.MAX_VALUE);
    public FloatOption learningRate = new FloatOption("learningRate", 'L', "Learning rate", 0.3f, 0, 1.00);
    public IntOption maxDepth = new IntOption("maxDepth", 'd', "Maximum Depth for a given tree.", 6, 1, Integer.MAX_VALUE);
    public IntOption maxWindowSize = new IntOption("maxWindowSize", 'M', "Maximum window size", 1000, 1, Integer.MAX_VALUE);
    public IntOption minWindowSize = new IntOption("minWindowSize", 'm', "Minimum window size", 1, 1, Integer.MAX_VALUE);
    public FlagOption detectDrift = new FlagOption("detectDrift", 'D', "Detect and adjust to drifts");
    public FlagOption useSquardError = new FlagOption("useSquardError", 'e', "useSquardError");

    public static final int updateStrategyReplace = 0;
    public static final int updateStrategyPush = 1;
    public MultiChoiceOption updateStrategy = new MultiChoiceOption("updateStrategy", 'u',
            "Ensemble update strategy",
            new String[]{"Replace","Push"},
            new String[]{"Replace old", "Push out old when ensemble is full and append at the end"},
            updateStrategyReplace);

    public IntOption randomSeedOption = new IntOption("randomSeed", 'Z', "The random seed", 1);

    private Booster[] ensemble;
    private int windowSize = 0;
    private ADWIN adwin = new ADWIN();
    private double sumOfErrors = 0;
    private double sumOfSquaredErrors = 0;
    private int samplesSeenAtTrain = 0;
    private ArrayList<float[]> XBuffer = new ArrayList<>();
    private ArrayList<Float> yBuffer = new ArrayList<>();
    private int latestIndex = 0;
    private String objective;
    private int numClasses = 0;
    private boolean ensembleFull = false;


    @Override
    public void resetLearningImpl() {
        ensemble = new Booster[nEstimators.getValue()];
        XBuffer.clear();
        yBuffer.clear();
        samplesSeenAtTrain = 0;
        sumOfErrors = 0;
        sumOfSquaredErrors = 0;
        windowSize = minWindowSize.getValue();
        latestIndex = 0;
        ensembleFull = false;
    }

    public static DMatrix createDMatrixFromLists(ArrayList<float[]> featureList, ArrayList<Float> labelList) throws XGBoostError {
        // Number of rows (instances) and columns (features)
        int numRows = featureList.size();
        int numCols = featureList.get(0).length;

        // Flatten the feature list into a single array
        float[] flatFeatureArray = new float[numRows * numCols];
        for (int i = 0; i < numRows; i++) {
            System.arraycopy(featureList.get(i), 0, flatFeatureArray, i * numCols, numCols);
        }

        // Convert labelList to an array
        float[] labelArray = new float[labelList.size()];
        for (int i = 0; i < labelList.size(); i++) {
            labelArray[i] = labelList.get(i);
        }

        // Create DMatrix from the flattened feature array
        DMatrix dMatrix = new DMatrix(flatFeatureArray, numRows, numCols, 0.0f);

        // Set labels to DMatrix
        dMatrix.setLabel(labelArray);

        return dMatrix;
    }

    private void printIndexes(ArrayList<Integer> indexes){
        System.out.print(indexes.size() + ": ");
        for (int i = 0; i < indexes.size(); i++){
            System.out.print(indexes.get(i) + " ");
        }
        System.out.println(" latestIndex = "+ latestIndex);
    }


    private ArrayList<Integer> getValidIndexesInOrder(){
//        from oldest to latest last
        int validEstimators = 0;
        ArrayList<Integer> indexes = new ArrayList<>();

        for (int i=0; i< ensemble.length; i++) {
            if (ensemble[i] != null) {
                validEstimators++;
                indexes.add(i);
            }
        }

        if ((validEstimators < ensemble.length)){
            return indexes;
        }else {
            if ((validEstimators == ensemble.length) && !ensembleFull){
                ensembleFull = true;
                return indexes;
            }
        }
//      Full
        indexes = new ArrayList<>();
        if (updateStrategy.getChosenIndex() == updateStrategyReplace){
            int i = (latestIndex + 1) % ensemble.length;
            for (; i != latestIndex;  i = (i + 1) % ensemble.length) {
                if (ensemble[i] != null){
                    indexes.add(i);
                }
            }
            indexes.add(latestIndex);
        }else{ // push
            for (int i = 0; i < ensemble.length; i++) {
                if (ensemble[i] != null){
                    indexes.add(i);
                }
            }
        }
        return indexes;
    }

    private void trainOnMiniBatch() {
        try {
            DMatrix trainData = createDMatrixFromLists(XBuffer, yBuffer);
            int newIndex = 0;
            ArrayList<Integer> indexes = getValidIndexesInOrder();
            if (indexes.size() > 0) {
                if (updateStrategy.getChosenIndex() == updateStrategyPush) {
                    if (indexes.size() == ensemble.length){ //full
                        indexes.remove(0);
                        newIndex = ensemble.length -1;
                    }else{ // not full
                        newIndex = indexes.get(indexes.size()-1) +1;
                    }
                } else { // replace
                    if (indexes.size() == ensemble.length) { //full
                        newIndex = indexes.get(0);
                        indexes.remove(0);
                    }else{// not full
                        newIndex = indexes.get(indexes.size()-1) +1;
                    }
                }
            }

            for (Integer b : indexes){
                float[][] margins = ensemble[b].predict(trainData, true);
                // Set base margin for the training data
                trainData.setBaseMargin(margins);
            }

            // Set up booster parameters
            Booster booster = XGBoost.train(trainData, getParams(), 10, new HashMap<>(), null, null);

            ensemble[newIndex] = booster;
            latestIndex = newIndex;

            XBuffer.clear();
            yBuffer.clear();
        } catch (XGBoostError e) {
            e.printStackTrace();
        }
    }

    @Override
    public void trainOnInstanceImpl(Instance instance) {
        if (samplesSeenAtTrain == 0) {
            objective = instance.classAttribute().isNumeric() ? "reg:squarederror" :
                    instance.numClasses() > 2 ? "multi:softmax": "binary:logistic";
            numClasses = instance.numClasses();;
        }
        samplesSeenAtTrain++;

        float[] X = new float[instance.numAttributes() - 1];
        for (int i = 0; i < X.length; i++) {
            X[i] = (float) instance.value(i);
        }
        float y = (float) instance.classValue();

        // Buffer the instance
        XBuffer.add(X);
        yBuffer.add(y);

        // When buffer is full, train a mini-batch
        if (XBuffer.size() >= windowSize) {
            trainOnMiniBatch();
        }

        //  adjustWindowSize
        windowSize = Math.min(minWindowSize.getValue() * (int) Math.pow(2.0, samplesSeenAtTrain), maxWindowSize.getValue());

        if (detectDrift.isSet()) {
            double error =
                    instance.classAttribute().isNumeric() ? getError(y, this.getVotesForInstance(instance)[0], useSquardError.isSet()) : // normalized/ regression error
                    (Utils.maxIndex(this.getVotesForInstance(instance)) == (int) instance.classValue() ? 0.0 : 1.0); // zero-one error for classification
            adwin.setInput(error);

            if (adwin.getChange()) {
                resetLearningImpl();
                // reset window to Minimum
                // train new member based on strategy
            }
        }
    }

    @Override
    public double[] getVotesForInstance(Instance instance) {
        double[] votes = new double[instance.classAttribute().isNominal() ? instance.numClasses(): 1];
        if (samplesSeenAtTrain == 0) {
            return votes;
        }


        float[] X = new float[instance.numAttributes() - 1];
        for (int i = 0; i < X.length; i++) {
            X[i] = (float) instance.value(i);
        }

        try {
            DMatrix testData = new DMatrix(X, 1, X.length, 0.0f);

            ArrayList<Integer> indexes = getValidIndexesInOrder();

//            printIndexes(indexes);

            for (int j=0; j < indexes.size() -1; j++){
                float[][] margins = ensemble[indexes.get(j)].predict(testData, true);
                // Set base margin for the training data
                testData.setBaseMargin(margins);
            }
            if (indexes.size()> 0) {
                float[][] prediction = ensemble[indexes.get(indexes.size() - 1)].predict(testData);

                if (instance.classAttribute().isNominal()) { // classification
                    if (instance.numClasses() == 2) { // binary class
                        votes[0] = 1.0 - prediction[0][0];
                        votes[1] = prediction[0][0];
                    }else{ // multi class
                        for (int i = 0; i < prediction.length; i++) {
                            votes[i] = prediction[0][i];
                        }
                    }
                }else{ // regression
                    votes[0] = prediction[0][0];
                }



            }

        } catch (XGBoostError e) {
            e.printStackTrace();
        }

        return votes;
    }

    private double getError(double trueValue, double prediction, boolean useSquaredError) {
        if (useSquaredError){
            double error = trueValue - prediction;
            return error * error;
        }else { // get normalized absolute error
            double absoluteError = Math.abs(trueValue - prediction);
            sumOfErrors += absoluteError;
            sumOfSquaredErrors += absoluteError * absoluteError;

            double mean = sumOfErrors / samplesSeenAtTrain;
            double std = Math.sqrt((sumOfSquaredErrors - ((sumOfErrors * sumOfErrors) / samplesSeenAtTrain)) / samplesSeenAtTrain);
            double normalizedError = (absoluteError - mean) / (3 * std);
            return normalizedError;
        }
    }

    private Map<String, Object> getParams() {
        Map<String, Object> params = new HashMap<>();
        params.put("eta", learningRate.getValue());
        params.put("max_depth", maxDepth.getValue());
        params.put("silent", 1);
        params.put("objective", objective);
        if (numClasses> 2) {
            params.put("num_class", numClasses);
        }
        params.put("seed", randomSeedOption.getValue());
        return params;
    }

    @Override
    public boolean isRandomizable() {
        return false;
    }

    @Override
    public void getModelDescription(StringBuilder out, int indent) {
        out.append("AdaptiveXGBoost Classifier\n");
    }

    @Override
    protected Measurement[] getModelMeasurementsImpl() {
        return null;
    }

    @Override
    public Capabilities getCapabilities() {
        return super.getCapabilities();
    }
}
