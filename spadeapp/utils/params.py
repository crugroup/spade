import json


def parse_user_params(user_params) -> dict:
    """
    Parse user params sent to a process run or file upload.

    Accepts a JSON string (empty means no params), ``None`` or an already parsed dict,
    as sent by JSON and multipart requests respectively.

    Raises:
        ValueError: If the params are not a JSON object.
    """
    if user_params is None:
        return {}
    if isinstance(user_params, str):
        if not user_params:
            return {}
        try:
            user_params = json.loads(user_params)
        except json.JSONDecodeError as e:
            raise ValueError("Failed to parse user params as JSON") from e
    if not isinstance(user_params, dict):
        raise ValueError("User params must be a JSON object")
    return user_params
