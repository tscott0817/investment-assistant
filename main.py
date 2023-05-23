import os
import time
import yfinance as yf
import hi_lo
import macd
import svm
import investor_analysis
# import sentimentAnalysis
# import sentimentAnalysisPretrainedBert
import arima
import garch
import random_forest
import requests
import types
import typing


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
frame_main = None
def main():

    # Window
    global main_window
    main_window = tk.Tk()
    main_window.title("Investment Assistant")
    # main_window.geometry("1920x1080")
    # main_window.geometry("1280x720")
    # main_window.geometry("960x540")
    # main_window.geometry("500x500")
    # main_window.geometry("800x600")  # Apparently is the default min size for Windows apps?
    main_window.configure(bg="white")
    main_window.resizable(True, True)

    width_main_window: int = 1280  # width for the Tk root
    height_main_window: int = 720  # height for the Tk root

    # get screen width and height
    width_screen: int = main_window.winfo_screenwidth()  # width of the screen
    height_screen: int = main_window.winfo_screenheight()  # height of the screen

    # calculate x and y coordinates for the Tk root window
    pos_x: float = (width_screen / 2) - (width_main_window / 2)
    pos_y: float = (height_screen / 2) - (height_main_window / 2)

    # set the dimensions of the screen
    # and where it is placed
    main_window.geometry('%dx%d+%d+%d' % (width_main_window, height_main_window, pos_x, pos_y))

    # TODO: Put in own function
    # screen_dpi = main_window.winfo_fpixels('1i')
    # screen_width = main_window.winfo_screenwidth()
    # screen_height = main_window.winfo_screenheight()
    # print(f"Screen DPI: {screen_dpi}")
    # print(f"Screen Width: {screen_width}")
    # print(f"Screen Height: {screen_height}")
    # main_window.update()
    # window_dpi = main_window.winfo_fpixels('1i')
    # window_width = main_window.winfo_width()
    # window_height = main_window.winfo_height()
    # print(f"Window DPI: {window_dpi}")
    # print(f"Window Width: {window_width}")
    # print(f"Window Height: {window_height}")

    # TODO: Probably move out of main
    # Colors
    color_search = "#729adb"
    color_search_light = "#e6e7e8"
    color_search_dark = "#141414"
    if not check_connection():
        # End mainloop
        connection_text = "No internet. A stable connection is required to access yahoo finance."
    else:
        connection_text = "Stable connection found."


    # TODO: Put here until mainloop() in own function to mimic "while running" and put init vars outside of it
    # Create a label
    label_main = ttk.Label(main_window, text=connection_text)
    label_main.pack(side="bottom", fill="both")
    label_main.configure(background="#c4c4c4")

    # Make the canvas into a frame
    global frame_main
    frame_main = tk.Frame(main_window, width=width_main_window * .05, height=height_main_window, bg=main_window.cget("bg"))
    # frame_main = tk.Frame(main_window, width=window_width * .05, height=window_height, bg="red")
    # frame_main.pack(side="left", fill="both", expand=True)
    frame_main.pack(side="left", fill="both")
    # Make the frame half the canvas width

    frame_main.pack(side="left")
    frame_main.update()

    cl_width: int = frame_main.winfo_width()
    cl_height: int = frame_main.winfo_height()
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

    def create_loading_label():
        # Use a label instead of a text box for under the button
        loading_text = str(percentage_global) + "% confident level that " + entry_stock.get() + " will continue to perform well."
        label = ttk.Label(frame_main, text=loading_text)
        label.pack(side="top", fill="both", padx=20, pady=10)
        label.configure(background="red")
        label.update()

    # All algorithms are run when this button is pressed.
    button = ttk.Button(frame_main, text="Analyze", width=20, style="run_button.TButton",
                        command=lambda: (plot_draw(), run_search(entry_stock.get(), entry_sd.get(), entry_ed.get()), create_loading_label()))
    button.pack(side="top", fill="both", padx=20, pady=10, ipadx=80, ipady=10)


    # TODO: Move somewhere else
    # Using the built-in themes:
    #     Available on all platform: alt, clam, classic, default
    #     Windows: vista, winnative, xpnative
    #     Mac: aqua

    # style = ttk.Style(main_window)
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
    url: str = "https://finance.yahoo.com"
    timeout: int = 10
    try:
        requests.get(url, timeout=timeout)
        print("Internet is on")
        return True

    # catching exception
    except (requests.ConnectionError, requests.Timeout) as exception:
        print("Internet is off")
        return False

