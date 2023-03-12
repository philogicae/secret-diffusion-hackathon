import requests
import json
from rich import print
from os import getenv
from dotenv import load_dotenv
load_dotenv()
token = getenv("IPFS")


class IFPS_api:
    def __init__(self):
        self._api_url = 'https://api.nft.storage/upload/'
        self._headers_image = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'image/jpg'
        }
        self._headers_text = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'text/plain'
        }

    def post_image(self, name, image):
        with open(image, 'rb') as f:
            data = f.read()
        res = requests.post(url=self._api_url,
                            data=data,
                            headers=self._headers_image)
        cid = str(json.loads(res.text)['value']['cid'])
        url = f'https://ipfs.io/ipfs/{cid}?filename={name}.jpg'
        return cid, url

    def post_secret(self, name, secret):
        res = requests.post(url=self._api_url,
                            data=json.dumps({'secret': secret}),
                            headers=self._headers_text)
        cid = str(json.loads(res.text)['value']['cid'])
        url = f'https://ipfs.io/ipfs/{cid}?filename={name}.json'
        return cid, url

    def post_metadata(self, name, metadata):
        res = requests.post(url=self._api_url,
                            data=json.dumps(metadata),
                            headers=self._headers_text)
        cid = str(json.loads(res.text)['value']['cid'])
        url = f'https://ipfs.io/ipfs/{cid}?filename={name}.json'
        return cid, url

    def post(self, name, secret, image):
        img_cid, img_url = self.post_image(name, image)
        scrt_cid, scrt_url = self.post_secret(name, secret)
        metadata = {
            "name": name,
            "description": scrt_url,
            "image": img_url,
            "attributes": []
        }
        cid, url = self.post_metadata(name, metadata)
        return dict(
            secret=dict(cid=scrt_cid, url=scrt_url),
            image=dict(cid=img_cid, url=img_url),
            metadata=dict(cid=cid, url=url)
        )


if __name__ == '__main__':
    name = 'btc'
    secret = 'my secret'
    image = 'src/output/img-1.jpg'
    ifps = IFPS_api()
    result = ifps.post(name, secret, image)
    print(result)
