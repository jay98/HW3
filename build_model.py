import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.svm import SVC
from sklearn.metrics import classification_report, confusion_matrix
from joblib import dump

col = ['Ax', 'Ay', 'Az', 'Gx', 'Gy', 'Gz', 'label']
data = pd.read_csv("data.csv", names=col)

X = data.drop('label', axis=1)
y = data['label']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20)

Cs = [0.001, 0.01, 0.1, 1., 10.]
gamma = [0.001, 0.01, 0.1, 1.]

param_grid = {'C': Cs, 'gamma': gamma}

svclassifier = GridSearchCV(SVC(kernel='rbf'), param_grid, cv=10)
# svclassifier = SVC(kernel='rbf'
svclassifier.fit(X_train, y_train)

dump(svclassifier, 'door_model.joblib')

y_pred = svclassifier.predict(X_test)

# [0.0880126953125, 0.980712890625, 0.068115234375, -0.7442748091603053, -1.7709923664122138, 0.030534351145038167, -1]
# [0.1282958984375, 0.978759765625, 0.058349609375, -0.9618320610687023, -4.248091603053435, -0.1297709923664122, -1]


print(confusion_matrix(y_test, y_pred))
print(classification_report(y_test, y_pred))
