import json
import requests

acces_token = "ya29.a0ARrdaM8RbbtwWGmSAafFw3XyN5HE22So0Ts0kPvd8kUpWG-DpC9ROJLUrFYX5Cv9RHZBeaiT3OPRTtBEA_kcUlPy1l78YKJ-KcKauK50CVycrK0b9lV2pE070Wo4FivyvsnoExN11tUPO4nEIy0DFgcWG4ZH"

headers = {"Authorization" : f"Bearer {acces_token}"}
para = {
    "name" : "sample.txt"
}

files = {
    'data': ('metadata', json.dumps(para), 'application/json; charset=UTF-8'),
    'file': open("./dummy.txt", "rb")
}
r = requests.post(
    "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart",
    headers=headers,
    files=files
)



