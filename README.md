# DeFi-Analytics-Liquidity-Yield
DeFi Analytics tool for Liquidity & Yield

### Overview
This repository provides an analytics solution for fetching real-time lending, borrowing, and liquidity data from DeFi protocols. Aave, Compound V3, and Uniswap are currently supported, and the modular architecture allows for straightforward integration of additional protocols. Data retrieval is managed through Web3.py, with contract ABIs fetched on-demand from Etherscan. The tool calculates key metrics such as interest rates, collateral factors, and total liquidity, then organizes the results in Pandas DataFrames for convenient analysis.

### API creds reminder
Make sure to set your Etherscan API key before running any modules:
ETHERSCAN_API_KEY=your_api_key

### General Structure
Each protocol has its own module within the analytics directory, and they all share a similar structure via a base module. Utilities, such as abi_fetcher.py for Etherscan ABI calls, reside in the utils directory. 


### Contributing
Contributions are welcome: fork this repository, create a branch, commit and push your changes, and open a pull request. This project is made available under the MIT License.

