import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import accuracy_score
from sklearn.ensemble import RandomForestClassifier
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.pyplot as plt


test_y, test_predict_rf = None, None
def random_forest_pred(stock_data_filename):
    global test_y, test_predict_rf
    # Read the CSV file into a DataFrame
    stock_data = pd.read_csv(stock_data_filename)

    # Handling missing values
    data = stock_data.drop(['Date'], axis=1)  # drop non-numeric columns
    data = data.fillna(data.mean())
    scaler = MinMaxScaler(feature_range=(0, 1))
    data_scaled = scaler.fit_transform(data)

    # Calculate the daily return
    data_scaled = pd.DataFrame(data_scaled, columns=data.columns)
    data_scaled['Return'] = data_scaled['Close'].pct_change()
    data_scaled.dropna(inplace=True)

    # Classify the return as '1' if positive and '0' if not
    data_scaled['Return'] = (data_scaled['Return'] > 0).astype(int)

    # Split the data into training and testing sets
    train_size = int(len(data_scaled) * 0.7)
    test_size = len(data_scaled) - train_size
    train_data, test_data = data_scaled.iloc[0:train_size, :], data_scaled.iloc[train_size:len(data_scaled), :]

    # 'Return' as target
    train_y = train_data['Return']
    test_y = test_data['Return']

    # Rest of the data as input
    train_X = train_data.drop('Return', axis=1)
    test_X = test_data.drop('Return', axis=1)

    # Define the Random Forest model
    model_rf = RandomForestClassifier(n_estimators=100, random_state=42)
    model_rf.fit(train_X, train_y)

    # Make predictions using the Random Forest model
    train_predict_rf = model_rf.predict(train_X)
    test_predict_rf = model_rf.predict(test_X)

    # Evaluate the Random Forest model
    accuracy_rf = accuracy_score(test_y, test_predict_rf)
    print("Accuracy of Random Forest:", accuracy_rf)

    # # Plot actual vs predicted
    # plt.figure(figsize=(10, 6))
    # plt.plot(test_y.index, test_y, label='Actual')
    # plt.plot(test_y.index, test_predict_rf, label='Predicted')
    # plt.title('(Random Forest Model) Actual vs Predicted Values')
    # plt.legend()
    # plt.show()

    # Classify the stock as either 'good' or 'poor'
    if accuracy_rf > 0.65:
        print("Random Forest Accuracy: Performing Well.\n")
        return 1
    else:
        print("Random Forest Accuracy: Performing Poorly.\n")
        return 0


def plot(plot_window, plot_bg_color):
    global test_y, test_predict_rf

    # Calculate the absolute error between actual and predicted values
    error = abs(test_y - test_predict_rf)

    # Create a figure with two subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)
    fig.patch.set_facecolor(plot_bg_color)

    # Plot actual vs predicted values
    ax1.plot(test_y.index, test_y, label='Actual')
    ax1.plot(test_y.index, test_predict_rf, label='Predicted')
    ax1.set_title('(Random Forest Model) Actual vs Predicted Values')
    ax1.legend()

    # Plot the absolute error
    ax2.plot(test_y.index, error, color='red')
    ax2.set_title('Absolute Error')

    # Create a canvas and draw the figure on it
    canvas = FigureCanvasTkAgg(fig, master=plot_window)
    canvas.draw()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    # Create a toolbar and pack it into the window
    toolbar = NavigationToolbar2Tk(canvas, plot_window)
    toolbar.update()
    toolbar.pack(side=tk.TOP, fill=tk.X)


# def plot(plot_window):
#     global test_y, test_predict_rf
#
#     # Plot actual vs predicted
#     fig, ax = plt.subplots()
#     ax.plot(test_y.index, test_y, label='Actual')
#     ax.plot(test_y.index, test_predict_rf, label='Predicted')
#     ax.set_title('(Random Forest Model) Actual vs Predicted Values')
#     ax.legend()
#
#     # # Create a Tkinter window
#     # plot_window = tk.Tk()
#     # plot_window.title('Plot Window')
#
#     # Create a canvas and draw the figure on it
#     canvas = FigureCanvasTkAgg(fig, master=plot_window)
#     canvas.draw()
#     canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
#
#     # Create a toolbar and pack it into the window
#     toolbar = NavigationToolbar2Tk(canvas, plot_window)
#     toolbar.update()
#     toolbar.pack(side=tk.TOP, fill=tk.X)