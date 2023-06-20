import hashlib
import os
import requests
import mimetypes
from pathvalidate import sanitize_filename
import sys


class FileLoader:
    chunkSize = 8192000

    def __init__(self, host, api_key):
        self.host = host
        self.api_key = api_key
        self.session = requests.session()
        self.session.headers.update({"X-API-KEY": api_key})

        response = self.session.get(f"{host}/s3")
        if response.status_code != 200:
            self.host = False
            print("Check if your host is correct!")
            return
        self.s3Enabled = response.json()["enabled"]

    def uploadFile(self, filePath, fileName=None, parent=None):
        if not self.host:
            print("Check if your host is correct!")
            return

        parameter = {
            "name": fileName
        }
        response = self.session.post(f"{self.host}/api2/file", json=parameter)
        if response.status_code != 200:
            return
        fileID = response.json()["results"][0]
        result = self.updateFile(fileID, filePath, fileName=fileName)
        if not result:
            print("Upload not successful")
            return
        print(f"Upload successful, file_id: {file_id}")
        if parent and result:
            _print = False
            if "type" not in parent:
                _print = True
            if "id" not in parent:
                _print = True
            if "project" not in parent:
                _print = True
            if _print:
                print("parent must have the following structure: {project: project_id, type: x, id: item_id}\n "
                      "The type must be one out of: experiment, sample, researchitem, corresponding to your parent")
                return fileID
            response = self.session.get(f"{self.host}/api2/project/{parent['project']}/{parent['type']}")
            item = response.json()["results"][0]
            files = item["files"]
            files.append({"id": fileID})
            parameter = {"id": parent["id"],
                         "files": files}
            response = self.session.post(f"{self.host}/api2/project/{parent['project']}/{parent['type']}", json=parameter)
            if response.status_code != 200:
                print("file not attached to parent")
            print(f"File attached to parent: file_id: {fileID}")

        return fileID

    def updateFile(self, fileID, filePath, fileName=None):
        if not os.path.isfile(filePath):
            return False

        filePath = filePath.replace("\\", "/")
        if fileName is None:
            fileName = filePath.split("/")[-1]

        if self.s3Enabled:
            flag = self.s3Upload(fileID, fileName, filePath)
        else:
            flag = self.chunkUpload(fileID, fileName, filePath)
        return flag

    def chunkUpload(self, fileID, fileName, filePath):
        chunkIDList = []
        with open(filePath, "rb") as uploadFile:
            data = uploadFile.read(self.chunkSize)
            url = f"{self.host}/app1/chunks/add"
            session = requests.session()
            session.headers.update({
                "X-API-KEY": self.api_key,
                'Content-Type': 'application/octet-stream',
            })
            while data:
                md5 = self.getMD5(data)
                session.headers.update({
                    "MD5": md5,
                })
                response = session.post(url, data=data)
                if response.status_code != 200:
                    return False
                chunkID = response.json()["_value"]

                chunkIDList.append(chunkID)
                data = uploadFile.read(self.chunkSize)

        parameter = {
            "id": fileID,
            "chunks": chunkIDList,
            "name": fileName
        }
        response = self.session.post(f"{self.host}/api2/file", json=parameter)
        if response.status_code != 200:
            return False
        return True

    def s3Upload(self, fileID, fileName, filePath):


        mimeType = mimetypes.MimeTypes().guess_type(filePath)[0]
        if mimeType is None:
            mimeType = "text/plain"
        payload = {"filename": fileName, "type": mimeType,
                   "metadata": {"name": fileName, "type": mimeType},
                   "createFileObject": False}  # adjust for your file

        response = self.session.post(f"{self.host}/s3/multipart", json=payload)
        if response.status_code != 200:
            return False
        uploadData = response.json()
        fileSize = os.path.getsize(filePath)      # bytes
        numberOfChunks = (fileSize // self.chunkSize) + 1
        numberOfChunksString = "1"
        for i in range(2, numberOfChunks + 1):
            numberOfChunksString = f"{numberOfChunksString},{i}"

        response = self.session.get(f"{self.host}/s3/multipart/{uploadData['uploadId']}/batch", params={
            "key": uploadData['key'], 'partNumbers': numberOfChunksString})
        if response.status_code != 200:
            return False
        batches = response.json()

        chunkNumber = 1
        partsList = []
        with open(filePath, "rb") as uploadFile:
            data = uploadFile.read(self.chunkSize)
            while data:
                etag = requests.put(batches['presignedUrls'][f"{chunkNumber}"],
                                    data=data).headers['etag']
                partsList.append({
                    "PartNumber": chunkNumber, "ETag": etag
                })
                chunkNumber += 1
                data = uploadFile.read(self.chunkSize)

        partsDict = {"parts": partsList}
        response = self.session.post(f"{self.host}/s3/multipart/{uploadData['uploadId']}/complete", params={
            'key': uploadData['key']}, json=partsDict)
        if response.status_code != 200:
            return False

        parameter = {
            "id": fileID,
            "s3key": uploadData['key'],
            "name": fileName
        }
        response = self.session.post(f"{self.host}/api2/file", json=parameter)
        if response.status_code != 200:
            return False
        return True


    def downloadFile(self, fileID, folderPath, overwrite=False):
        if not os.path.isdir(folderPath):
            print("This is not valid folder")
            return False, None

        response = self.session.get(f"{self.host}/api2/file/{fileID}")
        file = response.json()
        file_name = file["name"]
        file_name = sanitize_filename(file_name)

        filePath = f"{folderPath}/{file_name}"

        if os.path.isfile(filePath):
            if overwrite is False:
                print("File already present!")
                return False, None

        response = self.session.get(f"{self.host}/files/{fileID}")
        with open(filePath, "wb+") as newFile:
            for chunk in response.iter_content(chunk_size=self.chunkSize):
                if chunk:  # filter out keep-alive new chunks
                    newFile.write(chunk)

        print(f"Download successful, file_id: {fileID}")

        return True, filePath


    def getMD5(self, byteData):
        return hashlib.md5(byteData).hexdigest()

if __name__ == "__main__":
    argv = sys.argv[1:]
    kwargs = {kw[0]: kw[1] for kw in [ar.split('=') for ar in argv if ar.find('=') > 0]}
    args = [arg for arg in argv if arg.find('=') < 0]

    host = kwargs.get("host")
    api_key = kwargs.get("api_key")
    if not host or not api_key:
        print("Please specify host and api_key")
        sys.exit()

    fl = FileLoader(host, api_key)

    file_path = kwargs.get("file_path")
    file_id = kwargs.get("file_id")
    file_name = kwargs.get("file_name")

    parent_project = kwargs.get("parent_project")
    parent_type = kwargs.get("parent_type")
    parent_id = kwargs.get("parent_id")
    parent = None
    if parent_project and parent_type and parent_id:
        parent = {
            "project": parent_project,
            "type": parent_type,
            "id": parent_id
        }
    download_folder = kwargs.get("download_folder")
    overwrite = kwargs.get("overwrite")
    if overwrite:
        if overwrite.lower() == "true":
            overwrite = True
        else:
            overwrite = False
    else:
        overwrite = False


    command = args[0]

    if command == "upload":
        file_id = fl.uploadFile(file_path, file_name, parent)

    elif command == "update":
        fl.updateFile(file_id, file_path, file_name)

    elif command == "download":
        fl.downloadFile(file_id, download_folder, overwrite)

    else:
        print("Unknown command")

