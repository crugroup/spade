import importlib


def import_object(object_path: str):
    module_path, object_name = object_path.rsplit(".", 1)
    module = importlib.import_module(module_path)
    return getattr(module, object_name)
