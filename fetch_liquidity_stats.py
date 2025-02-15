"""Fetch DeFi liquidity, TVL, and APY data from Uniswap, Aave, and Curve."""

import requests
from typing import Dict, List
from config import UNISWAP_V3_API, AAVE_V3_API, CURVE_API
from utils import log_message, format_currency

def fetch_uniswap_tvl() -> List[Dict]:
    """Fetches TVL data from Uniswap V3 subgraph.

    Returns:
        List[Dict]: List of top liquidity pools with TVL.
    """
    query = """
    {
      pools(first: 5, orderBy: tvlUSD, orderDirection: desc) {
        id
        token0 { symbol }
        token1 { symbol }
        tvlUSD
        feeTier
      }
    }
    """
    try:
        response = requests.post(UNISWAP_V3_API, json={"query": query})
        data = response.json()
        pools = data["data"]["pools"]
        log_message("INFO", f"Fetched {len(pools)} Uniswap pools successfully.")
        return pools
    except Exception as e:
        log_message("ERROR", f"Error fetching Uniswap TVL: {str(e)}")
        return []

def fetch_aave_tvl() -> Dict:
    """Fetches total market size from Aave V3 subgraph.

    Returns:
        Dict: TVL data for Aave markets.
    """
    query = """
    {
      markets {
        name
        totalLiquidity
      }
    }
    """
    try:
        response = requests.post(AAVE_V3_API, json={"query": query})
        data = response.json()
        log_message("INFO", "Fetched Aave market liquidity successfully.")
        return data["data"]["markets"]
    except Exception as e:
        log_message("ERROR", f"Error fetching Aave TVL: {str(e)}")
        return {}

def fetch_curve_tvl() -> Dict:
    """Fetches TVL data from Curve API.

    Returns:
        Dict: Curve pools TVL data.
    """
    try:
        response = requests.get(CURVE_API)
        data = response.json()
        log_message("INFO", "Fetched Curve TVL successfully.")
        return data["data"]["poolData"]
    except Exception as e:
        log_message("ERROR", f"Error fetching Curve TVL: {str(e)}")
        return {}

