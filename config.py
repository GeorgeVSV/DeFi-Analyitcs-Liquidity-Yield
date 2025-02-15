import os
from dotenv import load_dotenv
from web3 import Web3

# Load environment variables from .env
load_dotenv()

# List of required environment variables
REQUIRED_ENV_VARS = [
    "ETH_INFURA_RPC_URL",
    "ETHERSCAN_API_KEY",
    "AAVE_DATA_PROVIDER_ADDRESS"
]

# Check for missing required environment variables
missing_vars = [var for var in REQUIRED_ENV_VARS if not os.getenv(var)]
if missing_vars:
    raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

# Assign environment variables with documentation
ETHERSCAN_API_KEY: str = os.getenv("ETHERSCAN_API_KEY", "")
"""
ETHERSCAN_API_KEY:
    Etherscan API key, used for fetching verified ABIs from the Etherscan API.
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

# Initialize Web3 only once
WEB3 = Web3(Web3.HTTPProvider(ETH_INFURA_RPC_URL))
"""
WEB3:
    A globally initialized Web3 instance using the configured Ethereum RPC.
"""

# Protocol Configuration
PROTOCOLS = {
    "Aave": {
        "data_provider": AAVE_DATA_PROVIDER_ADDRESS,
        "abi_path": "abis/aave.json",
    },
    "Compound": {
        "data_provider": "0xc3d688B66703497DAA19211EEdff47f25384cdc3",
        "abi_path": "abis/compound.json",
    }
}
"""
PROTOCOLS:
    Dictionary mapping protocol names to their contract addresses and ABI paths.
    This allows the DeFi fetcher to dynamically load protocol data.
"""
