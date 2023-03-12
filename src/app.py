from flask import Flask, render_template, request

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
    formatted_prompt = api.parse_prompt(prompt);
    print('Generating image...')
    api.generate(formatted_prompt)
    return "Image generated successfully."


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
