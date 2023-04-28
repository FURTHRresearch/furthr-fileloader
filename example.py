from FileLoader import FileLoader
import requests

# init file_loader
host = "you host"
api_key = "your api_key"
file_loader = FileLoader(host, api_key)

# To attach the file to a parent object, specify parent_project_name name, parent_type and parent_name.
# The script will search for the correct project_id and parent_id
parent_project_name = "Test"
parent_type = "experiment"
parent_name = "Name of experiment"

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
    print("upload with parent")
    parent = {"project":project_id,
              "id": exp_id,
              "type": "experiment"}
    file_id = file_loader.uploadFile("test_file.txt", parent=parent)
else:
    print("upload without parent")
    file_id = file_loader.uploadFile("test_file.txt")

print(file_loader.downloadFile(file_id, "test_download"))

