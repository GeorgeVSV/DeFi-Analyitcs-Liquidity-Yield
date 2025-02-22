import os
import json
import logging
import requests
from typing import Any, List
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

    def get_contract(self, protocol: str, contract_name: str, abi_path: str = None) -> web3.eth.Contract:
        """
        Returns a contract instance for a given protocol contract.

        - If an ABI file path is provided, it must use that file (no fallback).
        - If no ABI path is provided, it must always fetch from Etherscan.

        Args:
            protocol (str): The protocol name.
            contract_name (str): The name of the contract to fetch (must match keys in PROTOCOLS[protocol]).
            abi_path (str, optional): Path to the JSON file containing the ABI. If None, it fetches from Etherscan.

        Returns:
            Web3.eth.Contract: The Web3 contract instance.
        """
        config = PROTOCOLS.get(protocol)
        if not config:
            raise ValueError(f"Protocol '{protocol}' not found in config.")

        contract_address = config.get(contract_name)
        if not contract_address:
            raise ValueError(f"Contract '{contract_name}' not found in protocol '{protocol}'.")

        # Strict decision: Either load from file OR fetch from Etherscan
        if abi_path:
            contract_abi = self.load_abi_from_file(abi_path)
            logger.info(f"Loaded ABI from file for {protocol} ({contract_name}) at {abi_path}")
        else:
            contract_abi = self.fetch_abi_from_etherscan(contract_address)
            logger.info(f"Fetched ABI from Etherscan for {protocol} ({contract_name}) at {contract_address}")

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

    def aave_fetch_reserve_data(self) -> List[Any]:
        """
        Fetches all raw reserve data for Aave using UiPoolDataProvider.

        Returns:
            List[Any]: The raw response from the Aave contract.
        """
        ui_provider_contract = self.get_contract("Aave", "ui_pool_data_provider")
        provider_address = PROTOCOLS["Aave"]["pool_addresses_provider"]
        return ui_provider_contract.functions.getReservesData(provider_address).call()
