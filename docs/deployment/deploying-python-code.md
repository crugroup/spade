---
sidebar_position: 1
---

# Deploying Python code

Spade is nothing without your custom executors and file processors.

We generally recommend one of the two approches:

* extend the Spade Docker image with your custom code packaged as Python packages
* mount a volume with your custom code to the Spade Docker container, and set `PYTHONPATH` to point to it