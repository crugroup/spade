---
sidebar_position: 5
---

# Variables and Variable Sets

**Variables** and **Variable Sets** are key features in Spade that allow you to manage configuration values, secrets, and reusable parameters across your processes and files.

## Variables

Variables in Spade are key-value pairs that can store configuration data, environment-specific values, secrets, and other parameters that your processes and file processors might need. Variables can be marked as secret, in which case:
- Their values are encrypted in the database
- They are write-only in the UI and API (you can set them, but not read them back)
roups

## Variable Sets

**Variable Sets** are collections of related variables that can be applied together to processes or file operations. They provide a way to group configuration values logically.

## Using Variables in Processes and Files

Variables and variable sets can be linked to your processes and file processors. When a process or file operation is executed, Spade injects them into `system_params`.

