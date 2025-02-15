import os
from dotenv import load_dotenv

load_dotenv()  # Loads the .env file

ETHERSCAN_API_KEY: str = os.getenv("ETHERSCAN_API_KEY", "")
"""
ETHERSCAN_API_KEY:
    Etherscan API key, used for fetching verified ABIs from the Etherscan API
"""

ETH_INFURA_RPC_URL: str = os.getenv("ETH_INFURA_RPC_URL", "")
"""
ETH_INFURA_RPC_URL:
    The RPC endpoint provided by Infura.
    Typically https://mainnet.infura.io/v3/<API_KEY>
"""

AAVE_DATA_PROVIDER_ADDRESS: str = os.getenv("AAVE_DATA_PROVIDER_ADDRESS", "")
"""
AAVE_DATA_PROVIDER_ADDRESS:
    The on-chain address for the Aave data provider contract. 
    Taken from official AAVE protocol docs: https://aave.com/docs/resources/addresses
"""
