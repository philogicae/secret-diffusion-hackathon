import os
import random
from requests import packages, post
from rich import print
from io import BytesIO
from base64 import b64decode
from PIL import Image
from urllib3.exceptions import InsecureRequestWarning
packages.urllib3.disable_warnings(category=InsecureRequestWarning)


class SD_API:
    OUTPUT_DIR = "src/output"
    RANDOM_WORD_LIST = ["Paris", "Cat", "Ballerina",
                        "Hackathon Winner", "Dog", "Trophy", "Bucharest"]
    DEFAULT_PROMPT = dict(
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

    def autoprompt(self):
        new = self.DEFAULT_PROMPT.copy()
        seed = random.randint(1000000, 10000000)
        word = self.RANDOM_WORD_LIST[seed % len(self.RANDOM_WORD_LIST)]
        new["prompt"] = f"(photography of {word}:1.2), realist, art, 50mm, design, 8k, hdr"
        new['seed'] = seed
        print(new)
        return new

    def parse_prompt(self, prompt_string):
        if (not prompt_string):
            return self.autoprompt()

        prompt_parts = prompt_string.split("\n")
        prompt_dict = dict(prompt=prompt_parts[0])
        if len(prompt_parts) > 1:
            prompt_dict["negative_prompt"] = prompt_parts[1]

        prompt_dict["width"], prompt_dict["height"] = prompt_parts[-1].split(
            ":")[-1].split("x")

        for part in prompt_parts[2:-1]:
            key, val = part.split(":")
            prompt_dict[key.strip().replace(" ", "_").lower()
                        ] = float(val.strip())
        prompt_dict["n_iter"] = 1
        return prompt_dict

    def generate(self, prompt_data={}, n=1):
        prompt = self.DEFAULT_PROMPT | prompt_data | dict(n_iter=n)
        resp = self._call(self.txt2img, prompt)
        for i, data in enumerate(resp['images']):
            img = Image.open(BytesIO(b64decode(data.split(",", 1)[0])))
            img.save(f'{self.OUTPUT_DIR}/img-{i+1}.jpg')
            self.metadata(data, header=f"{i+1}/{len(resp['images'])}:")

    def metadata(self, data, header=''):
        png_payload = dict(image="data:image/png;base64," + data)
        resp = self._call(self.png_info, png_payload)
        metadata = resp.get("info")
        print(header, metadata)
