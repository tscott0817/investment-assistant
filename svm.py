import numpy as np
import pandas as pd
from sklearn.svm import SVC, LinearSVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import matplotlib.pyplot as plt


def svm_pred(dataset):
    # Load data from CSV file
    data = pd.read_csv(dataset)

    # Extract features and labels
    X = data[['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']]
    y = np.where(data['Close'].shift(-1) > data['Close'], 1, -1)  # Labels based on next day's closing price

    # Split data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Fit LinearSVC classifier
    clf = LinearSVC(max_iter=100000, random_state=42)

    unique_labels = np.unique(y_train)
    if len(unique_labels) < 2:
        print("Not enough classes in the training data for the SVM classifier.")
        return

    clf.fit(X_train, y_train)

    # Make predictions on test data
    y_pred = clf.predict(X_test)

    # Calculate accuracy score
    accuracy = accuracy_score(y_test, y_pred)
    # print('Accuracy:', accuracy)

    # Plot decision boundary
    # TODO: Not sure if we want plots
    # fig, ax = plt.subplots()
    # ax.scatter(X_test.iloc[:, 0], X_test.iloc[:, 1], c=y_test)
    # ax.set_xlabel('Open')
    # ax.set_ylabel('High')
    # ax.set_title('Stock Performance Classification')
    # xlim = ax.get_xlim()
    # ylim = ax.get_ylim()
    # xx, yy = np.meshgrid(np.linspace(*xlim, num=200), np.linspace(*ylim, num=200))
    # Z = clf.decision_function(np.c_[xx.ravel(), yy.ravel(), np.zeros_like(xx.ravel()), np.zeros_like(
    #     xx.ravel()), np.zeros_like(xx.ravel()), np.zeros_like(xx.ravel())])
    # Z = Z.reshape(xx.shape)
    # ax.contour(xx, yy, Z, levels=[0], colors='k')
    # ax.set_xlim(xlim)
    # ax.set_ylim(ylim)
    # plt.show()

    # Predict on full dataset
    y_pred_all = clf.predict(X)
    performance = np.where(y_pred_all > 0, 'Performing well', 'Performing poorly')
    data['Performance'] = performance

    # Determine overall performance
    n_well = len(data[data['Performance'] == 'Performing well'])
    n_poor = len(data[data['Performance'] == 'Performing poorly'])
    if n_well / (n_well + n_poor) >= 0.5:
        print('SVM: Performing well. \n')
        return 1
    else:
        print('SVM: Performing poorly. \n')
        return 0
