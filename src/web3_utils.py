from web3 import Web3
from os import getenv
from dotenv import load_dotenv
load_dotenv()
RPC = "https://polygon-testnet.public.blastapi.io"
contract_address = getenv("CONTRACT")
contract_abi = "src/contracts/abi/SFT.abi"


class web3_utils:
    def generate_mint_tx(amount, uri):
        # Connect to RPC
        w3 = Web3(Web3.HTTPProvider(RPC))
        with open(contract_abi, "r") as f:
            abi = f.read()

        # Load contract
        contract = w3.eth.contract(address=contract_address, abi=abi)

        # Generate mint tx
        return contract.functions.mint(int(amount), uri).buildTransaction({
            "from": "0x0000000000000000000000000000000000000001",
            "nonce": w3.eth.getTransactionCount("0x0000000000000000000000000000000000000001"),
            "gas": 1000000,
            "gasPrice": w3.toWei("50", "gwei")  # Metamask
        })
