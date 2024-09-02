# 🔥 Flint & Steel Backtesting Platform

**Flint & Steel Backtesting Platform** is an advanced Python application designed for quantitative analysts and traders looking to rigorously backtest and optimize trading strategies across a diverse range of financial instruments. With a focus on ease of use and powerful capabilities, this platform allows you to simulate trades on ETFs like SOXL, VFV, and VOO, as well as stocks such as NVIDIA, TESLA, META, and MICROSOFT.

## 📷 Screenshots

### 1. **Main Dashboard**
   ![Main Dashboard](https://github.com/user-attachments/assets/8527f159-ad6f-444b-b03c-2398def2d049)
   - **Description:** The main dashboard provides an overview of the various features on the platform.

### 2. **Date Configuration**
   ![Strategy Configuration](https://github.com/user-attachments/assets/584ae3ab-e2be-47ba-ae17-cca3337fb539)
   - **Description:** Users are able to select a ticker and date interval to backtest their strategy.

### 3. **Backtesting & Hyperparameters**
   ![Backtesting Results](https://github.com/user-attachments/assets/589a1b9a-bf28-43f8-ac9e-779de01bf1b9)
   - **Description:** Here users select their backtesting strategy from a dropdown list (or custom uploaded python script) and adjust hyperparameters as required. 

### 4. **RSI**
   ![Trade Execution Log](https://github.com/user-attachments/assets/e37cc786-2353-4a24-8672-0bc43fe3c32e)
   - **Description:** 1 out of 5 the backtesting strategies readily available with tunable hyperparameters.

### 5. **Bollinger Bands**
   ![Real-Time Simulation](https://github.com/user-attachments/assets/5d4f2a6c-e07b-4162-b622-ff7fa407af80)
   - **Description:** 2nd available backtesting strategy.

### 6. **Portfolio**
   ![Portfolio Management](https://github.com/user-attachments/assets/a8ba92a8-d837-43d9-8b97-534678479b05)
   - **Description:** Red Line (Cash): Represents the cash available in your portfolio throughout the backtest. The value on the right indicates the cash balance at the end of the backtest. Blue Line (Portfolio Value): This line shows the total value of your portfolio over time, including both the cash and the value of the assets held. The value on the rightshows the final portfolio value.

### 7. **Performance Analysis**
   ![Performance Analysis](https://github.com/user-attachments/assets/bfadcd6a-59e2-43c7-b744-e75cf90bc2ca)
   - **Description:** Red Circles (Negative Trades): These markers indicate trades that resulted in a loss. Blue Circles (Positive Trades): These markers indicate trades that resulted in a profit.

### 8. **Price Chart**
   ![Optimization Tools](https://github.com/user-attachments/assets/a4ecd957-498e-4d7a-9764-9642e8b18370)
   - **Black Line (Price):** This is the price movement of the asset (e.g., a stock) over time.
   - **Green Triangles (Buy Signals):** These indicate the points where the strategy executed a buy order.
   - **Red Triangles (Sell Signals):** These indicate the points where the strategy executed a sell order.
   - **Blue Line (Simple Moving Average - 100):** This line represents the long-period moving average (100 in this case), which is a smoothened version of the price to show long-term trends.
   - **Red Line (Simple Moving Average - 20):** This line represents the short-period moving average (20 in this case), which responds more quickly to price changes.

## 🚀 Key Features

- **🕒 Real-Time Trading Simulation:**
  - Simulate real-time trading scenarios with live market data, providing a realistic environment for strategy testing.
  
- **📈 Comprehensive Backtesting:**
  - Leverage historical data from `yfinance` to backtest trading strategies across various timeframes, with support for advanced metrics and performance evaluation.

- **💹 Diverse Portfolio Management:**
  - Create and manage a customizable portfolio of ETFs and stocks, adjusting allocations and rebalancing as needed.

- **🔧 Strategy Optimization:**
  - Optimize your trading strategies using built-in statistical and machine learning tools to enhance performance and profitability.

- **🖥️ Interactive GUI:**
  - A professional and user-friendly interface built with PyQt, enabling intuitive strategy configuration, backtesting, and result visualization.

## 🔍 Project Structure

### 1. **Main Application (`Flint&Steel.py`):**
   - The core script that launches the Flint & Steel Backtesting Platform GUI.
   - Handles initialization of all modules, sets up the user interface, and integrates all features such as real-time trading, backtesting, and portfolio management.

### 2. **Trading Strategies Module:**
   - **Implementation:** Provides a variety of trading strategies like moving averages, momentum trading, mean reversion, and more.
   - **Customization:** Users can define parameters for each strategy, enabling tailored testing and optimization.
   - **Visualization:** Includes tools to visualize strategy performance, compare different strategies, and analyze trade execution.

### 3. **Backtesting Engine:**
   - **Data Integration:** Pulls historical data via `yfinance`, with support for custom data sources.
   - **Analysis:** Provides detailed performance reports, including metrics like Sharpe ratio, maximum drawdown, and volatility.
   - **Execution:** Executes trades based on strategy signals, allowing users to simulate portfolio performance over time.

### 4. **Real-Time Trading Simulation:**
   - **Live Data Feed:** Simulates a live trading environment using real-time market data.
   - **Order Execution:** Mimics the order execution process, including market and limit orders, to assess how strategies perform under live conditions.

### 5. **Portfolio Management:**
   - **Asset Allocation:** Manage and rebalance portfolios, track holdings, and evaluate portfolio performance.
   - **Risk Management:** Includes features for stop-loss, take-profit, and risk-adjusted return analysis.

## ⚙️ Installation Guide

### Prerequisites:
- Python 3.8 or higher
- Required Python packages (`PyQt5`, `yfinance`, `pandas`, `numpy`, `matplotlib`, etc.)

### Steps to Install:
1. **Clone the Repository:**
   ```bash
   git clone https://github.com/yourusername/FlintAndSteel.git
   cd FlintAndSteel
   ```

2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Application:**
   ```bash
   python Flint&Steel.py
   ```

## 💻 Usage

### 1. **Configure Your Strategy:**
   - Use the intuitive GUI to select your desired trading strategy, adjust parameters, and set up the backtesting environment.

### 2. **Run Backtesting:**
   - Evaluate your strategy against historical data, with detailed reports and visualizations provided for performance analysis.

### 3. **Optimize Your Strategy:**
   - Utilize the built-in optimization tools to fine-tune your strategy, improving key performance metrics.

### 4. **Simulate Real-Time Trading:**
   - Deploy your optimized strategy in a simulated live trading environment to test its robustness.

### 5. **Analyze Results:**
   - Review comprehensive reports, including profit/loss, trade logs, and performance charts.

## 🤝 Contributing

We welcome contributions to enhance the Flint & Steel Backtesting Platform. To contribute:
1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes and commit them (`git commit -am 'Add new feature'`).
4. Push the branch (`git push origin feature-branch`).
5. Open a pull request with a detailed description of your changes.

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.
