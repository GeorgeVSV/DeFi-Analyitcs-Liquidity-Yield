import os
import json
import logging
import requests
from typing import Any, List, Dict
import web3
from config import WEB3_INSTANCE, PROTOCOLS, ETHERSCAN_GET_ABI_ENDPOINT

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class DataFetcher:
    """
    A class to fetch raw on-chain data from DeFi protocols.

    Attributes:
        web3_instance (Web3): The Web3 instance connected to the Ethereum network.
    """

    def __init__(self) -> None:
        """
        Initializes the DataFetcher with a Web3 instance.
        """
        self.web3_instance = WEB3_INSTANCE

    def get_contract(self, protocol: str, network: str,
                    base_asset: str = None, contract_type: str = None,
                    market_type: str = None, abi_path: str = None, abi_contract_type: str = None) -> web3.eth.Contract:
        """
        Returns a contract instance for a given protocol contract.

        - If an ABI file path is provided, it must use that file (no fallback).
        - If no ABI path is provided, it must always fetch from Etherscan.
        - Special case for Compound: Uses proxy address for contract instance, but ABI from implementation contract.

        Args:
            protocol (str): The protocol name (e.g., 'aave', 'compound').
            network (str): The blockchain network (e.g., 'ethereum', 'polygon').
            base_asset (str, optional): Required for Compound (e.g., 'usdc', 'weth'). Not used for Aave.
            contract_type (str, optional): The specific contract type (e.g., 'proxy', 'implementation', or Aave contract types).
            market_type (str, optional): Required for Aave (e.g., 'core_market', 'prime_market'). Not used for Compound.
            abi_path (str, optional): Path to the JSON file containing the ABI. If None, it fetches from Etherscan.
            abi_contract_type (str, optional): **Used only for Compound** – Contract type name from `config.py` (e.g., `"implementation"`).

        Returns:
            Web3.eth.Contract: The Web3 contract instance.
        """
        config = PROTOCOLS.get(protocol)
        if not config:
            raise ValueError(f"Protocol '{protocol}' not found in config.")

        contract_address = None  # Default to None

        # Explicit validation and fetching logic for each protocol
        if protocol == "aave":
            if not market_type or not contract_type:
                raise ValueError("Aave requires both 'market_type' and 'contract_type'.")
            contract_address = config[network][market_type].get(contract_type)
            abi_fetch_address = contract_address

        elif protocol == "compound":
            if not base_asset or not contract_type:
                raise ValueError("Compound requires both 'base_asset' and 'contract_type'.")
            contract_address = config[network][base_asset].get(contract_type)

            # Compound special case: If `abi_contract_type` is provided, fetch ABI from that contract type
            if abi_contract_type:
                abi_fetch_address = config[network][base_asset].get(abi_contract_type)
                if not abi_fetch_address:
                    raise ValueError(f"ABI contract type '{abi_contract_type}' not found for Compound {base_asset} on {network}.")
                logger.info(f"Fetching ABI from '{abi_contract_type}' contract: {abi_fetch_address} for proxy: {contract_address}")
            else:
                abi_fetch_address = contract_address  # Default ABI source

        else:
            raise ValueError(f"Unsupported protocol '{protocol}'.")

        if not contract_address:
            raise ValueError(f"Contract '{contract_type}' not found for '{protocol}' on {network}.")

        # Strict decision: Either load from file OR fetch from Etherscan
        if abi_path:
            contract_abi = self.load_abi_from_file(abi_path)
            logger.info(f"Loaded ABI from file for {protocol} ({contract_type}) at {abi_path}")
        else:
            contract_abi = self.fetch_abi_from_etherscan(abi_fetch_address)
            logger.info(f"Fetched ABI from Etherscan for {protocol} ({contract_type}) at {abi_fetch_address}")

        return self.web3_instance.eth.contract(address=contract_address, abi=contract_abi)

    def get_abi(self, contract_address: str, abi_path: str) -> Any:
        """
        Attempts to fetch ABI from Etherscan first, then falls back to loading from a local file.

        Args:
            contract_address (str): The contract address to fetch ABI for.
            abi_path (str): Path to the local ABI file for fallback.

        Returns:
            Any: The ABI for the contract.
        """
        abi = self.fetch_abi_from_etherscan(contract_address)
        if abi:
            return abi  # Successfully fetched from Etherscan
        return self.load_abi_from_file(abi_path)  # Fall back to local file

    def fetch_abi_from_etherscan(self, contract_address: str) -> Any:
        """
        Attempts to fetch the ABI of a verified smart contract from Etherscan.

        Args:
            contract_address (str): The address of the smart contract.

        Returns:
            Any: The ABI if successfully fetched, else None.
        """
        url = ETHERSCAN_GET_ABI_ENDPOINT.format(address=contract_address)
        response = requests.get(url)
        data = response.json()

        if data["status"] == "1":  # Status 1 means success
            return json.loads(data["result"])
        return None  # Contract is likely not verified

    def load_abi_from_file(self, abi_path: str) -> Any:
        """
        Loads a smart contract ABI from a JSON file.

        Args:
            abi_path (str): The file path to the ABI JSON.

        Returns:
            Any: The loaded ABI.
        """
        if not os.path.exists(abi_path):
            raise FileNotFoundError(f"ABI file not found: {abi_path}")
        with open(abi_path, "r") as file:
            return json.load(file)

    def save_abi_to_json(self, contract_address: str, file_name: str, save_path: str):
        """
        Fetches the ABI of a given contract from Etherscan and saves it as a JSON file.

        Args:
            contract_address (str): Address of the contract.
            file_name (str): Name of the JSON file to save (without .json extension).
            save_path (str): Directory where the file should be saved.

        Returns:
            str: Full path of the saved ABI file, or None if failed.
        """
        try:
            # Fetch ABI using the existing method
            abi = self.fetch_abi_from_etherscan(contract_address)

            if not abi:
                logger.error(f"Failed to fetch ABI for {contract_address} from Etherscan.")
                return None

            # Ensure the save directory exists
            os.makedirs(save_path, exist_ok=True)

            # Define full file path
            full_file_path = os.path.join(save_path, f"{file_name}.json")

            # Check if the file already exists
            if os.path.exists(full_file_path):
                logger.info(f"Overwriting existing ABI file: {full_file_path}")

            # Save ABI to JSON file
            with open(full_file_path, "w") as json_file:
                json.dump(abi, json_file, indent=4)

            logger.info(f"ABI for contract {contract_address} saved to {full_file_path}")
            return full_file_path

        except Exception as e:
            logger.exception(f"Error saving ABI for contract {contract_address}: {e}")
            return None

    # === Protocol-Specific Methods ===

    def aave_fetch_reserve_data(self, network: str, market_type: str, contract_type: str = 'ui_pool_data_provider') -> List[Any]:
        """
        Fetches all raw reserve data for Aave V3 using UiPoolDataProvider.

        Args:
            network (str): Name of the Aave V3 network (e.g. ethereum, polygon, base, etc.).
            market_type (str): Name of the Aave V3 market (e.g. for Ethereum network there are core_market, prime_market, etherfi_market).
            contract_type (str): Name of the Aave V3 smart contract (e.g. pool_addresses_provider, ui_pool_data_provider)

        Returns:
            List[Any]: The raw response from the Aave contract & network name.
        """

        ui_provider_contract = self.get_contract("aave", network=network, market_type=market_type, contract_type=contract_type)
        provider_address = PROTOCOLS["aave"][network][market_type]["pool_addresses_provider"]
        return [ui_provider_contract.functions.getReservesData(provider_address).call(), network]

    def compound_fetch_market_data(self, network: str) -> Dict[str, Any]:
        """
        Fetches key Compound v3 metrics for a given network for all avaible base assets.

        Args:
            network (str): Blockchain network (e.g., 'ethereum').

        Returns:
            List[Any]:  The raw response from the Compound including market metrics: supply, borrow, and utilization.
        """

        base_assets = PROTOCOLS['compound'][network]
        raw_data = []

        for base_asset in base_assets:
            contract = self.get_contract("compound", network=network, base_asset=base_asset, contract_type="proxy", abi_contract_type='implementation')

            # Fetch key metrics
            total_supply = contract.functions.totalSupply().call()
            total_borrow = contract.functions.totalBorrow().call()
            utilization = contract.functions.getUtilization().call()
            reserves = contract.functions.getReserves().call()

            # Base asset & pricing
            base_token = contract.functions.baseToken().call()
            base_price_feed = contract.functions.baseTokenPriceFeed().call()
            decimals = contract.functions.decimals().call()
        
            base_raw_data = {
                "network": network,
                "base_asset": base_asset,
                "decimals": decimals,
                "total_supply": total_supply,
                "total_borrow": total_borrow,
                "utilization_rate": utilization,
                "reserves": reserves,
                "base_token": base_token,
                "base_price_feed": base_price_feed,
            }
            raw_data.append(base_raw_data)
        return raw_data
