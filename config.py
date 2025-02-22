import os
import logging
from dotenv import load_dotenv
from web3 import Web3

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

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

# --- Hardcoded Addresses for Aave ---
"""
For Aave fetching required 2 smart contract addressees:
- POOL_ADDRESSES_PROVIDER: The registry contract for Aave V3.
- UI_POOL_DATA_PROVIDER: The contract for fetching all reserve data in one call.
"""

# --- Protocols Configuration ---
PROTOCOLS = {
    "Aave": {
        "pool_addresses_provider": "0x2f39d218133AFaB8F2B819B1066c7E434Ad94E9e",
        "ui_pool_data_provider": "0x3F78BBD206e4D3c504Eb854232EdA7e47E9Fd8FC",
    },
    "Compound": {
        # Naming convention for Compound V3: "<network>_<base_asset>_<contract_type>"
        # Ensures clarity for multi-chain support and contract distinctions
        "ethereum_usdc_proxy": "0xc3d688B66703497DAA19211EEdff47f25384cdc3",
        "ethereum_usdc_implementation": "0xaeC1954467B6d823A9042E9e9D6E4F40111069a9",
        "ethereum_weth_proxy": "0xA17581A9E3356d9A858b789D68B4d866e593aE94",
    }
}
