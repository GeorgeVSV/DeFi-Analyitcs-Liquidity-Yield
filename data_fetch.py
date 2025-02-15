import os
import json
import requests
from typing import Any, Callable
import web3
from config import WEB3_INSTANCE, PROTOCOLS, ETHERSCAN_GET_ABI_ENDPOINT

class DataFetcher:
    """
    A class to fetch on-chain data from DeFi protocols dynamically.

    Attributes:
        web3 (Web3): The Web3 instance connected to the Ethereum network.
    """

    def __init__(self) -> None:
        """
        Initializes the DataFetcher with a Web3 instance.
        """
        self.web3_instance = WEB3_INSTANCE

        # Dynamic method dispatcher for TVL fetching (only Aave for now)
        self.tvl_methods = {
            "Aave": self.fetch_tvl_aave
        }

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

    def get_abi(self, contract_address: str, abi_path: str) -> Any:
        """
        Attempts to fetch ABI from Etherscan first, then falls back to loading from a file.

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

    def get_contract(self, protocol: str) -> web3.contract.Contract:
        """
        Returns a contract instance for a given DeFi protocol.

        Args:
            protocol (str): The protocol name (only "Aave" for now).

        Returns:
            web3.contract.Contract: The Web3 contract instance.
        """
        config = PROTOCOLS.get(protocol)
        if not config:
            raise ValueError(f"Protocol '{protocol}' not found in config.")

        contract_address = self.web3_instance.to_checksum_address(config["data_provider"])
        abi = self.get_abi(contract_address, config["abi_path"])
        return self.web3_instance.eth.contract(address=contract_address, abi=abi)

    def fetch_tvl_aave(self, contract: web3.contract.Contract, asset_address: str) -> int:
        """
        Fetches TVL for Aave using getReserveData().

        Args:
            contract (web3.contract.Contract): The Aave contract instance.
            asset_address (str): The asset's smart contract address.

        Returns:
            int: The TVL in raw blockchain units.
        """
        return contract.functions.getReserveData(asset_address).call()[2]

    def fetch_tvl(self, protocol: str, asset_address: str) -> int:
        """
        Fetches the TVL for Aave (other protocols can be added later).

        Args:
            protocol (str): The protocol name.
            asset_address (str): The asset's smart contract address.

        Returns:
            int: The TVL in raw blockchain units.
        """
        if protocol not in self.tvl_methods:
            raise ValueError(f"TVL fetching not implemented for protocol '{protocol}'")

        # Retrieve the correct method dynamically from the dispatcher
        fetch_tvl_method: Callable = self.tvl_methods[protocol]

        contract = self.get_contract(protocol)
        return fetch_tvl_method(contract, asset_address)
