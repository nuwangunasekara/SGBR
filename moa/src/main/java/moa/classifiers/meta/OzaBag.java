/*
 *    OzaBag.java
 *    Copyright (C) 2007 University of Waikato, Hamilton, New Zealand
 *    @author Richard Kirkby (rkirkby@cs.waikato.ac.nz)
 *
 *    This program is free software; you can redistribute it and/or modify
 *    it under the terms of the GNU General Public License as published by
 *    the Free Software Foundation; either version 3 of the License, or
 *    (at your option) any later version.
 *
 *    This program is distributed in the hope that it will be useful,
 *    but WITHOUT ANY WARRANTY; without even the implied warranty of
 *    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *    GNU General Public License for more details.
 *
 *    You should have received a copy of the GNU General Public License
 *    along with this program. If not, see <http://www.gnu.org/licenses/>.
 *    
 */
package moa.classifiers.meta;

import com.github.javacliparser.FlagOption;
import com.github.javacliparser.FloatOption;
import moa.capabilities.CapabilitiesHandler;
import moa.capabilities.Capability;
import moa.capabilities.ImmutableCapabilities;
import moa.classifiers.AbstractClassifier;
import moa.classifiers.Classifier;
import com.yahoo.labs.samoa.instances.Instance;

import moa.classifiers.MultiClassClassifier;
import moa.classifiers.Regressor;
import moa.core.*;
import moa.evaluation.WindowRegressionPerformanceEvaluator;
import moa.options.ClassOption;
import com.github.javacliparser.IntOption;

import java.util.*;
import java.util.stream.IntStream;

/**
 * Incremental on-line bagging of Oza and Russell.
 *
 * <p>Oza and Russell developed online versions of bagging and boosting for
 * Data Streams. They show how the process of sampling bootstrap replicates
 * from training data can be simulated in a data stream context. They observe
 * that the probability that any individual example will be chosen for a
 * replicate tends to a Poisson(1) distribution.</p>
 *
 * <p>[OR] N. Oza and S. Russell. Online bagging and boosting.
 * In Artiﬁcial Intelligence and Statistics 2001, pages 105–112.
 * Morgan Kaufmann, 2001.</p>
 *
 * <p>Parameters:</p> <ul>
 * <li>-l : Classiﬁer to train</li>
 * <li>-s : The number of models in the bag</li> </ul>
 *
 * @author Richard Kirkby (rkirkby@cs.waikato.ac.nz)
 * @version $Revision: 7 $
 */
