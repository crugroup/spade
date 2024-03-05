---
sidebar_position: 1
---

# File

A **File** represents a definition of a file type that can be uploaded to Spade.
When you configure a File, you can specify:

* The file code (a unique identifier for the File)
* Description
* File format (e.g. PDF, XLSX, etc.)
* Tags
* File Processor (the Python class that Spade runs to process the file)
  see [File Processor](/docs/key-concepts/spade-sdk/file-processor.md)
* System & user parameters (see [Parameters](/docs/key-concepts/parameters.md))
* Linked process - the process that Spade automatically starts when a file is uploaded

## Uploading a File

When you upload a file, the following steps occur:
1. A form is displayed to the user to upload the file. If user parameters are defined,
   the user is prompted to enter them.
2. The file is processed by the File Processor.
3. Spade saves the results of the processing in the database, together with the following metadata:
    * Name of the uploaded file
    * Date and time of the upload
    * User who uploaded the file
    * Size of the file
    * Number of records in the file
    * Additional metadata defined by the File Processor. This can be any JSON-serializable data.

You can browse the history of file uploads in the File page.