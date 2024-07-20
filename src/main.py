from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import requests
from datetime import datetime
from io import BytesIO
import extract_msg
import os

app = FastAPI()

CLICKUP_API_KEY = "pk_43030192_303UC2Z0VJEJ5QY9ES23X8I22ISAHUX2"
TASK_ID = "864dh2wwg"
CLICKUP_API_URL = f"https://api.clickup.com/api/v2/task/{TASK_ID}/comment"
DATA_DIR = "data"

def fetch_comments():
    headers = {
        "Authorization": CLICKUP_API_KEY
    }
    params = {
        "custom_task_ids": "true"
    }
    response = requests.get(CLICKUP_API_URL, headers=headers, params=params)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Error fetching comments from ClickUp API")
    return response.json()

def convert_timestamp(timestamp):
    dt = datetime.utcfromtimestamp(timestamp / 1000)
    return dt.strftime('%Y-%m-%d'), dt.strftime('%H:%M:%S')

def download_file(url, filename):
    response = requests.get(url)
    response.raise_for_status()
    with open(filename, 'wb') as file:
        file.write(response.content)

def read_msg_file(file_path):
    msg = extract_msg.Message(file_path)
    return {
        "subject": msg.subject,
        "sender": msg.sender,
        "to": msg.to,
        "date": msg.date,
        "body": msg.body,
        "attachments": [attachment.longFilename for attachment in msg.attachments]
    }

def organize_comments(data):
    comments = data.get("comments", [])
    sorted_comments = sorted(comments, key=lambda x: int(x.get("date", 0)))
    organized_data = []
    for comment in sorted_comments:
        comment_text = "".join([part.get("text", "") for part in comment.get("comment", [])])
        date, time = convert_timestamp(int(comment.get("date", 0)))
        attachments = []
        for part in comment.get("comment", []):
            if part.get("type") == "attachment":
                attachment_url = part.get("attachment", {}).get("url")
                attachment_name = part.get("text")
                attachments.append({
                    "name": attachment_name,
                    "url": attachment_url
                })
                if attachment_name.endswith('.msg'):
                    if not os.path.exists(DATA_DIR):
                        os.makedirs(DATA_DIR)
                    file_path = os.path.join(DATA_DIR, attachment_name)
                    download_file(attachment_url, file_path)
                    msg_data = read_msg_file(file_path)
                    print(msg_data)  # Process msg_data as needed

        organized_data.append({
            "user": comment["user"]["username"],
            "date": date,
            "time": time,
            "comment_text": comment_text,
            "attachments": attachments
        })
    return organized_data

@app.get("/clickup-comments")
def get_clickup_comments():
    data = fetch_comments()
    organized_data = organize_comments(data)
    return JSONResponse(content={"comments": organized_data})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
