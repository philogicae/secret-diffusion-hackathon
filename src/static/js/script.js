let connected = false;
let defaultWalletAddress = "Please connect to Metamask";
walletAddress.textContent = defaultWalletAddress;

if (typeof window.ethereum !== "undefined") {
  const connectButton = document.getElementById("connect-button");
  const afterConnectButtons = document.getElementById("after-connect-buttons");
  afterConnectButtons.style.visibility = "hidden";

  const connect = async() => {
    window.ethereum
      .request({ method: "eth_requestAccounts" })
      .then((accounts) => {
        const selectedAccount = accounts[0];
        console.log(selectedAccount);
        connectButton.textContent = "Connected";
        connectButton.classList.add("connected");
        connected = true;
        walletAddress.textContent = "Connected to: " + selectedAccount;
        afterConnectButtons.style.visibility = "visible";
      })
      .catch((error) => {
        console.log("MetaMask wallet access denied:", error);
      });
  };

  const disconnect = async() => {
    window.ethereum
      .send("eth_chainId", [])
      .then(() => {
        connectButton.textContent = "Connect Wallet";
        connectButton.classList.remove("connected");
        connected = false;
        walletAddress.textContent = defaultWalletAddress
        afterConnectButtons.style.visibility = "hidden";
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

function redirectToCollection() {
  window.location.href = "/view-collection";
}
