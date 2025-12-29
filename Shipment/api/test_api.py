import requests

url = "https://controllabbusan.pythonanywhere.com/api/ext/update/6308CMCD251120/"  # thay shipment_id thật

headers = {
    "Authorization": "Token 34ca8ac4dc6cee7addfcc366af2d7624621c725e",  # token vms
    "Content-Type": "application/json"
}

data = {
    "company": "PYTHON TEST",
    "vessel": "MV PYTHON",
    "quanty": "8",
    "remark": "Test from Python script"
}

response = requests.patch(url, json=data, headers=headers)
print(response.status_code)
print(response.json())