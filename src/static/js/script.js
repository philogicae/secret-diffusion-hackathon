let connected = false;
let defaultWalletAddress = "Please connect to Metamask"
walletAddress.textContent = defaultWalletAddress;

if (typeof window.ethereum !== "undefined") {
  const connectButton = document.getElementById("connect-button");

  const connect = () => {
    window.ethereum
      .request({ method: "eth_requestAccounts" })
      .then((accounts) => {
        const selectedAccount = accounts[0];
        console.log(selectedAccount);
        connectButton.textContent = "Connected";
        connectButton.classList.add("connected");
        connected = true;
        walletAddress.textContent = "Connected to: " + selectedAccount;
      })
      .catch((error) => {
        console.log("MetaMask wallet access denied:", error);
      });
  };

  const disconnect = () => {
    window.ethereum
      .send("eth_chainId", [])
      .then(() => {
        connectButton.textContent = "Connect Wallet";
        connectButton.classList.remove("connected");
        connected = false;
        walletAddress.textContent = defaultWalletAddress
      })
      .catch((error) => {
        console.log("Error disconnecting wallet:", error);
      });
  };

  connectButton.addEventListener("click", async () => {
    if (connected) {
      disconnect();
    } else {
      connect();      
    }
  });
} else {
  console.log("Wallet extension not installed.");
}
