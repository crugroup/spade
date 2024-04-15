---
sidebar_position: 1
---

# Airflow

The Airflow executor is an executor for triggering Airflow DAGs through Spade.
The repository for the executor can be found [here.](https://github.com/crugroup/spade-executor-airflow)

## Configuration

The executor can be installed by running:
```bash
pip install spade-executor-airflow
```

The executor requires some environment variables to be set in order to authenticate
with an Airflow instance:
- `SPADE_AIRFLOW_URL`: The URL of the airflow instance to connect to
- `SPADE_AIRFLOW_USERNAME`: The username of the account to use when authenticating
- `SPADE_AIRFLOW_PASSWORD`: The password of said account
- `SPADE_AIRFLOW_VERIFY_SSL`: When set to `true`, forces Airflow to verify SSL certificates
when connecting. Defaults to `true`. It's recommended to not touch this setting unless you know
what you're doing.

## Usage

The library comes with two classes, the executor itself, and a history provider.
The only required system parameter for the executor is `dag_id`, which contains the ID
of the DAG to execute. Any other system parameters, as well as any user parameters,
will be ignored.

The history provider of this DAG will query Airflow for the previous runs of the DAG, and
return the status and any other results for each run.
Note that this will query for *all* runs of the given DAG, not just the ones triggered by
Spade.
