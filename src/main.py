import requests

task_id = "864dh2wwg"
url = "https://api.clickup.com/api/v2/task/" + task_id + "/comment"

query = {
  "custom_task_ids": "true",
  "team_id": "123",
  "start": "0",
  "start_id": "string"
}

headers = {"Authorization": "pk_43030192_303UC2Z0VJEJ5QY9ES23X8I22ISAHUX2"}

response = requests.get(url, headers=headers, params=query)

data = response.json()
print(data)