import os

TRUTH_VALUES = ("yes", "true", "1", "on")
comission_percentage = 5


def get_bool_config(name, default=False):
    """
    Get bool configuration from environment variables
    """
    try:
        env_var = os.environ[name]
    except KeyError:
        return default
    return env_var.lower() in TRUTH_VALUES


def get_value(request, key, ignore_case=False):
    if ignore_case:
        for param_key in request.query_params.keys():
            if param_key.lower() == key.lower():
                return request.query_params[param_key]

        for data_key in request.data.keys():
            if data_key.lower() == key.lower():
                return request.data[data_key]

        return None

    else:
        value = request.query_params.get(key, None)
        if not value:
            value = request.data.get(key, None)
        return value
