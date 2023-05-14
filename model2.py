# import os
# from sklearn import *

# import pandas as pd
# avo_TRAIN = pd.read_csv('score.csv')
# #drop NaN

# # Select data for learning
# f = ['angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral','year of birth','gender']
# X = avo_TRAIN[f]
# y = avo_TRAIN.score

# model = ensemble.RandomForestRegressor(random_state=2020, n_estimators=50)
# Xtrain, Xtest, ytrain, ytest = model_selection.train_test_split(X, y, test_size=0.8)
# print("training split: ", len(Xtrain), "; test split: ", len(Xtest))
# model.fit(X, y)
# model.score(Xtest, ytest)