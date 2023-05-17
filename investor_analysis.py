import pandas as pd
import json
import requests
import matplotlib.pyplot as plt


def get_recommendations(ticker):

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:97.0) Gecko/20100101 Firefox/97.0'
    }

    url = f'https://query2.finance.yahoo.com/v10/finance/quoteSummary/{ticker}?modules=recommendationTrend'
    r = requests.get(url, headers=headers)
    # print(r)

    if not r.ok:
        print("Error fetching data.")
        return

    result = r.json()['quoteSummary']['result']

    if not result:
        print(f"No recommendation data available for {ticker} ({ticker}).")
        return

    data = result[0]['recommendationTrend']['trend']

    periods = []
    strong_buys = []
    buys = []
    holds = []
    sells = []
    strong_sells = []

    for trend in data:
        periods.append(trend['period'])
        strong_buys.append(trend['strongBuy'])
        buys.append(trend['buy'])
        holds.append(trend['hold'])
        sells.append(trend['sell'])
        strong_sells.append(trend['strongSell'])

    dataframe = pd.DataFrame({
        'Period': periods,
        'Strong Buy': strong_buys,
        'Buy': buys,
        'Hold': holds,
        'Sell': sells,
        'Strong Sell': strong_sells
    })

    dataframe = dataframe.set_index('Period')
    # print(dataframe)

    ax = dataframe.plot.bar(rot=0)
    ax.set_title(f'({ticker}) Investors Recommendation Trends')
    ax.set_ylabel('Investors Recommendation Counts')
    # plt.show()

    # classify overall recommendation trend
    total_recommendations = dataframe.sum(axis=1).sum()
    total_buy_sell = dataframe['Buy'].sum() + dataframe['Sell'].sum()
    total_strong_buy_sell = dataframe['Strong Buy'].sum() + dataframe['Strong Sell'].sum()
    if total_strong_buy_sell >= total_buy_sell * 0.5:
        print(f"({ticker}) is performing well based on investors recommendation trends.")
        return 1
    else:
        print(f"({ticker}) is performing poorly based on investors recommendation trends.")
        return 0