# Getting started
This little python application can be used to upload and download file to your FURTHRmind 
server. If you do not use python, we provide a windows binary that can 
be used from other programming languages.

Copy the FileLoader.py to your project and create an instance of the class 
FileLoader. The needed packages can be found in the 'Pipfile'.

You need to pass the url to your server as well as your api_key when creating 
the FileLoader instance. You can create an api_key in your user setting 
on your FURTHRmind server application.

```
from FileLoader import FileLoader
file_loader = FileLoder(host, api_key) 
```

### Upload
To upload a file, call the upload method of your FileLoader instance:
```
file_loader.upload(file_path, file_name=None, parent=None)
```
The file_path is mandatory, while file_name and parent are optional. If not 
specifying the file_name, the file_name of the given file will be used.

By specifying the parent, you can attach the uploaded file directly to an object,
such as an experiment, a sample, or another researchitem.

The parent must look like this:
```
parent = {
        project: <project_id>,  # the id of the project where your parent object belongs to
        type: <type>,           # The type of your parent object, must be one out of: experiment, sample, researchitem
        id: <id>                # the id of your parent object
    }
```
## Update
To update existing files, you must call the update method of your FileLoader 
instance. You must specify the file_id of the file you want to update and 
the file_path of the new file. The file_name is again optional.

```
file_loader.update(file_id, file_path, file_name=None)
```

## Download
To download files, your need to call the download method of your FileLoader
instance. You must specify the file_id, that should be downloaded and a folder
where the file should be saved. Optionally you can specify whether an existing 
file with the same name in the download_folder shall be overwritten. Default 
behaviour is 'False'

```
file_loader.download(file_id, download_folder, overwrite=False)
```

## Example
An example on how to use the python class can be found in the example.py

## Usage of FileLoader.exe
The windows binary is used very similar to the python class. Execute the exe file, 
specify an command and pass some options. The host and api_key options are mandatory.

```
FileLoader.exe <command> host=<host> api_key=<api_key> option1=value1 option2=value2
```
### Upload
To upload files with the executable, use the ``upload`` command. The following 
options are available: 

```
file_path=<path_to_file>    # This option is mandatory 
file_name=<file_name>       # To specify a different file name 
parent_project=<project_id> # The id of the project where your parent object belongs to
parent_type                 # The type of your parent object, must be one out of: experiment, sample, researchitem   
parent_id                   # The id of your parent object
```

Example:
```
.\FileLoader.exe upload host=http://127.0.0.1:5000 api_key=<api_key> file_path=<absolute_file_path> 
                        parent_project=<project_id> parent_id=<parent_id> parent_type=<experiment or sample or researchitem>

```

### Download
To upload files with the executable, use the ``download`` command. The following 
options are available: 

```
file_id=<file_id>                    # The file_id of the file you want to download. This option is mandatory 
download_folder=<download_folder>    # Absolute path to the folder, where the file should be saved. This option is also mandatory
overwrite=false                      # false or true: Whether an existing file with the same name in the download_folder should be overwritten
```