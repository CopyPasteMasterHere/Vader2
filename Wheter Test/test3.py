print("hello world")
import requests
response = requests.get("https://opendata-download-metfcst.smhi.se/api/category/pmp3g/version/2/parameter.json")
print(response.json())