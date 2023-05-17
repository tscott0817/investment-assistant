import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression, ElasticNet
from sklearn import linear_model

# GUI
from tkinter import *
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)

data = None
data_csv = ""
X = None
Y = None
def regression_pred(dataset):
    global data
    global data_csv
    # Read in data
    data = pd.read_csv(dataset)
    data_csv = dataset

    # Average between high and low values; what the stock is worth on average for any given day
    data['Average'] = (data['High'] + data['Low']) / 2

    # Add the column of ones to the data
    data.insert(0, 'Ones', 1)
    # Create a new column converting the date type into an integer, use these values for tracking since start of data
    data['Date'] = pd.to_datetime(data['Date'])
    data.insert(1, 'DateInt', range(0, len(data)))
    # print(data)

    '''
    Separate the data into x and y:
        x = The ones column and ID (date as integer)
        y = The average of the High and Low values
    '''
    global X
    global Y
    cols = data.shape[1]
    X = data[['Ones', 'DateInt']]
    Y = data['Average']
    X = np.asarray(X.values)
    Y = np.asarray(Y.values)
    theta = np.matrix(np.array([0, 0])).T

    model = linear_model.LinearRegression(fit_intercept=False)
    model.fit(X, Y)
    model_coef = model.coef_


    # TODO: This classification doesn't really use the regression model, needs reworked
    '''
    Classifying as "good" or "poor" performing stock
    '''
    # Get number of years by the difference between the last date and the first date
    num_years = data['Date'].iloc[-1].year - data['Date'].iloc[0].year
    recent_data = data.tail(252 * num_years)

    # Compute the year-over-year percentage change in closing prices for each year
    yearly_pct_change = recent_data['Close'].pct_change(periods=252).groupby(recent_data['Date'].dt.year).mean()
    sum_pct_change = yearly_pct_change.sum()

    print(f"{num_years} Year High/Low Analysis: ", sum_pct_change)
    # Classify the stock as "good" or "poor" performing based on the trend
    if sum_pct_change > 0:
        print("The stock is performing well over time.\n")
        return 1
    else:
        print("The stock is performing poorly over time.\n")
        return 0

def generate_polynomial_features(X, polydegree):
    poly = PolynomialFeatures(degree=polydegree)
    polynomial_x = poly.fit_transform(X)
    return polynomial_x

def nonlinear_regression_elastic(X, y, degree, alpha, l1_ratio):
    X_poly = generate_polynomial_features(X, degree)
    model = ElasticNet(alpha=alpha, l1_ratio=l1_ratio, fit_intercept=False)
    model.fit(X_poly, y)
    y_pred = model.predict(X_poly)
    return y_pred, model.coef_

def plot(main_window):
    global data
    global data_csv
    global X
    global Y
    poly_degree_values = [2, 3, 4, 6, 8]
    plot_colors = ['red', 'blue', 'green', 'orange', 'purple']

    # fig, ax = plt.subplots()  # Create Figure and Axes objects
    # TODO: Make relative to window size, not hardcoded
    fig, ax = plt.subplots(figsize=(4, 3))  # Create Figure and Axes objects
    # fig, ax = plt.subplots(figsize=(main_window.winfo_screenwidth() * 0.5, 6))  # Adjust the height as needed

    for i, degree in enumerate(poly_degree_values):
        y_pred, model_coef = nonlinear_regression_elastic(X, Y, degree=degree, alpha=2, l1_ratio=0.9)
        ax.plot(data['Date'], y_pred, color=plot_colors[i], label=f"Predicted (Degree {degree})")

    file_name_with_extension = os.path.basename(data_csv)
    data_name, _ = os.path.splitext(file_name_with_extension)

    ax.scatter(data['Date'], data['Average'], color='#1f77b4', label='Training Data')

    ax.set_title(data_name + f" Average Daily Stock Price (Elastic Net)")
    ax.set_xlabel('Date')
    ax.set_ylabel('Average Daily Market Value')
    ax.legend(poly_degree_values)

    # creating the Tkinter canvas
    # containing the Matplotlib figure
    canvas = FigureCanvasTkAgg(fig, master=main_window)
    canvas.draw()
    canvas.get_tk_widget().grid(row=5, column=5, sticky="nsew")

    # creating the Matplotlib toolbar
    # toolbar = NavigationToolbar2Tk(canvas, main_window)
    # change toolbar to use the grid layout manager
    toolbar = NavigationToolbar2Tk(canvas, main_window, pack_toolbar=False)
    toolbar.update()

    # placing the toolbar on the Tkinter window
    canvas.get_tk_widget().grid(row=5, column=5, sticky="nsew")
    # canvas.get_tk_widget().pack()
