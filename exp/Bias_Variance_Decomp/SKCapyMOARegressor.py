from pprint import pprint

import numpy as np
from sklearn.base import BaseEstimator, RegressorMixin

from capymoa.base import MOARegressor
from moa.classifiers import Regressor as MOAAbstractRegressor
from moa.classifiers.trees import FIMTDD
from capymoa.stream._stream import NumpyStream


class SKCapyMOARegressor(BaseEstimator, RegressorMixin):

    def __init__(self, MOA_regressor: MOAAbstractRegressor=FIMTDD, CLI="-s VarianceReductionSplitCriterion -g 50 -c 0.01 -e",  **config):
        self.MOA_regressor = MOA_regressor
        self.CLI = CLI

    def fit(self, X, y):
        stream = NumpyStream(X, y, enforce_regression=True)
        self.capymoa_model = MOARegressor(schema=stream.get_schema(), moa_learner=self.MOA_regressor(), CLI=self.CLI)
        while stream.has_more_instances():
            instance = stream.next_instance()
            self.capymoa_model.train(instance)
        return self

    def predict(self, X):
        predictions = []
        dummy_y = np.zeros(X.shape[0])
        stream = NumpyStream(X, dummy_y, enforce_regression=True)
        while stream.has_more_instances():
            instance = stream.next_instance()
            prediction = self.capymoa_model.predict(instance)
            predictions.append(prediction)
        return np.array(predictions)


