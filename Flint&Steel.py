import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import backtrader as bt
import datetime
import logging
import scipy.stats as stats
import math
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
import requests
from bs4 import BeautifulSoup
import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry
from PIL import Image, ImageTk
from tkinter import scrolledtext, filedialog

# Setup logging for the application
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Persistent Portfolio Class
class Portfolio:
    def __init__(self, initial_cash):
        self.cash = initial_cash
        self.holdings = {}
        self.transaction_history = []
    
    def add_ticker(self, ticker):
        if ticker not in self.holdings:
            self.holdings[ticker] = 0

    def buy(self, ticker, price, amount):
        total_cost = price * amount
        if total_cost > self.cash:
            logger.warning(f"Not enough cash to buy {amount} of {ticker}")
            return False
        self.cash -= total_cost
        self.holdings[ticker] += amount
        self.transaction_history.append({'ticker': ticker, 'price': price, 'amount': amount, 'type': 'buy', 'date': datetime.datetime.now()})
        logger.info(f"Bought {amount} of {ticker} at {price}. Cash left: {self.cash}")
        return True

    def sell(self, ticker, price, amount):
        if self.holdings[ticker] < amount:
            logger.warning(f"Not enough holdings to sell {amount} of {ticker}")
            return False
        self.cash += price * amount
        self.holdings[ticker] -= amount
        self.transaction_history.append({'ticker': ticker, 'price': price, 'amount': amount, 'type': 'sell', 'date': datetime.datetime.now()})
        logger.info(f"Sold {amount} of {ticker} at {price}. Cash after sale: {self.cash}")
        return True

    def portfolio_value(self, current_prices):
        value = self.cash
        for ticker, amount in self.holdings.items():
            value += current_prices.get(ticker, 0) * amount
        logger.info(f"Current portfolio value: {value}")
        return value

    def get_holdings_summary(self):
        return {ticker: amount for ticker, amount in self.holdings.items() if amount > 0}

# Data Retrieval using yfinance
class DataHandler:
    def __init__(self, tickers, start_date, end_date):
        self.tickers = tickers
        self.start_date = start_date
        self.end_date = end_date
        self.data = None
    
    def fetch_data(self):
        logger.info(f"Fetching data for {self.tickers} from {self.start_date} to {self.end_date}")
        self.data = yf.download(self.tickers, start=self.start_date, end=self.end_date)
        logger.info("Data fetching complete")
        return self.data

# Moving Average Strategy for Backtrader with Hyperparameters
class MovingAverageStrategy(bt.Strategy):
    params = (
        ('short_period', 50),
        ('long_period', 200),
        ('risk_percentage', 0.01),
        ('stop_loss', 0.02),
        ('take_profit', 0.05),
        ('printlog', False),
    )

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.order = None
        self.short_ma = bt.indicators.SimpleMovingAverage(self.datas[0], period=self.params.short_period)
        self.long_ma = bt.indicators.SimpleMovingAverage(self.datas[0], period=self.params.long_period)

    def log(self, txt, dt=None):
        if self.params.printlog:
            dt = dt or self.datas[0].datetime.date(0)
            logger.info(f'{dt.isoformat()} {txt}')

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'BUY EXECUTED, Price: {order.executed.price}')
            elif order.issell():
                self.log(f'SELL EXECUTED, Price: {order.executed.price}')
            self.bar_executed = len(self)
        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        self.log(f'OPERATION PROFIT, GROSS {trade.pnl:.2f}, NET {trade.pnlcomm:.2f}')

    def next(self):
        if self.order:
            return
        if self.short_ma > self.long_ma:
            if self.position.size == 0:
                self.order = self.buy()
        elif self.short_ma < self.long_ma:
            if self.position.size > 0:
                self.order = self.sell()

        # Implement Stop Loss and Take Profit
        if self.position.size > 0:
            if self.dataclose[0] >= self.position.price * (1 + self.params.take_profit):
                self.sell()
            elif self.dataclose[0] <= self.position.price * (1 - self.params.stop_loss):
                self.sell()

