import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tools.sm_exceptions import ValueWarning
from pmdarima.arima import auto_arima
from sklearn.metrics import mean_squared_error, mean_absolute_error
import math
from arch.__future__ import reindexing

warnings.filterwarnings('ignore')

# Suppress the value warning
warnings.filterwarnings("ignore", category=ValueWarning)


def test_stationarity(timeseries):
    rolmean = timeseries.rolling(12).mean()
    rolstd = timeseries.rolling(12).std()
    adft = adfuller(timeseries, autolag='AIC')
    return adft[0:4], rolmean, rolstd


train_data_original_scale, test_data_original_scale, fc_series = None, None, None
def arima_pred(dataset_path):
    global train_data_original_scale, test_data_original_scale, fc_series
    # Read the data from the CSV file
    tsla_data = pd.read_csv(dataset_path)

    # Convert the 'Date' column to datetime
    tsla_data['Date'] = pd.to_datetime(tsla_data['Date'])

    # Set 'Date' as the index
    tsla_data.set_index('Date', inplace=True)

    # Use 'Close' column for analysis
    df_close = tsla_data['Close']
    df_close = df_close.ffill()

    test_stationarity(df_close)

    # Log transformation
    df_log = np.log(df_close)

    # Splitting data into train and test
    train_data, test_data = df_log[3:int(len(df_log) * 0.9)], df_log[int(len(df_log) * 0.9):]
    train_data_original_scale = np.exp(train_data)
    test_data_original_scale = np.exp(test_data)

    # Auto ARIMA
    model_autoARIMA = auto_arima(train_data, start_p=0, start_q=0,
                                 test='adf',  # use adftest to find optimal 'd'
                                 max_p=3, max_q=3,  # maximum p and q
                                 m=1,  # frequency of series
                                 d=None,  # let model determine 'd'
                                 seasonal=False,  # No Seasonality
                                 start_P=0,
                                 D=0,
                                 trace=True,
                                 error_action='ignore',
                                 suppress_warnings=True,
                                 stepwise=True)

    model_autoARIMA.fit(train_data, disp=-1)

    # Modeling with ARIMA
    model = ARIMA(train_data, order=model_autoARIMA.order)
    fitted = model.fit()

    # forecast
    forecast = fitted.forecast(len(test_data), alpha=0.05)

    fc_series = pd.Series(np.exp(forecast), index=test_data.index)

    # Handle NaN and inf values
    test_data_original_scale = np.nan_to_num(test_data_original_scale)
    fc_series = np.nan_to_num(fc_series)

    # Evaluation
    mse = mean_squared_error(test_data_original_scale, fc_series)
    mae = mean_absolute_error(test_data_original_scale, fc_series)
    rmse = math.sqrt(mean_squared_error(test_data_original_scale, fc_series))
    mape = np.mean(np.abs(fc_series - test_data_original_scale) / np.abs(test_data_original_scale))

    print(f'MSE: {mse}')
    print(f'MAE: {mae}')
    print(f'RMSE: {rmse}')
    print(f'MAPE: {mape}')

    # Determine classification
    if rmse > 150:
        print('The stock is performing well according to ARIMA.\n')
        return 1
    else:
        print('The stock is performing poorly according to ARIMA.\n')
        return 0


def plot(plot_window, plot_bg_color):
    global train_data_original_scale, test_data_original_scale, fc_series
    # Visualizing the original and forecasted time series
    fig, ax = plt.subplots(figsize=(12, 5), dpi=100)
    fig.patch.set_facecolor(plot_bg_color)
    ax.plot(train_data_original_scale, label='training')
    ax.plot(test_data_original_scale, color='blue', label='Actual Stock Price')
    ax.plot(fc_series, color='orange', label='Predicted Stock Price')
    ax.set_title('ARIMA Stock Price Prediction')
    ax.set_xlabel('Time')
    ax.set_ylabel('Actual Stock Price')
    ax.legend(loc='upper left', fontsize=8)

    canvas = FigureCanvasTkAgg(fig, master=plot_window)
    canvas.draw()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    toolbar = NavigationToolbar2Tk(canvas, plot_window)
    toolbar.update()
    toolbar.pack(side=tk.TOP, fill=tk.X)

# def plot(plot_window):
#     global train_data_original_scale, test_data_original_scale, fc_series
#     # Visualizing the original and forecasted time series
#     plt.figure(figsize=(12, 5), dpi=100)
#     plt.plot(train_data_original_scale, label='training')
#     plt.plot(test_data_original_scale, color='blue', label='Actual Stock Price')
#     plt.plot(fc_series, color='orange', label='Predicted Stock Price')
#     plt.title('ARIMA Stock Price Prediction')
#     plt.xlabel('Time')
#     plt.ylabel('Actual Stock Price')
#     plt.legend(loc='upper left', fontsize=8)
#     plt.show()