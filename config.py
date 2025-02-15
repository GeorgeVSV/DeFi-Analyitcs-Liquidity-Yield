import os
from dotenv import load_dotenv
from web3 import Web3

# Load environment variables from .env
load_dotenv()

# --- Required Environment Variables ---
"""
This section loads required API keys and RPC URLs from the .env file.
Each key is documented to clarify its purpose.

ENVIRONMENT VARIABLES:
- ETH_INFURA_RPC_URL: The Infura RPC URL for connecting to Ethereum.
- ETHERSCAN_API_KEY: API key for interacting with Etherscan's API.
"""

ETH_INFURA_RPC_URL = os.getenv("ETH_INFURA_RPC_URL")
ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY")

# Ensure all required secrets are loaded
REQUIRED_ENV_VARS = [
    "ETH_INFURA_RPC_URL",
    "ETHERSCAN_API_KEY"
]
missing_vars = [var for var in REQUIRED_ENV_VARS if not os.getenv(var)]
if missing_vars:
    raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

# --- Web3 Initialization ---
"""
A single Web3 instance is initialized globally to prevent multiple redundant connections.
This should be imported and used across all modules that require Web3 interaction.
"""
WEB3_INSTANCE = Web3(Web3.HTTPProvider(ETH_INFURA_RPC_URL))

# --- Etherscan API Configuration ---
"""
Etherscan API Endpoints:
- ETHERSCAN_API_URL: The base URL for Etherscan API requests.
- ETHERSCAN_GET_ABI_ENDPOINT: Fetches contract ABI from Etherscan for verified contracts.
"""

ETHERSCAN_API_URL = "https://api.etherscan.io/api"
ETHERSCAN_GET_ABI_ENDPOINT = (
    f"{ETHERSCAN_API_URL}?module=contract&action=getabi&address={{address}}&apikey={ETHERSCAN_API_KEY}"
)

# --- Protocol Configuration ---
"""
Each DeFi protocol has:
- data_provider: Smart contract address for fetching protocol data.
- abi_path: The local path to the ABI file (used as a fallback if fetching ABI fails).
"""

PROTOCOLS = {
    "Aave": {
        "data_provider": "0x41393e5e337606dc3821075Af65AeE84D7688CBD",
        "abi_path": "abis/aave.json",
    },
}
