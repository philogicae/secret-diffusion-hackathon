import os
from requests import packages, post
from rich import print
from io import BytesIO
from base64 import b64decode
from PIL import Image
from urllib3.exceptions import InsecureRequestWarning
packages.urllib3.disable_warnings(category=InsecureRequestWarning)


class SD_API:
    OUTPUT_DIR = "src/output"
    DEFAULT_PROMPT = prompt = dict(
        prompt="(logo of bitcoin:1.2), pixel art, design, 8k, hdr",
        negative_prompt="out of frame, blurry, low res",
        width=256,
        height=256,
        sampler_name="Euler",
        steps=30,
        cfg_scale=5,
        seed=0,
        n_iter=1
    )

    def __init__(self, ip):
        self.ip = ip
        self.txt2img = f"{self.ip}/sdapi/v1/txt2img"
        self.png_info = f"{self.ip}/sdapi/v1/png-info"
        os.makedirs(self.OUTPUT_DIR, exist_ok=True)

    def _call(self, url, payload):
        r = post(url, json=payload, verify=False)
        if r.status_code == 200:
            print(f"POST request successful: {url}")
            return r.json()
        else:
            raise Exception("Error: {}".format(r.status_code))

    def generate(self, prompt_data={}, n=1):
        prompt = self.DEFAULT_PROMPT | prompt_data | dict(n_iter=n)
        resp = self._call(self.txt2img, prompt)
        for i, data in enumerate(resp['images']):
            img = Image.open(BytesIO(b64decode(data.split(",", 1)[0])))
            img.save(f'{self.OUTPUT_DIR}/img-{i+1}.png')
            self.metadata(data, header=f"{i+1}/{len(resp['images'])}:")

    def metadata(self, data, header=''):
        png_payload = dict(image="data:image/png;base64," + data)
        resp = self._call(self.png_info, png_payload)
        metadata = resp.get("info")
        print(header, metadata)
