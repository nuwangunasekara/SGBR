package moa.classifiers.trees;

import moa.classifiers.bayes.NaiveBayes;
import moa.classifiers.core.attributeclassobservers.AttributeClassObserver;
import moa.core.Utils;
import com.yahoo.labs.samoa.instances.Instance;


public class RandomHoeffdingRegressionTree extends HoeffdingRegressionTree {

    private static final long serialVersionUID = 1L;

    @Override
    public String getPurposeString() {
        return "Random regression trees for data streams.";
    }

    public static class RandomLearningNodeForRegression extends ActiveLearningNodeForRegression {

        private static final long serialVersionUID = 1L;

        protected int[] listAttributes;

        protected int numAttributes;

        public RandomLearningNodeForRegression(double[] initialClassObservations,LearningNodePerceptron p) {
            super(initialClassObservations,p);
        }

        @Override
        public void learnFromInstance(Instance inst, HoeffdingTree ht) {
            this.observedClassDistribution.addToValue(0,
                    inst.weight());
            this.observedClassDistribution.addToValue(1,
                    inst.weight() * inst.classValue());
            this.observedClassDistribution.addToValue(2,
                    inst.weight() * inst.classValue() * inst.classValue());


            if (regressionTree==false)  {
                learningModel.updatePerceptron(inst);
            }
            if (this.listAttributes == null) {
                this.numAttributes = (int) Math.floor(Math.sqrt(inst.numAttributes()));
                this.listAttributes = new int[this.numAttributes];
                for (int j = 0; j < this.numAttributes; j++) {
                    boolean isUnique = false;
                    while (isUnique == false) {
                        this.listAttributes[j] = ht.classifierRandom.nextInt(inst.numAttributes() - 1);
                        isUnique = true;
                        for (int i = 0; i < j; i++) {
                            if (this.listAttributes[j] == this.listAttributes[i]) {
                                isUnique = false;
                                break;
                            }
                        }
                    }

                }
            }
            for (int j = 0; j < this.numAttributes - 1; j++) {
                int i = this.listAttributes[j];
                int instAttIndex = modelAttIndexToInstanceAttIndex(i, inst);
                AttributeClassObserver obs = this.attributeObservers.get(i);
                if (obs == null) {
                    obs = inst.attribute(instAttIndex).isNominal() ? ht.newNominalClassObserver() : ht.newNumericClassObserver();
                    this.attributeObservers.set(i, obs);
                }
                obs.observeAttributeTarget(inst.value(instAttIndex),  inst.classValue());
            }
        }
    }
    public static class ARFMeanLearningNode extends RandomLearningNodeForRegression {

        public ARFMeanLearningNode(double[] initialClassObservations, LearningNodePerceptron p) {
            super(initialClassObservations, p);
        }

        @Override
        public double[] getClassVotes(Instance inst, HoeffdingTree ht) {

            double numberOfExamplesSeen = 0;

            double sumOfValues = 0;

            double prediction = 0;

            double V[] = super.getClassVotes(inst, ht);
            sumOfValues = V[1];
            numberOfExamplesSeen = V[0];
            prediction = sumOfValues / numberOfExamplesSeen;
            return new double[]{prediction};
        }

    }
    public static class ARFPerceptronLearningNode extends RandomLearningNodeForRegression {

        public ARFPerceptronLearningNode(double[] initialClassObservations, LearningNodePerceptron p) {
            super(initialClassObservations, p);
        }

        @Override
        public double[] getClassVotes(Instance inst, HoeffdingTree ht) {
            return new double[] {learningModel.prediction(inst)};
        }
    }





    public RandomHoeffdingRegressionTree() {
        this.removePoorAttsOption = null;
    }

    @Override
    protected LearningNode newLearningNode() {
        LearningNodePerceptron p = new LearningNodePerceptron();
        return newLearningNode(new double[0],p);
    }
    @Override
    protected LearningNode newLearningNode(double[] initialClassObservations,LearningNodePerceptron p) {
        if (meanPredictionNodeOption.isSet())
        {
            regressionTree=true ;
            return new ARFMeanLearningNode(initialClassObservations, p);
        }
        regressionTree=false ;
        return new ARFPerceptronLearningNode(initialClassObservations, p);
    }

    @Override
    public boolean isRandomizable () {
        return true;
    }
    @Override
    public void enforceTrackerLimit() {

    }
    @Override
    protected void deactivateLearningNode(ActiveLearningNode toDeactivate,
                                          SplitNode parent, int parentBranch) {

    }

}
