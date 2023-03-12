from web3 import auto


class web3_utils:
    def __init__(self):
        self.w3 = auto.w3
        self.w3.eth.enable_unaudited_features()
