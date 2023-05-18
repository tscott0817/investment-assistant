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


# GUI
import tkinter as tk
from tkinter import ttk
from tkinter.ttk import Entry  # User input
# from tkinter import Entry  # A little uglier?
import sv_ttk

# For MS Windows related resolution errors
import ctypes
ctypes.windll.shcore.SetProcessDpiAwareness(2)  # Must be >= Windows 8.1

main_window = None
plot_window = None
plot_drawn = False
def main():

    # Window
    global main_window
    # width = main_window.winfo_screenwidth()
    main_window = tk.Tk()
    main_window.title("Investment Assistance")
    # main_window.geometry("1920x1080")
    # main_window.geometry("1280x720")
    # main_window.geometry("960x540")
    main_window.geometry("500x500")
    main_window.configure(bg="white")
    main_window.resizable(False, False)

    # global plot_drawn
    # if plot_drawn:
    #     print("Can draw plots")
    #     # global plot_window
    #     # plot_window = tk.Toplevel()
    #     # plot_window.title("Plots")
    #     # plot_window.geometry("960x540")
    #     # plot_window.configure(bg="white")
    #     # plot_window.resizable(False, False)
    # else:
    #     # TODO: remove previously drawn plots
    #     pass
    # global plot_window
    # plot_window = tk.Toplevel()
    # plot_window.title("Plots")
    # plot_window.geometry("960x540")
    # plot_window.configure(bg="white")
    # plot_window.resizable(False, False)

    # TODO: Put in own function
    screen_dpi = main_window.winfo_fpixels('1i')
    screen_width = main_window.winfo_screenwidth()
    screen_height = main_window.winfo_screenheight()
    print(f"Screen DPI: {screen_dpi}")
    print(f"Screen Width: {screen_width}")
    print(f"Screen Height: {screen_height}")
    main_window.update()
    window_dpi = main_window.winfo_fpixels('1i')
    window_width = main_window.winfo_width()
    window_height = main_window.winfo_height()
    print(f"Window DPI: {window_dpi}")
    print(f"Window Width: {window_width}")
    print(f"Window Height: {window_height}")

    # TODO: Probably move out of main
    # Colors
    color_search = "#729adb"
    color_display = "#de804e"

    # TODO: Put here until mainloop() in own function to mimic "while running" and put init vars outside of it
    # Create a label
    label_main = ttk.Label(main_window, text="Welcome! Let me assist you.")
    # label_main.grid(row=0, column=0, padx=20, pady=20)
    label_main.pack(side="top", fill="both", expand=True)

    # Create a canvas that hold the entry_stock, entry_sd, entry_ed, and button
    canvas_left = tk.Canvas(main_window, width=window_width * .5,
                       height=window_height, bg=color_search)
    # canvas_left.grid(row=1, column=0, padx=0, pady=0, sticky='W')
    # canvas_left.pack(side="left", fill="both", expand=True)
    canvas_left.pack(side="left", fill="both")

    canvas_left.update()
    cl_width = canvas_left.winfo_width()
    cl_height = canvas_left.winfo_height()
    print(f"Canvas Size: {cl_width}x{cl_height}")

    # # Create an Entry widget to accept User Input
    entry_stock = Entry(canvas_left, width=cl_width)
    entry_stock.insert(0, "Enter Stock Symbol")
    entry_stock.bind("<Button-1>", lambda event: entry_stock.delete(0, "end"))
    # entry_stock.grid(row=0, column=0, padx=20, pady=20)
    # Use pack to put entry_stock in the middle of the canvas
    entry_stock.pack(side="top", fill="both")
    entry_stock.focus_set()
    entry_stock.update()

    # Start date
    entry_sd = Entry(canvas_left, width=int(canvas_left.winfo_width() * .1))
    entry_sd.insert(0, "Enter a Start Date")
    entry_sd.bind("<Button-1>", lambda event: entry_sd.delete(0, "end"))
    # entry_sd.grid(row=1, column=0, padx=20, pady=20)
    entry_sd.pack(side="top", fill="both")
    entry_sd.focus_set()
    entry_sd.update()

    # End date
    entry_ed = Entry(canvas_left, width=int(canvas_left.winfo_width() * .1))
    entry_ed.insert(0, "Enter an End Date")
    entry_ed.bind("<Button-1>", lambda event: entry_ed.delete(0, "end"))
    # entry_ed.grid(row=2, column=0, padx=20, pady=20)
    entry_ed.pack(side="top", fill="both")
    entry_ed.focus_set()
    entry_ed.update()

    # All algorithms are run when this button is pressed.
    # button = ttk.Button(canvas_left, text="Run Algorithms", width=20, style="run_button.TButton",
    #                     command=lambda: run_search(entry_stock.get(), entry_sd.get(), entry_ed.get()))
    button = ttk.Button(canvas_left, text="Run Algorithms", width=20, style="run_button.TButton",
                        command=lambda: (plot_draw(), run_search(entry_stock.get(), entry_sd.get(), entry_ed.get())))

    # button.grid(row=3, column=0, padx=20, pady=20, ipadx=80, ipady=40)
    button.pack(side="top", fill="both")

    # TODO: Move somewhere else
    style = ttk.Style()
    style.configure("run_button.TButton", font=("Arial", 14))

    canvas_right = tk.Canvas(main_window, width=window_width * .5,
                       height=window_height, bg=color_display)
    # canvas_right.grid(row=0, column=1, padx=0, pady=0, sticky='E')
    canvas_right.pack(side="right", fill="both", expand=True)
    canvas_right.update()
    cr_width = canvas_right.winfo_width()
    cr_height = canvas_right.winfo_height()
    print(f"Canvas Size: {cr_width}x{cr_height}")

    # Set widgets theme
    # sv_ttk.set_theme("light")

    # main_window.resizable(True, True)
    main_window.mainloop()

    # Delete extra files when the program exits
    global stock_data_list
    for s_data in stock_data_list:
        os.remove(s_data)

