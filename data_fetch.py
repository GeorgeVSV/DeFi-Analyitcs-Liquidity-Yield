import os
import json
import requests
from typing import Any, List
import web3
from config import WEB3_INSTANCE, PROTOCOLS, ETHERSCAN_GET_ABI_ENDPOINT

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

    def get_contract(self, protocol: str, contract_name: str) -> web3.contract.Contract:
        """
        Returns a contract instance for a given protocol contract.

        Args:
            protocol (str): The protocol name.
            contract_name (str): The name of the contract to fetch (must match keys in PROTOCOLS[protocol]).

        Returns:
            web3.contract.Contract: The Web3 contract instance.
        """
        config = PROTOCOLS.get(protocol)
        if not config:
            raise ValueError(f"Protocol '{protocol}' not found in config.")

        contract_address = config.get(contract_name)
        if not contract_address:
            raise ValueError(f"Contract '{contract_name}' not found in protocol '{protocol}'.")

        contract_abi = self.get_abi(contract_address, config["abi_paths"].get(contract_name, ""))
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
