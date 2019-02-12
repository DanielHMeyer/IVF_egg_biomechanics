# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.linear_model import LogisticRegression, LogisticRegressionCV
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import make_scorer, roc_auc_score
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)




class OutcomePredictor(object):
    """
    A class to train classifiers to predict the reproductive potential of human eggs.
    """
    
    def __init__(self, classifier='svm', selection='forward'):
        """
        Initialize an instance of the class.
        
        Args:
            model (str):        Which classifier to use
            selection (str):    What type of feature selection algorithm to use
        """
        self.classifier = OutcomePredictor._prepare_model(classifier)
        self.selection = selection
    
    @staticmethod
    def _create_train_test_set(X, y, test_size=0.2):
        """
        Create training and test set
        
        Args:
            X (DataFrame):  DataFrame with features
            y (Series):     Series with labels
            test_size (float):  size of the test set
        Returns:
            X_train (DataFrame):    Training set features
            X_test (DataFrame):     Test set features
            y_train (Series):       Training set labels
            y_test (Series):        Test set labels
        """
        X_train, X_test, y_train, y_test = train_test_split(X, y,
                                                            test_size=test_size, 
                                                            random_state=42, 
                                                            stratify=y)
        X_train.reset_index(drop=True, inplace=True)
        X_test.reset_index(drop=True, inplace=True)
        y_train.reset_index(drop=True, inplace=True)
        y_test.reset_index(drop=True, inplace=True)                                                    
        return (X_train, X_test, y_train, y_test)
    
    @staticmethod
    def _prepare_model(classifier):
        if classifier=='svm':
            svm = SVC(kernel='rbf', random_state=7, class_weight='balanced')
            pipe_svm = make_pipeline(StandardScaler(), svm)
            param_range = [0.0001, 0.001, 0.01, 0.1, 1.0, 10.0, 100.0, 1000.0]
            grid_svm = [{'svc__C': param_range, 'svc__gamma': param_range}]
            grid_search = GridSearchCV(estimator=pipe_svm, param_grid=grid_svm,
                              scoring=make_scorer(roc_auc_score), cv=20)
        elif classifier=='forest':
            forest = RandomForestClassifier(random_state=7)
            grid_forest = [{'max_depth': [1,2,3,4,5,6,None],
                            'n_estimators': [2,4,6,8,10]}]
            grid_search = GridSearchCV(estimator=forest, param_grid=grid_forest,
                                     scoring=make_scorer(roc_auc_score), cv=20)
        return grid_search

    #TODO: Implement sequential backward selection
    def perform_sequential_backward_selection(self, X_train, y_train):
        pass
    
    def perform_forward_feature_selection(self, X_train, y_train):
        """
        Find the best feature combination by forward feature selection
        
        Args:
            X_train (DataFrame):    Training set features
            y_train (DataFrame):    Training set labels
        
        Returns:
            best_combination_of_features (DataFrame): The combination of features
                with the best score
        """
        grid_search = self.classifier
        best_features_so_far = []
        all_features = X_train.columns.tolist()
        features_to_choose_from = all_features.copy()
        best_combination_of_features = pd.DataFrame({'Features':'', 
                                                     'Score': 0, 
                                                     'Model': ''}, index=[0])
        print('')
        print('Starting forward feature selection process.')
        
        while True:
            results = pd.DataFrame(columns=['Features', 'Score', 'Model'])
            print('#####################################################')
            for col in features_to_choose_from:
                features = best_features_so_far.copy()
                features.append(col)
                grid_search.fit(X_train[features], y_train)
                results = results.append(pd.DataFrame({'Features': col, 
                                             'Score': grid_search.best_score_,
                                             'Model': grid_search}, index=[0]),
                                ignore_index=True, sort=True)
                print('Score %s: %.3f' % (col, grid_search.best_score_))
                print(grid_search.best_params_)
            results = results.loc[results['Score']==max(results['Score']), 
                    ['Features', 'Score', 'Model']]
            next_feature = results.iloc[0]['Features']
            best_features_so_far.append(next_feature)
            features_to_choose_from.remove(next_feature)
            if (best_combination_of_features.iloc[0]['Score'] <
                results.iloc[0]['Score']):
                best_combination_of_features = results
                best_combination_of_features['Features'] = best_features_so_far
            else:
                self.classifier = best_combination_of_features.iloc[0]['Model']
                print('')
                print('Forward feature selection process terminated.')
                print('')
                break
        return best_combination_of_features
            
    def fit(self, X_train, y_train):
        if self.selection=='forward':
            best_combination = self.perform_forward_feature_selection(X_train,
                                                                      y_train)
        return best_combination
    
    # TODO: implement predict function
    def predict(self):
        pass
        
        