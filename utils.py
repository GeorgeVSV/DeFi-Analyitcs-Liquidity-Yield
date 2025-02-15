import requests
import json
from web3 import Web3
from typing import List, Dict, Any
from config import ETH_RPC_URL

# Global Web3 instance (created once and reused)
w3 = Web3(Web3.HTTPProvider(ETH_RPC_URL))


def get_abi(address: str, etherscan_api_key: str) -> List[Dict[str, Any]]:
    """
    Fetch the ABI for a given smart contract address from Etherscan.

    Parameters:
        address (str): 
            The smart contract address (hex) whose ABI will be fetched.
        etherscan_api_key (str): 
            Your Etherscan API key for accessing the Etherscan API.

    Returns:
        List[Dict[str, Any]]:
            A list of dictionaries representing the contract's ABI if verified; 
            otherwise, raises an exception.

    Raises:
        ValueError:
            If the address is invalid, the API key is invalid, or Etherscan 
            returns an error (e.g., unverified contract).
    """
    # Convert address to checksum format (ensures correctness)
    checksum_address = w3.to_checksum_address(address)

    # Construct the Etherscan API request
    abi_url = (
        "https://api.etherscan.io/api"
        f"?module=contract&action=getabi&address={checksum_address}"
        f"&apikey={etherscan_api_key}"
    )

    # Fetch ABI from Etherscan
    response = requests.get(abi_url)
    data = response.json()

    # Check for errors in the response
    if data.get("status") != "1":
        raise ValueError(
            f"Error fetching ABI from Etherscan. status={data.get('status')}, "
            f"message={data.get('message')}, result={data.get('result')}"
        )

    # Parse JSON string into a Python list of dictionaries
    try:
        abi: List[Dict[str, Any]] = json.loads(data["result"])
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse ABI JSON. Original error: {e}")

    return abi
