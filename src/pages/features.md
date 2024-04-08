# Features

Spade is all about simplicity. It does two things and does them well:

- **Upload a file**: Spade allows you to upload a file, which is the process by your custom Python code.
- **Do something**: Run your custom Python logic to do whatever you can code in Python

In reality there's more to it. Spade is:

- :scroll: **Auditable** - Spade keeps the history of user actions (file uploads and process executions)
- :muscle: **Flexible** - write your processes in Python. Do what you want with your files
- :page_with_curl: **Reusable** - run the same Python code with multiple sets of input parameters defined by admins
- :wrench: **Configurable** - use `react-json-form` to define custom forms and allow users input the parameters you need
- :lock: **Secure** - define roles to limit what users can do in Spade
- :rocket: **Quick to deploy** - we provide a reference Docker Compose file and a Helm chart to get your Spade instance up in no time
- :star: **Modern** - Spade leverages future proof technologies such as:
    * Django
    * Django Rest Framework
    * React
    * Refine.dev
    * Postgresql
- :zap: **Open** - intergate it with anything you can connect to with Python. We use Spade as a business user friendly 
  interface for Apache Airflow, but you can do whatever your imagination permits.

# Why Spade

Our needs were simple - a web interface for business users to upload files and trigger simple processes.
On one hand there were tools with powerful features, but too complex for business users, such as Airflow or Dagster,
on the other hand there were tools like Airtable, which allow data input and simple workflows, but are not flexible enough.
We needed something in between, and we built Spade.

# The future

Spade is CRU's gift to the open source community. We built it to power critical business processes at CRU,
but we designed it in an extremely flexible and generic way, to easily expand for our future use cases.
There are two ways Spade will be extended in the future:

## Core Spade

While we consider Spade to be a complete concept, we are aware there are areas where the functionalities can
be improved or extended. Our immediate plans include:

* Process level permissions
* Pluggable authentication providers, such as Azure Active Directory or Okta
* Asynchronous process execution

Those are our ideas, but if you have yours that would make Spade better, we'll certainly listen.
Just open a Github issue or pull request and we'll go from there

## Executors and File Processors

We intergrate spade with Apache Airflow, but you can integrate it with anything. If you want to share
your extensions, just open a PR to the documentation and we'll present your work in the
[Extensions](/extensions/intro) section.
