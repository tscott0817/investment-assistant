import pandas as pd
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.pyplot as plt

df = None
def macd_pred(csv_file_path):
    global df
    # Read in the CSV file
    df = pd.read_csv(csv_file_path)

    # Calculate the MACD
    short_ema = df['Close'].ewm(span=12, adjust=False).mean()
    long_ema = df['Close'].ewm(span=26, adjust=False).mean()
    macd = short_ema - long_ema
    signal = macd.ewm(span=9, adjust=False).mean()
    df['MACD'] = macd
    df['Signal'] = signal

    # Calculate daily returns
    df['Returns'] = df['Close'].pct_change()

    # Make stock predictions based on the MACD
    df['Position'] = 0
    df.loc[signal > macd, 'Position'] = 1
    df.loc[signal < macd, 'Position'] = -1
    df['Strategy'] = df['Position'].shift(1) * df['Returns']
    df['Cumulative_Returns'] = (1 + df['Strategy']).cumprod()

    # Print the cumulative returns
    final_return = df['Cumulative_Returns'].iloc[-1]
    print(f"MACD Cumulative Returns: {final_return:.2f}")

    # Make investment decision based on final return
    if final_return > 1:
        print("This stock has good returns\n")
        decision = 1
    else:
        print("This stock has poor returns.\n")
        decision = 0

    return decision


# MACD Line: The MACD line primarily indicates the overall momentum of the price movement.
# When the MACD line is above the zero line, it suggests bullish momentum, indicating that the shorter-term EMA is above the longer-term EMA.
# Conversely, when the MACD line is below the zero line, it indicates bearish momentum, implying that the shorter-term EMA is below the longer-term EMA.
#
# Signal Line: The signal line helps traders identify potential buy and sell signals based on the crossovers with the MACD line.
# When the MACD line crosses above the signal line, it generates a bullish signal, suggesting a potential buying opportunity.
# Conversely, when the MACD line crosses below the signal line, it generates a bearish signal, indicating a potential selling opportunity.

def plot(plot_window):
    global df
    # Plotting MACD and Signal line
    # fig1, ax1 = plt.subplots(figsize=(12, 5))
    # fig, ax = plt.subplots()
    fig1 = plt.figure(facecolor='violet')  # TODO: This should be method param for when the theme is changed
    ax1 = fig1.add_subplot(111, facecolor='yellow')
    ax1.plot(df['MACD'], label='MACD', color='red')
    ax1.plot(df['Signal'], label='Signal Line', color='blue')
    ax1.set_title('MACD and Signal Line')
    ax1.legend(loc='upper left')

    canvas1 = FigureCanvasTkAgg(fig1, master=plot_window)
    canvas1.draw()
    canvas1.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    toolbar1 = NavigationToolbar2Tk(canvas1, plot_window)
    toolbar1.update()
    toolbar1.pack(side=tk.TOP, fill=tk.X)

    fig2 = plt.figure(facecolor='violet')  # TODO: This should be method param for when the theme is changed
    ax2 = fig2.add_subplot(111, facecolor='yellow')
    ax2.plot(df['Cumulative_Returns'], label='Cumulative Returns', color='green')
    ax2.set_title('Cumulative Returns')
    ax2.legend(loc='upper left')

    canvas2 = FigureCanvasTkAgg(fig2, master=plot_window)
    canvas2.draw()
    canvas2.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    toolbar2 = NavigationToolbar2Tk(canvas2, plot_window)
    toolbar2.update()
    toolbar2.pack(side=tk.TOP, fill=tk.X)
