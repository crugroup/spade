---
sidebar_position: 10
---

# Versioning

Spade is more than one component, so to make sure they work well together, we need have
consistent versioning across them. This applies not just to the code and its artifact,
but also to Docker images.

We'll do our best to follow Semantic Versioning once we reach a stable state (v1)
for components. Until then we promise our best efforts to not break things.

## Spade SDK

Spade SDK follows a standard `major.minor.revision` version number pattern. From 1.0.0
Semantic Versioning rules will apply.

At present, the Github repo only has a `main` branch, and with the code being as simple as it is now,
we don't think there's an need for a more advanced Git workflow.

The Pypi package versions are consistent with Github tags

## Spade

### Docker images

We provide the following tags for Spade Docker images:
* `latest` - the latest stable release on `main` branch
* `major.minor.revision` - based on a Github release tag
* `develop` - the latest development version on `develop` branch

## Spade UI

### Docker images

The rules for Spade UI Docker images are the same as for Spade.