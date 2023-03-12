from sd_api import SD_API

url = input("Enter Stable-Diffusion URL: ")
api = SD_API(url)
api.generate()