# Example RSI Strategy
class RSIStrategy(bt.Strategy):
    params = (
        ('rsi_period', 14),
        ('rsi_lower', 30),
        ('rsi_upper', 70),
    )

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.order = None
        self.rsi = bt.indicators.RSI_SMA(self.data.close, period=self.params.rsi_period)

    def next(self):
        if self.order:
            return
        if self.rsi < self.params.rsi_lower:
            if self.position.size == 0:
                self.order = self.buy()
        elif self.rsi > self.params.rsi_upper:
            if self.position.size > 0:
                self.order = self.sell()

# Example Bollinger Bands Strategy
class BollingerBandsStrategy(bt.Strategy):
    params = (
        ('bbands_period', 20),
        ('bbands_devfactor', 2.0),
    )

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.order = None
        self.bbands = bt.indicators.BollingerBands(self.datas[0], period=self.params.bbands_period, devfactor=self.params.bbands_devfactor)

    def next(self):
        if self.order:
            return
        if self.dataclose < self.bbands.lines.bot:
            if self.position.size == 0:
                self.order = self.buy()
        elif self.dataclose > self.bbands.lines.top:
            if self.position.size > 0:
                self.order = self.sell()

# Example MACD Strategy
class MACDStrategy(bt.Strategy):
    params = (
        ('macd1', 12),
        ('macd2', 26),
        ('signal', 9),
    )

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.order = None
        self.macd = bt.indicators.MACD(self.datas[0], period_me1=self.params.macd1, period_me2=self.params.macd2, period_signal=self.params.signal)

    def next(self):
        if self.order:
            return
        if self.macd.lines.macd > self.macd.lines.signal:
            if self.position.size == 0:
                self.order = self.buy()
        elif self.macd.lines.macd < self.macd.lines.signal:
            if self.position.size > 0:
                self.order = self.sell()

# Example Buy and Hold Strategy
class BuyAndHoldStrategy(bt.Strategy):
    def __init__(self):
        self.dataclose = self.datas[0].close
        self.order = None

    def next(self):
        if self.order:
            return
        if self.position.size == 0:
            self.order = self.buy()

# Metrics Dashboard
class MetricsDashboard:
    def __init__(self):
        self.metrics = {}

    def calculate_sharpe_ratio(self, returns, risk_free_rate=0.01):
        excess_returns = returns - risk_free_rate
        sharpe_ratio = np.mean(excess_returns) / np.std(excess_returns)
        logger.info(f"Sharpe Ratio: {sharpe_ratio:.2f}")
        self.metrics['Sharpe Ratio'] = sharpe_ratio
        return sharpe_ratio

    def calculate_max_drawdown(self, portfolio_values):
        drawdowns = portfolio_values / np.maximum.accumulate(portfolio_values) - 1
        max_drawdown = np.min(drawdowns)
        logger.info(f"Maximum Drawdown: {max_drawdown:.2%}")
        self.metrics['Max Drawdown'] = max_drawdown
        return max_drawdown

    def calculate_total_return(self, start_value, end_value):
        total_return = (end_value - start_value) / start_value
        logger.info(f"Total Return: {total_return:.2%}")
        self.metrics['Total Return'] = total_return
        return total_return

    def display_metrics(self, text_widget):
        text_widget.delete(1.0, tk.END)
        text_widget.insert(tk.END, "Metrics Summary:\n\n")
        for metric, value in self.metrics.items():
            if metric == 'Max Drawdown':
                text_widget.insert(tk.END, f"{metric}: {value:.2%} (Max loss from peak)\n")
            elif metric == 'Sharpe Ratio':
                text_widget.insert(tk.END, f"{metric}: {value:.2f} (Risk-adjusted return)\n")
            elif metric == 'Total Return':
                text_widget.insert(tk.END, f"{metric}: {value:.2%} (Overall portfolio growth)\n")
            else:
                text_widget.insert(tk.END, f"{metric}: {value:.2f}\n")
        logger.info("Metrics Dashboard updated")

