from flask import Flask, render_template, request
from sd_api import SD_API
from cryptor import Cryptor
from ipfs_api import IFPS_api
from web3_utils import web3_utils
import json

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/view-collection')
def view_collection():
    return render_template('view-collection.html')


@app.route('/create-secret')
def create_secret():
    return render_template('create-secret.html')


@app.route('/generate-image')
def generate_image():
    # Retrieve data
    stable_diffusion_link = request.args.get('stableDiffusionLink')
    secret = request.args.get('secret')
    prompt = request.args.get('prompt')
    amount = request.args.get('amount')

    # Prepare prompt
    sd_api = SD_API(stable_diffusion_link)
    print('Formatting prompt...')
    formatted_prompt = sd_api.parse_prompt(prompt)

    # Prepare image
    print('Generating image...')
    img_path, metadata = sd_api.generate(formatted_prompt)

    # Encryption
    print('Encrypting secret...')
    pk = Cryptor.generate_pk()
    to_encrypt = json.dumps(dict(secret=secret, metadata=metadata))
    encrypted_secret = Cryptor.encrypt(pk, to_encrypt)

    # Post on IPFS
    print('Posting on IPFS...')
    ifps = IFPS_api()
    result = ifps.post('Secret', encrypted_secret, img_path)
    url = result['metadata']['url']
    print(url)

    # Mint
    print('Prepare minting...')
    tx = web3_utils.generate_mint_tx(amount, url)
    print(tx)

    # Prepare response
    Cryptor.save_pk('pk', pk)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
