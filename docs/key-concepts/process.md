---
sidebar_position: 3
---

# Process

A **Process** is very similar to a [File](/docs/key-concepts/file.md), in that it runs Python code on user action.
There are a few differences, however:
1) There's no input file attached on process execution
2) A process cannot be linked to another process
3) The history of process runs can come from an external source, such as a database or API. For more details,
   see [history-provider](/docs/key-concepts/spade-sdk/history-provider.md)

Process configuration works in a similar way to [File configuration](/docs/key-concepts/file.md)