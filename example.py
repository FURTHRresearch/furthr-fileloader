from FileLoader import FileLoader
import os
import requests

# host = "https://test.furthrmind.app"
host = "http://127.0.0.1:5000"

# api_key is saved in home directory
home = os.path.expanduser("~")
with open(f"{home}/furthrmind_test_apikey.txt") as f:
    api_key = f.read()

# init file_loader
file_loader = FileLoader(host, api_key)

# get a test parent from a test project
session = requests.session()
session.headers.update({"X-API-KEY": api_key})

response = session.get(f"{host}/api2/project")
projects = response.json()["results"]
project_id = exp_id = None
for project in projects:
    if project["name"] == "Test":
        project_id = project["id"]
        for exp in project["experiments"]:
            if exp["name"] == "Test":
                exp_id = exp["id"]
                break
        break

if project_id and exp_id:
    parent = {"project":project_id,
              "id": exp_id,
              "type": "experiment"}
    print(parent)
    file_id = file_loader.uploadFile("test_file.txt", parent=parent)
    print(file_id)

    print(file_loader.downloadFile(file_id, "test_download"))

