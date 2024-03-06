---
sidebar_position: 5
---

# Parameters

Executors and File Processors have two ways of receiving parameters for each run:
**system parameters** and **user parameters**.

Both types of parameters are simple JSON objects, and can accept any type of data that
is serialisable to JSON. 

## System Parameters
System parameters are parameters sent to the [Process](process.md) or [File](file.md) for every
run, and are meant for things that do not change between runs, e.g. a table to write to in a database,
or a specific URL to send HTTP requests to. These are set as part of a File or Process, and require
write privileges to edit.
Note that this should **not** be used to store things like authentication credentials, as they are
not encrypted and can be accessed by anyone with view privileges on the File or Process.

## User Parameters
User parameters are designed for parameters that can change for every run, and are set by the user
each time they are triggered. These are defined as a [JsonSchema](https://json-schema.org) in the
admin panel, and are displayed as a form to the user for each run. The final results of that form
are sent as a Python dictionary to the underlying [Executor](executor.md) or
[File Processor](file-processor.md).