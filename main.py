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
import requests


# GUI
import tkinter as tk
from tkinter import ttk
from tkinter.ttk import Entry  # User input
from tkinter import scrolledtext
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
    main_window.title("Investment Assistant")
    # main_window.geometry("1920x1080")
    # main_window.geometry("1280x720")
    # main_window.geometry("960x540")
    # main_window.geometry("500x500")
    main_window.geometry("800x600")  # Apparently is the default min size for Windows apps
    main_window.configure(bg="white")
    main_window.resizable(False, False)

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
    color_search_light = "#e6e7e8"
    color_search_dark = "#141414"
    # Change color_search to a rgb tuple
    # color_search = (114, 154, 219)
    # Check for stable connection
    connection_text = " "
    if not check_connection():
        # End mainloop
        connection_text = "No internet. A stable connection is required to access yahoo finance."
    else:
        connection_text = "Stable connection found."


    # TODO: Put here until mainloop() in own function to mimic "while running" and put init vars outside of it
    # Create a label
    # main_window.wm_attributes('-transparentcolor', 'white')
    label_main = ttk.Label(main_window, text=connection_text)
    # Center the label
    label_main.pack(side="bottom", fill="both")
    # Change the label background color
    label_main.configure(background="#c4c4c4")

    # # Create a canvas that hold the entry_stock, entry_sd, entry_ed, and button
    # canvas_main = tk.Canvas(main_window, width=window_width * .5,
    #                    height=window_height, bg=main_window.cget("bg"), highlightthickness=0)
    # # canvas_main = tk.Canvas(main_window, width=window_width * .5,
    # #                    height=window_height, bg=color_search_dark)
    # canvas_main.pack(side="left", fill="both")
    #
    # canvas_main.update()

    # Make the canvas into a frame
    frame_main = tk.Frame(main_window, width=window_width * .5, height=window_height, bg=main_window.cget("bg"))
    frame_main.pack(side="left", fill="both")
    frame_main.update()

    cl_width = frame_main.winfo_width()
    cl_height = frame_main.winfo_height()
    print(f"Canvas Size: {cl_width}x{cl_height}")

    # # Create an Entry widget to accept User Input
    entry_stock = Entry(frame_main, width=cl_width)
    entry_stock.insert(0, "Enter Stock Symbol")
    entry_stock.bind("<Button-1>", lambda event: entry_stock.delete(0, "end"))
    entry_stock.pack(side="top", fill="both", padx=20, pady=10)
    entry_stock.focus_set()
    entry_stock.update()

    # Start date
    entry_sd = Entry(frame_main, width=int(frame_main.winfo_width() * .1))
    entry_sd.insert(0, "Enter a Start Date")
    entry_sd.bind("<Button-1>", lambda event: entry_sd.delete(0, "end"))
    entry_sd.pack(side="top", fill="both", padx=20, pady=10)
    entry_sd.focus_set()
    entry_sd.update()

    # End date
    entry_ed = Entry(frame_main, width=int(frame_main.winfo_width() * .1))
    entry_ed.insert(0, "Enter an End Date")
    entry_ed.bind("<Button-1>", lambda event: entry_ed.delete(0, "end"))
    entry_ed.pack(side="top", fill="both", padx=20, pady=10)
    entry_ed.focus_set()
    entry_ed.update()

    def create_loding_label():
        # Use a label instead of a text box for under the button
        loading_text = str(percentage_global) + "% confident level that " + entry_stock.get() + " will continue to perform well."
        label = ttk.Label(frame_main, text=loading_text)
        # label.pack(side="top", fill="both", padx=20, pady=10, ipadx=80, ipady=80)
        label.pack(side="top", fill="both", padx=20, pady=10)
        label.configure(background="red")
        label.update()

    # All algorithms are run when this button is pressed.
    button = ttk.Button(frame_main, text="Run Algorithms", width=20, style="run_button.TButton",
                        command=lambda: (plot_draw(), run_search(entry_stock.get(), entry_sd.get(), entry_ed.get()), create_loding_label()))
    button.pack(side="top", fill="both", padx=20, pady=10, ipadx=80, ipady=40)


    # TODO: Move somewhere else
    style = ttk.Style(main_window)
    # Using the built-in themes:
    #
    #     Available on all platform: alt, clam, classic, default
    #
    #     Windows: vista, winnative, xpnative
    #
    #     Mac: aqua

    # style.theme_use("clam")
    # style.configure("run_button.TButton", font=("Arial", 14))

    # Set theme
    # sv_ttk.set_theme("light")
    # Set the initial theme
    main_window.tk.call("source", "azure.tcl")
    main_window.tk.call("set_theme", "light")

    def change_theme():
        # NOTE: The theme's real name is azure-<mode>
        if main_window.tk.call("ttk::style", "theme", "use") == "azure-dark":
            # Set light theme
            main_window.tk.call("set_theme", "light")
        else:
            # Set dark theme
            main_window.tk.call("set_theme", "dark")

    # Remember, you have to use ttk widgets
    button = ttk.Button(frame_main, text="Change theme!", command=change_theme)
    button.pack(side="bottom", padx=20, pady=10)
    button.update()

    main_window.resizable(True, True)
    main_window.mainloop()

    # Delete extra files when the program exits
    global stock_data_list
    for s_data in stock_data_list:
        os.remove(s_data)