plots_frame = None
frame_plot = None
canvas_plot = None
scrollbar_plot = None

def plot_draw():
    global plots_frame
    global frame_plot
    global canvas_plot
    global scrollbar_plot

    # # Create a frame to hold the canvas and scrollbar
    if plots_frame is not None:
        plots_frame.destroy()
        frame_plot.destroy()
        canvas_plot.destroy()
        # scrollbar_plot.destroy()

    frame_plot = ttk.Frame(main_window)
    frame_plot.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
    # Recreate the frame each time this function is called

    # Calculate the width for the frame
    frame_width = int(main_window.winfo_width() / 4)

    # Configure the frame width
    frame_plot.config(width=frame_width)

    # Create a canvas for the plots
    canvas_plot = tk.Canvas(frame_plot)
    canvas_plot.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Create a scrollbar
    scrollbar = ttk.Scrollbar(frame_plot, orient=tk.VERTICAL, command=canvas_plot.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # Configure the canvas to use the scrollbar
    canvas_plot.configure(yscrollcommand=scrollbar.set, highlightthickness=0)
    canvas_plot.bind('<Configure>', lambda e: canvas_plot.configure(scrollregion=canvas_plot.bbox('all')))

    # Enable mouse wheel scrolling
    canvas_plot.bind_all("<MouseWheel>", lambda e: canvas_plot.yview_scroll(int(-1 * (e.delta / 120)), "units"))

    # Create a frame to hold the plots
    plots_frame = ttk.Frame(canvas_plot)

    # Add the plots frame to the canvas
    canvas_plot.create_window((0, 0), window=plots_frame, anchor=tk.NW)

    def on_window_resize(event):
        canvas_plot.itemconfig(1, width=canvas_plot.winfo_width())

    def configure_scrollbar():
        canvas_plot.update_idletasks()
        canvas_plot.config(scrollregion=canvas_plot.bbox('all'))
        if plots_frame.winfo_reqheight() > canvas_plot.winfo_height():
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        else:
            scrollbar.pack_forget()

    main_window.bind("<Configure>", on_window_resize)
    main_window.after(10, configure_scrollbar)  # Delay execution to allow time for widget creation



# TODO: If I want to add loading text to each algo
#   I need to separate each algo into its own function
#   Call each sequentially as a callback in the button press lambda
#   Then display the text in the main window when each algo starts and finishes.
stock_data_list: list = []  # Holds the .csv data for each searched stock
plot_list: list = []
model_hi_lo = None
percentage_global: float = 0
hi_lo_text: str = ""
macd_text: str = ""
def run_search(stock: str, start_date: str, end_date: str):
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
        # global plot_window
        # Call the plots
        regression_result = hi_lo.regression_pred(stock_data)  # Pass the csv file to objects
        print("hi_lo_result: ", regression_result)
        hi_lo.plot(plots_frame)
        # text_widget.insert(tk.END, '\n')  # Add a newline to separate the plots
        macd_result = macd.macd_pred(stock_data)
        print("macd_result: ", macd_result)
        macd.plot(plots_frame)
        svm_result = svm.svm_pred(stock_data)
        print("svm_result: ", svm_result)
        svm.plot(plots_frame)
        # random_forest.random_forest_pred(stock_data)
        # print("random_forest_result: ", random_forest.random_forest_pred(stock_data))
        # random_forest.plot(plots_frame)
        # arima_result = arima.arima_pred(stock_data)
        # print("arima_result: ", arima_result)
        # arima.plot(plots_frame)
        # garch_result = garch.garch_pred(stock_data)
        # print("garch_result: ", garch_result)
        # garch.plot(plots_frame)
        # investor_analysis_result = investor_analysis.get_recommendations(stock)
        # print("investor_analysis_result: ", investor_analysis_result)
        # investor_analysis.plot(plots_frame)
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
        results = [regression_result, macd_result, svm_result]

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