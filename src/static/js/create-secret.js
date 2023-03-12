let connected = false;
let stableDiffusionLink = "";
let secret = "";
let inputPrompt = "";
let amount = 1;

let hasStableDiffusionLink = false;
let hasSecret = false;
let hasPrompt = false;
let hasAmount = false;

const walletAddress = document.getElementById("walletAddress");
let sdUrlInput = document.getElementById("sd-url-input");
let secretInput = document.getElementById("secret-input");
let promptInput = document.getElementById("prompt-input");
let amountInput = document.getElementById("amount-input");
let sdBtn = document.getElementById("sd-btn");
let secretBtn = document.getElementById("secret-btn");
let promptBtn = document.getElementById("prompt-btn");
let amountBtn = document.getElementById("amount-btn");
let numberNftBtn = document.getElementById("number-nft-btn");

let generateImageBtn = document.getElementById("generate-image-btn");
generateImageBtn.disabled = true; // disable the button initially

window.ethereum.request({ method: "eth_requestAccounts" }).then((accounts) => {
  const selectedAccount = accounts[0];
  console.log(selectedAccount);
  connected = true;
  walletAddress.textContent = "Connected to: " + selectedAccount;
});

function handleSDUrl() {
  stableDiffusionLink = sdUrlInput.value;
  if (stableDiffusionLink.length > 0) {
    hasStableDiffusionLink = true;
  }

  if (hasStableDiffusionLink) {
    console.log(`StableDiffusion instance URL is: ${stableDiffusionLink}`);
    sdUrlInput.disabled = true;
    sdBtn.innerHTML = '<i class="fas fa-check"></i> URL saved';
    sdBtn.classList.add("success");
    enableGenerateImageBtn();
  } else {
    console.log("Please enter a valid StableDiffusion instance URL.");
  }
}

function handleSecret() {
  secret = secretInput.value;
  if (secret.length > 0) {
    hasSecret = true;
  }

  if (hasSecret) {
    console.log(`Secret is: ${secret}`);
    secretInput.disabled = true;
    secretBtn.innerHTML = '<i class="fas fa-check"></i> Secret saved';
    secretBtn.classList.add("success");
    enableGenerateImageBtn();
  } else {
    console.log("Please enter a valid secret.");
  }
}

function handlePrompt() {
  inputPrompt = promptInput.value;
  hasPrompt = true;
  console.log(`Prompt is: ${inputPrompt}`);
  promptInput.disabled = true;
  promptBtn.innerHTML = '<i class="fas fa-check"></i> Prompt saved';
  promptBtn.classList.add("success");
  enableGenerateImageBtn();
}

function handleAmount() {
  let strAmount = amountInput.value;
  if (strAmount == NaN || strAmount == "") {
    strAmount = 0;
  }
  let intAmount = parseInt(strAmount);
  amount = intAmount + 1;
  hasAmount = true;
  console.log(`Amount is: ${amount}`);
  amountInput.disabled = true;
  amountBtn.innerHTML = '<i class="fas fa-check"></i> Amount saved';
  amountBtn.classList.add("success");
  enableGenerateImageBtn();
}

function handleGenerateImage() {
  let spinner = document.getElementById("spinner");
  spinner.style.display = "block";
  fetch(
    "/generate-image?stableDiffusionLink=" +
      stableDiffusionLink +
      "&secret=" +
      secret +
      "&prompt=" +
      inputPrompt +
      "&amount=" +
      amount
  )
    .then((response) => {
      if (response.ok) {
        console.log(response);
        return response;
      } else {
        throw new Error("Error generating image.");
      }
    })
    .then(() => {
      spinner.style.display = "none";
    });
}

function enableGenerateImageBtn() {
  if (hasStableDiffusionLink && hasSecret && hasPrompt && hasAmount) {
    generateImageBtn.disabled = false; // enable the button
    generateImageBtn.innerHTML = "Generate AI Image"; // Set the button text
  } else {
    generateImageBtn.disabled = true; // disable the button
    generateImageBtn.innerHTML = "Please fill in all inputs"; // Set the button text
  }
}

// Call the function initially to set the state of the button
enableGenerateImageBtn();

if (!connected) {
  walletAddress.textContent =
    "Please return to Home page and connect to Metamask";
}

function redirectToHome() {
  window.location.href = "/";
}
