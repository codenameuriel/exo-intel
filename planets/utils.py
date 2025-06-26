from decouple import config, UndefinedValueError

def build_nasa_tap_url(table, columns, format='csv'):
    if not columns:
        raise ValueError("columns cannot be empty")

    try:
        base_url = config("NASA_TAP_BASE_URL")
    except UndefinedValueError:
        raise UndefinedValueError("NASA_TAP_BASE_URL is not configured in the .env file")

    query_columns = ",".join(columns)

    query_param_value = f"select {query_columns} from {table}".replace(" ", "+")

    return f"{base_url}?query={query_param_value}&format={format}"

def try_float(val):
    try:
        return float(val)
    except (TypeError, ValueError):
        return None

def try_int(val):
    try:
        return int(val)
    except (TypeError, ValueError):
        return None