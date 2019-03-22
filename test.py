import requests

res = requests.post("http://127.0.0.1:8000/card/balance", data={'username': '110201500467700', 'password': '147258'})

print(res.text)
