import numpy as np
import pandas as pd
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from sklearn.svm import SVC, LinearSVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import matplotlib.pyplot as plt

'''
    The features used for training the SVM model are:
    
        'Open': The opening price of the stock.
        'High': The highest price of the stock during the day.
        'Low': The lowest price of the stock during the day.
        'Close': The closing price of the stock.
        'Adj Close': The adjusted closing price of the stock.
        'Volume': The trading volume of the stock.
    
    The labels used for training are determined based on the next day's closing price. 
    If the next day's closing price is higher than the current day's closing price, the label is set to 1 (indicating a positive or upward trend). 
    Otherwise, the label is set to -1 (indicating a negative or downward trend).
    
    The SVM model is trained using the fit method, which takes the training features (X_train) and labels (y_train) as input. 
    It tries to find the optimal hyperplane that maximally separates the data points of different classes in the feature space.
    
    The outcomes of the SVM model are predictions made on the test data (X_test) using the trained model. 
    The predictions are obtained using the predict method, which takes the test features as input and returns the predicted labels. 
    These predicted labels are stored in the y_pred variable.
    
    Additionally, the code calculates the accuracy of the predictions by comparing the predicted labels (y_pred) with the actual labels (y_test). 
    The accuracy score is calculated using the accuracy_score function from the sklearn.metrics module.
    
    The SVM model is also used to make predictions on the full dataset (X). 
    The predictions are stored in the y_pred_all variable, and based on these predictions, the performance of the stock is determined as either "Performing well" or "Performing poorly" for each data point. 
    The overall performance is then determined based on the proportion of data points classified as "Performing well" compared to the total number of data points. 
    If the proportion is greater than or equal to 0.5, the SVM is considered to be performing well; otherwise, it is considered to be performing poorly. 
    The function returns either 1 or 0 based on this determination.

'''

x_test, y_test, clf = None, None, None
def svm_pred(dataset):
    global X_test, y_test, clf
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

    # Predict on full dataset
    y_pred_all = clf.predict(X)
    performance = np.where(y_pred_all > 0, 'Performing well', 'Performing poorly')  # 1 = positve trend, -1 = negative trend (previous day closing prices)
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


def plot(plot_window):
    # TODO: I guess blue = positive trend and red = negative trend
    global X_test, y_test, clf
    fig, ax = plt.subplots(figsize=(12, 5))
    colors = ['blue' if label == 1 else 'red' for label in y_test]
    ax.scatter(X_test.iloc[:, 0], X_test.iloc[:, 1], c=colors)
    ax.set_xlabel('Open')
    ax.set_ylabel('High')
    ax.set_title('Stock Trend Classification')

    # Plot decision boundary
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()
    xx, yy = np.meshgrid(np.linspace(*xlim, num=200), np.linspace(*ylim, num=200))
    Z = clf.decision_function(np.c_[xx.ravel(), yy.ravel(), np.zeros_like(xx.ravel()), np.zeros_like(
        xx.ravel()), np.zeros_like(xx.ravel()), np.zeros_like(xx.ravel())])
    Z = Z.reshape(xx.shape)
    ax.contour(xx, yy, Z, levels=[0], colors='k')
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)

    canvas = FigureCanvasTkAgg(fig, master=plot_window)
    canvas.draw()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    toolbar = NavigationToolbar2Tk(canvas, plot_window)
    toolbar.update()
    toolbar.pack(side=tk.TOP, fill=tk.X)

# def plot(plot_window):
#     global X_test, y_test, clf
#     fig, ax = plt.subplots(figsize=(12, 5))
#     ax.scatter(X_test.iloc[:, 0], X_test.iloc[:, 1], c=y_test)
#     ax.set_xlabel('Open')
#     ax.set_ylabel('High')
#     ax.set_title('Stock Performance Classification')
#     xlim = ax.get_xlim()
#     ylim = ax.get_ylim()
#     xx, yy = np.meshgrid(np.linspace(*xlim, num=200), np.linspace(*ylim, num=200))
#     Z = clf.decision_function(np.c_[xx.ravel(), yy.ravel(), np.zeros_like(xx.ravel()), np.zeros_like(xx.ravel()), np.zeros_like(xx.ravel()), np.zeros_like(xx.ravel())])
#     Z = Z.reshape(xx.shape)
#     ax.contour(xx, yy, Z, levels=[0], colors='k')
#     ax.set_xlim(xlim)
#     ax.set_ylim(ylim)
#
#     canvas = FigureCanvasTkAgg(fig, master=plot_window)
#     canvas.draw()
#     canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
#
#     toolbar = NavigationToolbar2Tk(canvas, plot_window)
#     toolbar.update()
#     toolbar.pack(side=tk.TOP, fill=tk.X)