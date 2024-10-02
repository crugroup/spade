---
sidebar_position: 4
---

# File Processor
An **File Processor** is a class designed receive and process an arbitrary file, and are the
backbone of [Files](../file.md).

The main method that defines a File Processor is `process`:

```python
class FileProcessor:
    @classmethod
    def process(cls, file: File, filename: str, data, user_params: dict | None, user: User, *args, **kwargs) -> FileUpload:
        pass
```

The method is used as a class method, and should not store anything that isn't required
for every use of this executor (these should go in [parameters](../parameters.md) instead).

When a run is triggered, this method is called with the File object (containing the file
format and system parameters), the file name, the file data in bytes, and the user parameters.
The result is a FileUpload object, denoting things such as if the job was successful, any output
of the action, or an error message if something went wrong. 

In the FileUpload, you can also store additional metadata about the file, such as:
* Size of the file
* Number of records
* Any other custom metadata that can be respresented as a JSON serialisable Python dictionary
