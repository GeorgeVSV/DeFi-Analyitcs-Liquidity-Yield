# DeFi-Analytics-Liquidity-Yield (DALY)
**DeFi analytics tool for real-time liquidity & yield tracking.**

## **Overview**
**DALY** provides a structured analytics solution for fetching and analyzing **lending, borrowing, and liquidity data** from DeFi protocols. The tool currently supports **Aave V3**, with planned expansion to **Compound V3** and **Uniswap**. 

**Key Features:**
- **Modular & Protocol-Agnostic Architecture:** Each protocol has its own dedicated fetching and processing module, ensuring scalability and maintainability.
- **Real-Time On-Chain Data Retrieval:** Uses `Web3.py` to fetch raw data directly from smart contracts.
- **Automatic ABI Fetching:** Retrieves ABIs dynamically from Etherscan for up-to-date contract interactions.
- **Financial Metric Computation:** Computes **TVL (Total Value Locked), Utilization Rate, Lending APY, Borrowing APY, and Collateral Metrics**.
- **Optimized Data Handling:** Outputs structured **Pandas DataFrames** for further analysis and visualization.

## **API Credentials Reminder**  
Before running the tool, set your **Etherscan API key**:
ETHERSCAN_API_KEY=your_api_key

## **Project Architecture**
DALY follows a **modular OOP structure** with a clear separation of concerns:

### **1. Fetching Layer – `DataFetcher`** 
Handles **on-chain data retrieval** for each protocol:
- Uses `Web3.py` to call smart contract functions.
- Fetches ABIs dynamically from **Etherscan**.
- Each protocol has its own fetching method (e.g., `aave_fetch_reserve_data()`).

### **2. Processing Layer – `DataProcessor`**
Converts **raw blockchain data** into structured, human-readable financial metrics:
- Processes **lending, borrowing, and liquidity data**.
- Implements **per-second compounding** for accurate **APY calculations**.
- Uses **protocol-specific methods** (e.g., `aave_process_reserve_data()`).

### **3. Configuration Layer – `config.py`**
- Stores **protocol contract addresses** and **ABI paths**.
- Defines **environment variables** (e.g., RPC URLs, API keys).

### **4. Main Execution – `main.py` (Planned)**
- **Centralized script** to call **DataFetcher** & **DataProcessor** for **full data extraction**.
- Outputs structured **Pandas DataFrames** for further analysis.

### **5. Future Modules (Planned)**
- **`DataExporter`** → Export structured data to **CSV/JSON**.
- **`StrategyAnalyzer`** → Detect **profitable lending & borrowing opportunities**.
- **`Dashboard`** → Visualization layer for **real-time analytics**.
