from arch.__future__ import reindexing
reindexing.reindex = True
import warnings
import math
import numpy as np
import pandas as pd
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.pyplot as plt
from arch.utility.exceptions import ConvergenceWarning
from arch import arch_model
from arch.__future__ import reindexing

warnings.filterwarnings("ignore", "", ConvergenceWarning)

tsla_data, rolling_predictions = None, None
def garch_pred(stock_data):
    global tsla_data, rolling_predictions
    reindexing.reindex = True
    # Read dataset from the csv file
    tsla_data = pd.read_csv(stock_data)

    # Convert 'Date' column to datetime
    tsla_data['Date'] = pd.to_datetime(tsla_data['Date'])
    tsla_data.set_index("Date", inplace=True)

    daily_volatility = tsla_data['Close'].std()
    monthly_volatility = math.sqrt(21) * daily_volatility
    annual_volatility = math.sqrt(252) * daily_volatility

    # BUILDING THE GARCH MODEL
    garch_model = arch_model(tsla_data['Close'], p=1, q=1,
                             mean='constant', vol='GARCH', dist='normal')
    gm_result = garch_model.fit(disp='off')

    gm_forecast = gm_result.forecast(horizon=5)

    # Rolling Predictions
    rolling_predictions = []
    test_size = 365

    for i in range(test_size):
        train = tsla_data['Close'][:-(test_size - i)]
        model = arch_model(train, p=1, q=1)
        model_fit = model.fit(disp='off')
        pred = model_fit.forecast(horizon=1)
        rolling_predictions.append(np.sqrt(pred.variance.values[-1, :][0]))

    rolling_predictions = pd.Series(rolling_predictions, index=tsla_data['Close'].index[-365:])

    # Calculate Sharpe ratio
    returns = tsla_data['Close'].pct_change()
    sharpe_ratio = np.sqrt(252) * (returns.mean() / returns.std())

    if sharpe_ratio < 1:
        print("Based on the GARCH Sharpe ratio, it is not a good time to invest.\n")
        return 0
    else:
        print("Based on the GARCH Sharpe ratio, it is a good time to invest.\n")
        return 1


def plot(plot_window, plot_bg_color):
    global tsla_data, rolling_predictions

    fig, ax = plt.subplots(figsize=(13, 4))
    fig.patch.set_facecolor(plot_bg_color)
    ax.grid(which="major", axis='y', color='#758D99', alpha=0.3, zorder=1)
    ax.spines[['top', 'right']].set_visible(False)
    plt.plot(tsla_data['Close'][-365:])
    plt.plot(rolling_predictions)
    plt.title("(GARCH Model) Volatility Prediction - Rolling Forecast")
    plt.legend(['True Daily Returns', 'Predicted Volatility'])

    canvas = FigureCanvasTkAgg(fig, master=plot_window)
    canvas.draw()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    toolbar = NavigationToolbar2Tk(canvas, plot_window)
    toolbar.update()
    toolbar.pack(side=tk.TOP, fill=tk.X)