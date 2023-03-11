let connected = false;

window.ethereum
.request({ method: "eth_requestAccounts" })
.then((accounts) => {
  const selectedAccount = accounts[0];
  console.log(selectedAccount);
  connected = true;
  walletAddress.textContent = "Connected to: " + selectedAccount;
})

if(!connected) {
    walletAddress.textContent = "Please return to Home page and connect to Metamask";
} else {
    // SHOW NFT GALLERY
}

function redirectToHome() {
    window.location.href = "/";
  }