# GUI Setup with Tkinter
class TradingPlatformGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Flint&Steel Backtesting Platform")
        self.portfolio = Portfolio(initial_cash=100000)
        self.custom_script = None
        self.setup_gui()

    def setup_gui(self):
        # Main Frame
        self.main_frame = ttk.Frame(self.root, padding="10 10 10 10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Ticker Input Frame
        self.ticker_frame = ttk.LabelFrame(self.main_frame, text="Ticker Input")
        self.ticker_frame.grid(row=0, column=0, padx=10, pady=10, sticky=(tk.W, tk.E))

        self.ticker_label = ttk.Label(self.ticker_frame, text="Enter Ticker:")
        self.ticker_label.grid(row=0, column=0, padx=5, pady=5)

        self.ticker_entry = ttk.Combobox(self.ticker_frame, values=self.get_ticker_list())
        self.ticker_entry.grid(row=0, column=1, padx=5, pady=5)

        self.start_date_label = ttk.Label(self.ticker_frame, text="Start Date:")
        self.start_date_label.grid(row=1, column=0, padx=5, pady=5)

        self.start_date_entry = DateEntry(self.ticker_frame, width=12, background='darkblue',
                                          foreground='white', borderwidth=2, year=2022, month=1, day=1)
        self.start_date_entry.grid(row=1, column=1, padx=5, pady=5)

        self.end_date_label = ttk.Label(self.ticker_frame, text="End Date:")
        self.end_date_label.grid(row=2, column=0, padx=5, pady=5)

        self.end_date_entry = DateEntry(self.ticker_frame, width=12, background='darkblue',
                                        foreground='white', borderwidth=2, year=2023, month=9, day=1)
        self.end_date_entry.grid(row=2, column=1, padx=5, pady=5)

        self.submit_button = ttk.Button(self.ticker_frame, text="Submit", command=self.submit_ticker)
        self.submit_button.grid(row=3, column=1, padx=5, pady=5)

        # Strategy Selection Frame
        self.strategy_frame = ttk.LabelFrame(self.main_frame, text="Backtesting Strategy")
        self.strategy_frame.grid(row=1, column=0, padx=10, pady=10, sticky=(tk.W, tk.E))

        self.strategy_label = ttk.Label(self.strategy_frame, text="Select Strategy:")
        self.strategy_label.grid(row=0, column=0, padx=5, pady=5)

        self.strategy_options = ttk.Combobox(self.strategy_frame, values=['Moving Average', 'RSI', 'Bollinger Bands', 'MACD', 'Buy and Hold'])
        self.strategy_options.grid(row=0, column=1, padx=5, pady=5)
        self.strategy_options.bind("<<ComboboxSelected>>", self.update_hyperparameters)

        # Hyperparameters Frame
        self.hyperparameters_frame = ttk.LabelFrame(self.main_frame, text="Strategy Hyperparameters")
        self.hyperparameters_frame.grid(row=2, column=0, padx=10, pady=10, sticky=(tk.W, tk.E))

        # Set up dynamic hyperparameters widgets (initially empty)
        self.hyperparameter_widgets = {}

        # Metrics Display Frame
        self.metrics_frame = ttk.LabelFrame(self.main_frame, text="Metrics Dashboard")
        self.metrics_frame.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky=(tk.W, tk.E))

        self.metrics_text = tk.Text(self.metrics_frame, width=60, height=10)
        self.metrics_text.grid(row=0, column=0, padx=10, pady=10)

        # Backtest Button
        self.backtest_button = ttk.Button(self.main_frame, text="Run Backtest", command=self.run_predefined_backtest)
        self.backtest_button.grid(row=4, column=0, padx=10, pady=10)

        # Custom Script Section
        self.custom_script_frame = ttk.LabelFrame(self.main_frame, text="Custom Backtest Script")
        self.custom_script_frame.grid(row=0, column=1, rowspan=4, padx=10, pady=10, sticky=(tk.N, tk.S, tk.E, tk.W))

        self.custom_script_editor = scrolledtext.ScrolledText(self.custom_script_frame, wrap=tk.WORD, width=40, height=20)
        self.custom_script_editor.grid(row=0, column=0, padx=10, pady=10)

        self.load_script_button = ttk.Button(self.custom_script_frame, text="Load Script", command=self.load_script)
        self.load_script_button.grid(row=1, column=0, padx=5, pady=5, sticky=(tk.W, tk.E))

        self.run_custom_backtest_button = ttk.Button(self.custom_script_frame, text="Run Custom Backtest", command=self.run_custom_backtest)
        self.run_custom_backtest_button.grid(row=2, column=0, padx=5, pady=5, sticky=(tk.W, tk.E))

    def get_ticker_list(self):
        return ['SOXL', 'VFV.TO', 'VOO', 'NVDA', 'TSLA', 'META', 'MSFT']

    def submit_ticker(self):
        ticker = self.ticker_entry.get().upper()
        start_date = self.start_date_entry.get_date().strftime('%Y-%m-%d')
        end_date = self.end_date_entry.get_date().strftime('%Y-%m-%d')
        sentiment = SentimentAnalysis(ticker).analyze_sentiment()
        self.metrics_text.insert(tk.END, f"Sentiment Score for {ticker}: {sentiment}\n")
        logger.info(f"Ticker submitted: {ticker}")

    def update_hyperparameters(self, event):
        strategy = self.strategy_options.get()
        for widget in self.hyperparameter_widgets.values():
            widget.grid_forget()
        self.hyperparameter_widgets = {}

        if strategy == 'Moving Average':
            self.hyperparameter_widgets['short_ma_label'] = ttk.Label(self.hyperparameters_frame, text="Short MA Period:")
            self.hyperparameter_widgets['short_ma_label'].grid(row=0, column=0, padx=5, pady=5)
            self.hyperparameter_widgets['short_ma_entry'] = ttk.Entry(self.hyperparameters_frame)
            self.hyperparameter_widgets['short_ma_entry'].grid(row=0, column=1, padx=5, pady=5)

            self.hyperparameter_widgets['long_ma_label'] = ttk.Label(self.hyperparameters_frame, text="Long MA Period:")
            self.hyperparameter_widgets['long_ma_label'].grid(row=1, column=0, padx=5, pady=5)
            self.hyperparameter_widgets['long_ma_entry'] = ttk.Entry(self.hyperparameters_frame)
            self.hyperparameter_widgets['long_ma_entry'].grid(row=1, column=1, padx=5, pady=5)

            self.hyperparameter_widgets['risk_label'] = ttk.Label(self.hyperparameters_frame, text="Risk Percentage:")
            self.hyperparameter_widgets['risk_label'].grid(row=2, column=0, padx=5, pady=5)
            self.hyperparameter_widgets['risk_entry'] = ttk.Entry(self.hyperparameters_frame)
            self.hyperparameter_widgets['risk_entry'].grid(row=2, column=1, padx=5, pady=5)

            self.hyperparameter_widgets['stop_loss_label'] = ttk.Label(self.hyperparameters_frame, text="Stop Loss:")
            self.hyperparameter_widgets['stop_loss_label'].grid(row=3, column=0, padx=5, pady=5)
            self.hyperparameter_widgets['stop_loss_entry'] = ttk.Entry(self.hyperparameters_frame)
            self.hyperparameter_widgets['stop_loss_entry'].grid(row=3, column=1, padx=5, pady=5)

            self.hyperparameter_widgets['take_profit_label'] = ttk.Label(self.hyperparameters_frame, text="Take Profit:")
            self.hyperparameter_widgets['take_profit_label'].grid(row=4, column=0, padx=5, pady=5)
            self.hyperparameter_widgets['take_profit_entry'] = ttk.Entry(self.hyperparameters_frame)
            self.hyperparameter_widgets['take_profit_entry'].grid(row=4, column=1, padx=5, pady=5)

        elif strategy == 'RSI':
            self.hyperparameter_widgets['rsi_period_label'] = ttk.Label(self.hyperparameters_frame, text="RSI Period:")
            self.hyperparameter_widgets['rsi_period_label'].grid(row=0, column=0, padx=5, pady=5)
            self.hyperparameter_widgets['rsi_period_entry'] = ttk.Entry(self.hyperparameters_frame)
            self.hyperparameter_widgets['rsi_period_entry'].grid(row=0, column=1, padx=5, pady=5)

            self.hyperparameter_widgets['rsi_lower_label'] = ttk.Label(self.hyperparameters_frame, text="RSI Lower:")
            self.hyperparameter_widgets['rsi_lower_label'].grid(row=1, column=0, padx=5, pady=5)
            self.hyperparameter_widgets['rsi_lower_entry'] = ttk.Entry(self.hyperparameters_frame)
            self.hyperparameter_widgets['rsi_lower_entry'].grid(row=1, column=1, padx=5, pady=5)

            self.hyperparameter_widgets['rsi_upper_label'] = ttk.Label(self.hyperparameters_frame, text="RSI Upper:")
            self.hyperparameter_widgets['rsi_upper_label'].grid(row=2, column=0, padx=5, pady=5)
            self.hyperparameter_widgets['rsi_upper_entry'] = ttk.Entry(self.hyperparameters_frame)
            self.hyperparameter_widgets['rsi_upper_entry'].grid(row=2, column=1, padx=5, pady=5)

        elif strategy == 'Bollinger Bands':
            self.hyperparameter_widgets['bbands_period_label'] = ttk.Label(self.hyperparameters_frame, text="BBands Period:")
            self.hyperparameter_widgets['bbands_period_label'].grid(row=0, column=0, padx=5, pady=5)
            self.hyperparameter_widgets['bbands_period_entry'] = ttk.Entry(self.hyperparameters_frame)
            self.hyperparameter_widgets['bbands_period_entry'].grid(row=0, column=1, padx=5, pady=5)

            self.hyperparameter_widgets['bbands_devfactor_label'] = ttk.Label(self.hyperparameters_frame, text="BBands Dev Factor:")
            self.hyperparameter_widgets['bbands_devfactor_label'].grid(row=1, column=0, padx=5, pady=5)
            self.hyperparameter_widgets['bbands_devfactor_entry'] = ttk.Entry(self.hyperparameters_frame)
            self.hyperparameter_widgets['bbands_devfactor_entry'].grid(row=1, column=1, padx=5, pady=5)

        elif strategy == 'MACD':
            self.hyperparameter_widgets['macd1_label'] = ttk.Label(self.hyperparameters_frame, text="MACD Fast Period:")
            self.hyperparameter_widgets['macd1_label'].grid(row=0, column=0, padx=5, pady=5)
            self.hyperparameter_widgets['macd1_entry'] = ttk.Entry(self.hyperparameters_frame)
            self.hyperparameter_widgets['macd1_entry'].grid(row=0, column=1, padx=5, pady=5)

            self.hyperparameter_widgets['macd2_label'] = ttk.Label(self.hyperparameters_frame, text="MACD Slow Period:")
            self.hyperparameter_widgets['macd2_label'].grid(row=1, column=0, padx=5, pady=5)
            self.hyperparameter_widgets['macd2_entry'] = ttk.Entry(self.hyperparameters_frame)
            self.hyperparameter_widgets['macd2_entry'].grid(row=1, column=1, padx=5, pady=5)

            self.hyperparameter_widgets['signal_label'] = ttk.Label(self.hyperparameters_frame, text="Signal Period:")
            self.hyperparameter_widgets['signal_label'].grid(row=2, column=0, padx=5, pady=5)
            self.hyperparameter_widgets['signal_entry'] = ttk.Entry(self.hyperparameters_frame)
            self.hyperparameter_widgets['signal_entry'].grid(row=2, column=1, padx=5, pady=5)

    def run_predefined_backtest(self):
        ticker = self.ticker_entry.get().upper()
        start_date = self.start_date_entry.get_date().strftime('%Y-%m-%d')
        end_date = self.end_date_entry.get_date().strftime('%Y-%m-%d')
        initial_cash = 100000

        data_handler = DataHandler([ticker], start_date, end_date)
        data = data_handler.fetch_data()

        cerebro = bt.Cerebro()

        strategy = self.strategy_options.get()
        if strategy == 'Moving Average':
            short_period = int(self.hyperparameter_widgets['short_ma_entry'].get()) if 'short_ma_entry' in self.hyperparameter_widgets else 50
            long_period = int(self.hyperparameter_widgets['long_ma_entry'].get()) if 'long_ma_entry' in self.hyperparameter_widgets else 200
            risk_percentage = float(self.hyperparameter_widgets['risk_entry'].get()) if 'risk_entry' in self.hyperparameter_widgets else 0.01
            stop_loss = float(self.hyperparameter_widgets['stop_loss_entry'].get()) if 'stop_loss_entry' in self.hyperparameter_widgets else 0.02
            take_profit = float(self.hyperparameter_widgets['take_profit_entry'].get()) if 'take_profit_entry' in self.hyperparameter_widgets else 0.05

            cerebro.addstrategy(MovingAverageStrategy, short_period=short_period, long_period=long_period, 
                                risk_percentage=risk_percentage, stop_loss=stop_loss, take_profit=take_profit)

        elif strategy == 'RSI':
            rsi_period = int(self.hyperparameter_widgets['rsi_period_entry'].get()) if 'rsi_period_entry' in self.hyperparameter_widgets else 14
            rsi_lower = int(self.hyperparameter_widgets['rsi_lower_entry'].get()) if 'rsi_lower_entry' in self.hyperparameter_widgets else 30
            rsi_upper = int(self.hyperparameter_widgets['rsi_upper_entry'].get()) if 'rsi_upper_entry' in self.hyperparameter_widgets else 70

            cerebro.addstrategy(RSIStrategy, rsi_period=rsi_period, rsi_lower=rsi_lower, rsi_upper=rsi_upper)

        elif strategy == 'Bollinger Bands':
            bbands_period = int(self.hyperparameter_widgets['bbands_period_entry'].get()) if 'bbands_period_entry' in self.hyperparameter_widgets else 20
            bbands_devfactor = float(self.hyperparameter_widgets['bbands_devfactor_entry'].get()) if 'bbands_devfactor_entry' in self.hyperparameter_widgets else 2.0

            cerebro.addstrategy(BollingerBandsStrategy, bbands_period=bbands_period, bbands_devfactor=bbands_devfactor)

        elif strategy == 'MACD':
            macd1 = int(self.hyperparameter_widgets['macd1_entry'].get()) if 'macd1_entry' in self.hyperparameter_widgets else 12
            macd2 = int(self.hyperparameter_widgets['macd2_entry'].get()) if 'macd2_entry' in self.hyperparameter_widgets else 26
            signal = int(self.hyperparameter_widgets['signal_entry'].get()) if 'signal_entry' in self.hyperparameter_widgets else 9

            cerebro.addstrategy(MACDStrategy, macd1=macd1, macd2=macd2, signal=signal)

        elif strategy == 'Buy and Hold':
            cerebro.addstrategy(BuyAndHoldStrategy)

        data_feed = bt.feeds.PandasData(dataname=data)
        cerebro.adddata(data_feed)

        cerebro.broker.setcash(initial_cash)
        cerebro.addanalyzer(bt.analyzers.TimeReturn, _name='returns')
        strat = cerebro.run()
        strat = strat[0]

        # Retrieve the TimeReturn analyzer to get the returns
        portfolio_returns = strat.analyzers.returns.get_analysis()

        # Convert the returns to a cumulative portfolio value
        portfolio_values = np.cumprod([1 + r for r in portfolio_returns.values()]) * initial_cash

        final_value = cerebro.broker.getvalue()
        logger.info(f"Final Portfolio Value after Backtest: {final_value}")

        # Update Metrics Dashboard
        dashboard = MetricsDashboard()
        dashboard.calculate_total_return(initial_cash, final_value)
        returns = data['Close'].pct_change().dropna()
        dashboard.calculate_sharpe_ratio(returns)
        dashboard.calculate_max_drawdown(portfolio_values)
        dashboard.display_metrics(self.metrics_text)

        # Annotated Backtesting Graph
        cerebro.plot(style='candlestick')
        self.display_backtest_summary()

    def display_backtest_summary(self):
        summary_window = tk.Toplevel(self.root)
        summary_window.title("Backtest Summary")

        summary_label = ttk.Label(summary_window, text="Backtest Graph Components Explained", font=("Arial", 12, "bold"))
        summary_label.pack(pady=10)

        explanations = [
            "1. **Red Line (Cash)**: This represents the cash available in your portfolio throughout the backtest.",
            "2. **Blue Line (Portfolio Value)**: Shows the total value of your portfolio over time, including both cash and asset values.",
            "3. **Red Circles (Negative Trades)**: Indicate trades that resulted in a loss.",
            "4. **Blue Circles (Positive Trades)**: Indicate trades that resulted in a profit.",
            "5. **Green Triangles (Buy Signals)**: Points where the strategy executed a buy order.",
            "6. **Red Triangles (Sell Signals)**: Points where the strategy executed a sell order.",
            "7. **Blue Line (Long Moving Average)**: Represents the long-period moving average.",
            "8. **Red Line (Short Moving Average)**: Represents the short-period moving average."
        ]

        for explanation in explanations:
            ttk.Label(summary_window, text=explanation, wraplength=400, justify=tk.LEFT).pack(anchor="w", padx=10, pady=2)

        close_button = ttk.Button(summary_window, text="Close", command=summary_window.destroy)
        close_button.pack(pady=10)

    def load_script(self):
        script_path = filedialog.askopenfilename(filetypes=[("Python Files", "*.py")])
        if script_path:
            with open(script_path, 'r') as file:
                self.custom_script_editor.delete(1.0, tk.END)
                self.custom_script_editor.insert(tk.END, file.read())
                self.custom_script = script_path
            logger.info(f"Loaded script from {script_path}")

    def run_custom_backtest(self):
        if self.custom_script:
            exec(open(self.custom_script).read())
        else:
            logger.warning("No script loaded.")

# Sentiment Analysis Module
class SentimentAnalysis:
    def __init__(self, ticker):
        self.ticker = ticker
    
    def fetch_news(self):
        url = f"https://news.google.com/search?q={self.ticker}"
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        headlines = [h.text for h in soup.find_all('a', class_='DY5T1d RZIKme')]
        return headlines
    
    def analyze_sentiment(self):
        headlines = self.fetch_news()
        sentiment_score = 0
        for headline in headlines:
            if "up" in headline or "good" in headline:
                sentiment_score += 1
            elif "down" in headline or "bad" in headline:
                sentiment_score -= 1
        logger.info(f"Sentiment score for {self.ticker}: {sentiment_score}")
        return sentiment_score

# Example usage of the GUI
if __name__ == "__main__":
    root = tk.Tk()
    app = TradingPlatformGUI(root)
    root.mainloop()
