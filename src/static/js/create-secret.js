let connected = false;
let stableDiffusionLink = "";
const walletAddress = document.getElementById("walletAddress");
const sdUrlInput = document.getElementById("sd-url-input");
const submitBtn = document.getElementById("submit-btn");

window.ethereum
    .request({ method: "eth_requestAccounts" })
    .then((accounts) => {
        const selectedAccount = accounts[0];
        console.log(selectedAccount);
        connected = true;
        walletAddress.textContent = "Connected to: " + selectedAccount;
    })

function handleSDUrl() {
    stableDiffusionLink = sdUrlInput.value;
    if (stableDiffusionLink) {
        console.log(`StableDiffusion instance URL is: ${stableDiffusionLink}`);
        sdUrlInput.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-check"></i> URL saved';
        submitBtn.classList.add("success");
        // LOGIC TO CREATE NFT
    } else {
        console.log("Please enter a valid StableDiffusion instance URL.");
    }
}

if (!connected) {
    walletAddress.textContent = "Please return to Home page and connect to Metamask";
}

function redirectToHome() {
    window.location.href = "/";
}
