import io
from PIL import Image
from flask import Flask, make_response, render_template, request

from sd_api import SD_API

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
    stable_diffusion_link = request.args.get('stableDiffusionLink')
    prompt = request.args.get('prompt')
    api = SD_API(stable_diffusion_link)
    print('Formatting prompt...')
    formatted_prompt = api.parse_prompt(prompt)
    print('Generating image...')
    print(formatted_prompt)

    genImage_data = api.generate(formatted_prompt)[0]
    img = genImage_data['img']  # Extract the Image object from the dictionary
    img_data = io.BytesIO()
    img.save(img_data, format='JPEG')
    response = make_response(img_data.getvalue())
    response.headers['Content-Type'] = 'image/jpeg'
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