public class OzaBag extends AbstractClassifier implements MultiClassClassifier, Regressor,
                                                          CapabilitiesHandler {

    @Override
    public String getPurposeString() {
        return "Incremental on-line bagging of Oza and Russell.";
    }
        
    private static final long serialVersionUID = 1L;

    public ClassOption baseLearnerOption = new ClassOption("baseLearner", 'l',
            "Classifier to train.", Classifier.class, "trees.HoeffdingTree");

    public IntOption ensembleSizeOption = new IntOption("ensembleSize", 's',
            "The number of models in the bag.", 10, 1, Integer.MAX_VALUE);

    public IntOption randomSeedOption = new IntOption("randomSeed", 'Z', "The random seed", 1);

    public FlagOption parallelTrain = new FlagOption("parallelTrain", 'T', "Parallel train");

    public FloatOption usePercentageOfLearnersForPrediction = new FloatOption("usePercentageOfLearnersForPrediction", 'p',
            "Use best performing top p percent", 1.0, 0.1, 1.0);

    protected Classifier[] ensemble;
    protected WindowRegressionPerformanceEvaluator[] evaluators;
    private boolean canUseBestPerforming = false;

    @Override
    public void resetLearningImpl() {
        this.classifierRandom = new Random(randomSeedOption.getValue());
        this.ensemble = new Classifier[this.ensembleSizeOption.getValue()];
        this.evaluators = new WindowRegressionPerformanceEvaluator[this.ensembleSizeOption.getValue()];
        Classifier baseLearner = (Classifier) getPreparedClassOption(this.baseLearnerOption);
        baseLearner.resetLearning();
        for (int i = 0; i < this.ensemble.length; i++) {
            this.ensemble[i] = baseLearner.copy();
            this.evaluators[i] = new WindowRegressionPerformanceEvaluator();
        }
    }

    public static void trainClassifierOnInstance (Instance inst,
                                                  Classifier classifier,
                                                  int k,
                                                  WindowRegressionPerformanceEvaluator evaluator,
                                                  double useBestPerforming)
    {
//        int k = MiscUtils.poisson(1.0, classifierRandom);
        if (k > 0) {
            Instance weightedInst = (Instance) inst.copy();
            weightedInst.setWeight(inst.weight() * k);
            classifier.trainOnInstance(weightedInst);
        }
        if(useBestPerforming < 1.0){
            evaluator.addResult(new InstanceExample(inst), classifier.getPredictionForInstance(inst));
        }
    }

    @Override
    public void trainOnInstanceImpl(Instance inst) {
        int[] k = new int[this.ensemble.length];

        IntStream.range(0, this.ensemble.length)
                .forEach(i -> k[i] = MiscUtils.poisson(1.0, this.classifierRandom));

        // train each learner
        if (this.parallelTrain.isSet()) {
            IntStream.range(0, this.ensemble.length)
                    .parallel()
                    .forEach(i -> trainClassifierOnInstance(
                                                            inst,
                                                            this.ensemble[i],
                                                            k[i],
                                                            this.evaluators[i],
                                                            usePercentageOfLearnersForPrediction.getValue())
                    );
        }else{
            for (int i = 0; i < this.ensemble.length; i++) {
                trainClassifierOnInstance(
                                            inst,
                                            this.ensemble[i],
                                            k[i],
                                            this.evaluators[i],
                                            usePercentageOfLearnersForPrediction.getValue());
            }
        }

        if (usePercentageOfLearnersForPrediction.getValue() < 1.0) {
            if (!canUseBestPerforming) {
                canUseBestPerforming = true; // all evaluators have been set. Hence, can use them.
            }
        }
    }

    static class Performance {
        int idx;
        double value;

        public Performance(int idx, double value) {
            this.idx = idx;
            this.value = value;
        }
    }

    @Override
    public double[] getVotesForInstance(Instance inst) {
        boolean regression = inst.classAttribute().isNumeric();
        double sumOfPredictions = 0;
        DoubleVector combinedVote = new DoubleVector();

        List<Performance> performances = new ArrayList<>();
        if (canUseBestPerforming) {
            double[] adjustedR2s = new double[this.evaluators.length];

            for (int i = 0; i < this.evaluators.length; i++) {
                adjustedR2s[i] = this.evaluators[i].getAdjustedCoefficientOfDetermination();
                performances.add(new Performance(i, adjustedR2s[i]));
            }

            Collections.sort(performances, new Comparator<Performance>() { // sort
                @Override
                public int compare(Performance t1, Performance t2) {
//                    return Double.compare(t1.value, t2.value); // natural order
                    return Double.compare(t2.value, t1.value);// for reverse order
                }
            });
        }

        if (regression){
            int length = (int) (this.ensemble.length * (canUseBestPerforming ? usePercentageOfLearnersForPrediction.getValue() : 1.0));
            for (int i = 0; i <  length; i++) {
                int idx = canUseBestPerforming ? performances.get(i).idx : i;
                sumOfPredictions += this.ensemble[idx].getVotesForInstance(inst)[0];
            }
            return new double[]{sumOfPredictions/length};
        }else { // classification
            for (int i = 0; i < this.ensemble.length; i++) {
                DoubleVector vote = new DoubleVector(this.ensemble[i].getVotesForInstance(inst));
                if (vote.sumOfValues() > 0.0) {
                    vote.normalize();
                    combinedVote.addValues(vote);
                }
            }
            return combinedVote.getArrayRef();
        }
    }

    @Override
    public boolean isRandomizable() {
        return true;
    }

    @Override
    public void getModelDescription(StringBuilder out, int indent) {
        // TODO Auto-generated method stub
    }

    @Override
    protected Measurement[] getModelMeasurementsImpl() {
        return new Measurement[]{new Measurement("ensemble size",
                    this.ensemble != null ? this.ensemble.length : 0)};
    }

    @Override
    public Classifier[] getSubClassifiers() {
        return this.ensemble.clone();
    }

    @Override
    public ImmutableCapabilities defineImmutableCapabilities() {
        if (this.getClass() == OzaBag.class)
            return new ImmutableCapabilities(Capability.VIEW_STANDARD, Capability.VIEW_LITE);
        else
            return new ImmutableCapabilities(Capability.VIEW_STANDARD);
    }
}
