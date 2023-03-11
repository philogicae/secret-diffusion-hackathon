let connected = false;

if (typeof window.ethereum !== "undefined") {
  const connectButton = document.getElementById("connect-button");

  const connect = () => {
    window.ethereum
      .request({ method: "eth_requestAccounts" })
      .then((accounts) => {
        const selectedAccount = accounts[0];
        console.log(selectedAccount);
        connectButton.textContent = "Connected";
        connected = true;
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
        connected = false;
      })
      .catch((error) => {
        console.log("Error disconnecting wallet:", error);
      });
  };

  connectButton.addEventListener("click", () => {
    if (connected) {
      disconnect();
    } else {
      connect();
    }
  });
} else {
  console.log("Wallet extension not installed.");
}
