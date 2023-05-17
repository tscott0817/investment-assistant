import pandas as pd
import matplotlib.pyplot as plt


def macd_pred(csv_file_path):
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

    # # Plotting MACD and Signal line
    # plt.figure(figsize=(12,5))
    # plt.plot(df['MACD'], label='MACD', color = 'red')
    # plt.plot(df['Signal'], label='Signal Line', color='blue')
    # plt.title('MACD and Signal Line')
    # plt.legend(loc='upper left')
    # plt.show()
    #
    # # Plotting Cumulative Returns
    # plt.figure(figsize=(12,5))
    # plt.plot(df['Cumulative_Returns'], label='Cumulative Returns', color = 'green')
    # plt.title('Cumulative Returns')
    # plt.legend(loc='upper left')
    # plt.show()

    return decision
