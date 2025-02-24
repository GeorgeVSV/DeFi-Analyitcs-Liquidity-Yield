import pandas as pd
from typing import List, Dict, Any
from datetime import datetime, timezone

class DataProcessor:
    """
    A class to process raw on-chain data into structured, human-readable formats.

    This includes reserve data, borrowing/lending metrics, utilization rates, and
    APY calculations for DeFi protocols.

    Attributes:
        RAY (int): Scaling factor for ray-based calculations (1e27).
        SECONDS_PER_YEAR (int): Total seconds in a year (for interest calculations).
    """

    RAY = 10**27  # Scaling factor for Ray format
    SECONDS_PER_YEAR = 31_536_000  # 365 days

    def __init__(self):
        """Initializes the DataProcessor."""
        pass

    def aave_process_reserve_data(self, raw_data: List) -> pd.DataFrame:
        """
        Processes Aave V3 reserve data into a structured Pandas DataFrame.

        Args:
            raw_data (List): The raw response from `DataFetcher.aave_fetch_reserve_data()`.

        Returns:
            pd.DataFrame: A structured DataFrame containing processed metrics.
        """
        processed_data = []

        reserves = raw_data[0][0]
        network = raw_data[1]

        for asset in reserves:
            # Extract essential data
            asset_address = asset[0]
            asset_name = asset[1]
            symbol = asset[2]
            decimals = asset[3]
            ltv = asset[4] / 100  # Convert to %
            liquidation_threshold = asset[5] / 100  # Convert to %
            liquidation_bonus = asset[6]
            variable_borrow_index = asset[13]
            total_scaled_variable_debt = asset[21]
            available_liquidity = asset[20]

            # Calculate Total Variable Debt
            total_variable_debt = (total_scaled_variable_debt * variable_borrow_index) / self.RAY

            # Calculate TVL (Total Value Locked)
            tvl = total_variable_debt + available_liquidity

            # Calculate Utilization Rate
            utilization_rate = (total_variable_debt / tvl) if tvl > 0 else 0

            # Lending APY Calculation
            liquidity_rate = asset[14]
            lending_apr = liquidity_rate / self.RAY
            lending_apy = ((1 + (lending_apr / self.SECONDS_PER_YEAR)) ** self.SECONDS_PER_YEAR) - 1
            lending_apy *= 100

            # Variable Borrow APY Calculation
            variable_borrow_rate = asset[15]
            variable_borrow_apr = variable_borrow_rate / self.RAY
            variable_borrow_apy = ((1 + (variable_borrow_apr / self.SECONDS_PER_YEAR)) ** self.SECONDS_PER_YEAR) - 1
            variable_borrow_apy *= 100

            # Additional Metrics
            spread = variable_borrow_apy - lending_apy
            borrow_cap = asset[36]
            supply_cap = asset[37]

            # Store processed asset data
            asset_data = {
                "protocol": "Aave V3",
                "network": network,
                "asset_address": asset_address,
                "asset_name": asset_name,
                "symbol": symbol,
                "decimals": decimals,
                "ltv_percent": round(ltv, 2),
                "liquidation_threshold_percent": round(liquidation_threshold, 2),
                "liquidation_bonus": liquidation_bonus,
                "tvl": round(tvl, 2),
                "total_variable_debt": round(total_variable_debt, 2),
                "utilization_rate_percent": round(utilization_rate * 100, 2),
                "lending_apy_percent": round(lending_apy, 2),
                "variable_borrow_apy_percent": round(variable_borrow_apy, 2),
                "spread_percent": round(spread, 2),
                "borrow_cap": borrow_cap,
                "supply_cap": supply_cap,
                "load_datetime": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
            }
            processed_data.append(asset_data)

        return pd.DataFrame(processed_data)
    
    def process_compound_market_data(self, raw_data:List) -> pd.DataFrame:
        """
        Processes raw Compound v3 market data into a structured DataFrame.

        Args:
            raw_data (List[Any]): Raw fetched data.

        Returns:
            pd.DataFrame: Structured market metrics.
        """
        processed_data = []
        base_assets = raw_data
        print(base_assets)

        for base_asset in base_assets:
            decimals = 10 ** base_asset["decimals"]
            base_asset_data = {
                "protocol": "Compound V3",
                "network": base_asset["network"],
                "base_asset": base_asset["base_asset"],
                "base_token": base_asset["base_token"],
                "reserves": base_asset["reserves"] / decimals,
                "total_supply": base_asset["total_supply"] / decimals,
                "total_borrow": base_asset["total_borrow"] / decimals,
                "utilization_rate_percent": base_asset["utilization_rate"] / 1e18 * 100,
            }
            processed_data.append(base_asset_data)
        return pd.DataFrame(processed_data)
