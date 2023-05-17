import os
import time
import yfinance as yf
import regression
import macd
import svm
import investor_analysis
# import sentimentAnalysis
# import sentimentAnalysisPretrainedBert
import arima
import garch
import random_forest
# from tk import *
# from tkinter import *
# from tkinter import ttk
import tkinter as tk


def main():

    '''
        Inits and User Input
    '''
    stock_data_list = []
    running = True
    print("Welcome to the Stock Market Prediction Program!")
    print("Please follow the prompts to get started. Enter 'q' at any point the exit the program.")
    print("Enter the stock symbol of any company in AMEX, NYSE, or NASDAQ.")
    print("To start at the beginning dataset, enter 'Start' for the start date.")
    print("To go until the end of the dataset, enter 'End' for the end date.")

    '''
        Main Loop
    '''
    while running:
        # User input
        stock = input("Please enter in a stock symbol to search: ")
        if stock =='q':  # Enter 'q' at any point in program to quit
            break
        time.sleep(0.1)  # Sleep is needed otherwise it still executes the next line

        # Check all stock symbols to makes sure company exists
        stock_exists = False
        with open("data/all_symbols.txt", "r") as f:
            for line in f:
                if stock in line:
                    print("Stock exists")
                    stock_exists = True
            f.close()

        '''
            Stock Data:
                - If the stock exists, ask for a start and end date
                - If the stock does not exist, ask for another stock symbol
        '''
        if stock_exists:
            start_date = input("Please enter in a start date (YYYY-MM-DD): ")
            if start_date =='q':
                break
            time.sleep(0.1)
            end_date = input("Please enter in an end date (YYYY-MM-DD): ")
            if end_date =='q':
                break
            time.sleep(0.1)

            # Read and parse the stock data
            if start_date == 'Start' and end_date == 'End':  # Full dataset
                current_stock = yf.download(stock)
            elif start_date == 'Start':  # Beginning of dataset until end_date
                current_stock = yf.download(stock, end=end_date)
            elif end_date == 'End':  # Set start date until end of dataset
                current_stock = yf.download(stock, start=start_date)
            else:  # Specific set of dates
                current_stock = yf.download(stock, start=start_date, end=end_date)

            current_stock["Date"] = current_stock.index
            stock_data = current_stock[['Date', 'Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']]
            stock_data.reset_index(drop=True, inplace=True)

            # Put data into csv files located at data/filename.csv, for regression and macd models
            stock_data.to_csv(f"data/{stock}.csv", index=False)
            stock_data = f"data/{stock}.csv"
            if stock_data not in stock_data_list:
                stock_data_list.append(stock_data)


            '''
                Models:
                    - Each returns a classification or 'good' or 'poor' performance as a '0' or '1'
                    - The collection of the models predictions will be used to determine the final confidence level for investment
            '''
            regression_result = regression.regression_pred(stock_data)  # Pass the csv file to objects
            macd_result = macd.macd_pred(stock_data)
            svm_result = svm.svm_pred(stock_data)
            random_forest.random_forest_pred(stock_data)
            arima_result = arima.arima_pred(stock_data)
            garch_result = garch.garch_pred(stock_data)
            investor_analysis_result = investor_analysis.get_recommendations(stock)
            # sentimentAnalysis.sentiment_analysis_subreddit(stock)
            # sentimentAnalysisPretrainedBert.sentiment_analysis(stock)

            # Add all results to list
            results = [regression_result, macd_result, svm_result, arima_result, garch_result, investor_analysis_result]
            # results = [regression_result, macd_result, svm_result]

            num_ones = sum(result == 1 for result in results)
            num_zeros = sum(result == 0 for result in results)

            if num_ones + num_zeros > 0:
                ratio = num_ones / (num_ones + num_zeros)
                percentage = ratio * 100
                print(f"There is a {percentage:.2f}% confidence level of {stock} stock performing well.")
            else:
                print("The results list is empty.")

        else:
            print("Stock does not exist. Please try again.")
            continue


    # Delete the files when the program is quit
    for s_data in stock_data_list:
        os.remove(s_data)


if __name__ == "__main__":
    main()
