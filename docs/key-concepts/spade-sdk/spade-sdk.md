---
sidebar_position: 1
---

# Spade SDK
The **Spade SDK** is a library containing type definitions for all of the concepts
within Spade, so you can write extensions without having to import the entire
library into your dependencies. It can be installed using pip:

```bash
pip install spadesdk
```

Any classes that will be used as [Executors](executor.md), [File Processors](file-processor.md)
and [History Providers](history-provider.md) **must** derive from the classes in this SDK.