'''
    Need internet connection to gather data from yahoo finance
'''
def check_connection():
    # initializing URL
    # url = "https://www.google.com"  # Just to test connection
    url = "https://finance.yahoo.com"
    timeout = 10
    try:
        requests.get(url, timeout=timeout)
        print("Internet is on")
        return True

    # catching exception
    except (requests.ConnectionError, requests.Timeout) as exception:
        print("Internet is off")
        return False
def plot_draw():
    global plot_window
    plot_window = tk.Toplevel()
    plot_window.title("Plots")
    plot_window.geometry("800x600")
    plot_window.configure(bg="white")
    plot_window.resizable(True, True)
    plot_window.update()


stock_data_list = []  # Holds the .csv data for each searched stock
plot_list = []
model_hi_lo = None
percentage_global = 0
hi_lo_text = ""
macd_text = ""
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
        global plot_window
        # Create a scrolled text widget to hold the plots
        # text_widget = scrolledtext.ScrolledText(plot_window, width=100, height=30)
        # text_widget.pack(fill=tk.BOTH, expand=True)

        # Call the plots
        regression_result = regression.regression_pred(stock_data)  # Pass the csv file to objects
        print("hi_lo_result: ", regression_result)
        regression.plot(plot_window)
        # text_widget.insert(tk.END, '\n')  # Add a newline to separate the plots
        macd_result = macd.macd_pred(stock_data)
        print("macd_result: ", macd_result)
        macd.plot(plot_window)
        # svm_result = svm.svm_pred(stock_data)
        # random_forest.random_forest_pred(stock_data)
        # arima_result = arima.arima_pred(stock_data)
        # garch_result = garch.garch_pred(stock_data)
        # investor_analysis_result = investor_analysis.get_recommendations(stock)
        # sentimentAnalysis.sentiment_analysis_subreddit(stock)
        # sentimentAnalysisPretrainedBert.sentiment_analysis(stock)

        # Configure the scrollbar to scroll the text widget
        # scrollbar = tk.Scrollbar(plot_window, command=text_widget.yview)
        # scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        # text_widget.configure(yscrollcommand=scrollbar.set)


        # TODO: This is really gross


        # # Add all results to list
        # results = [regression_result, macd_result, svm_result, arima_result, garch_result, investor_analysis_result]
        # # results = [regression_result, macd_result, svm_result]
        results = [regression_result, macd_result]

        num_ones = sum(result == 1 for result in results)
        num_zeros = sum(result == 0 for result in results)

        if num_ones + num_zeros > 0:
            ratio = num_ones / (num_ones + num_zeros)
            percentage = ratio * 100
            # Force percentage to be 2 decimal places
            percentage = float("{:.2f}".format(percentage))
            print(f"There is a {percentage:.2f}% confidence level of {stock} stock performing well.")
            global percentage_global
            percentage_global = percentage
        else:
            print("The results list is empty.")

    else:
        print("Stock does not exist. Please try again.")


if __name__ == "__main__":
    main()