def plot_draw():
    global plot_window
    plot_window = tk.Toplevel()
    plot_window.title("Plots")
    plot_window.geometry("960x540")
    plot_window.configure(bg="white")
    plot_window.resizable(False, False)

stock_data_list = []  # Holds the .csv data for each searched stock
plot_list = []
model_hi_lo = None
def run_search(stock, start_date, end_date):
    '''
        Inits and User Input
    '''
    print(stock)
    print(start_date)
    print(end_date)

    # Check all stock symbols to makes sure company exists
    global stock_data_list
    stock_exists = False
    with open("data/all_symbols.txt", "r") as f:
        for line in f:
            if stock in line:
                stock_exists = True
        f.close()

    '''
        Stock Data:
            - If the stock exists, ask for a start and end date
            - If the stock does not exist, ask for another stock symbol
    '''
    if stock_exists:

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
        print(regression_result)
        global plot_window
        regression.plot(plot_window)
        # macd_result = macd.macd_pred(stock_data)
        # svm_result = svm.svm_pred(stock_data)
        # random_forest.random_forest_pred(stock_data)
        # arima_result = arima.arima_pred(stock_data)
        # garch_result = garch.garch_pred(stock_data)
        # investor_analysis_result = investor_analysis.get_recommendations(stock)
        # sentimentAnalysis.sentiment_analysis_subreddit(stock)
        # sentimentAnalysisPretrainedBert.sentiment_analysis(stock)


        # TODO: This is really gross


        # # Add all results to list
        # results = [regression_result, macd_result, svm_result, arima_result, garch_result, investor_analysis_result]
        # # results = [regression_result, macd_result, svm_result]
        results = [regression_result]

        num_ones = sum(result == 1 for result in results)
        num_zeros = sum(result == 0 for result in results)

        if num_ones + num_zeros > 0:
            ratio = num_ones / (num_ones + num_zeros)
            percentage = ratio * 100
            print(f"There is a {percentage:.2f}% confidence level of {stock} stock performing well.")
        else:
            print("The results list is empty.")

        # return display_plots()

    else:
        print("Stock does not exist. Please try again.")


if __name__ == "__main__":
    main()