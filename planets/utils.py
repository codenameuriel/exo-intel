from django.conf import settings


def build_nasa_tap_url(table, columns, format="csv"):
    if not columns:
        raise ValueError("columns cannot be empty")

    try:
        base_url = settings.NASA_TAP_BASE_URL
    except AttributeError:
        raise AttributeError(
            "NASA_TAP_BASE_URL is not configured in the settings. Ensure that is is defined in the correct .env file."
        )

    query_columns = ",".join(columns)

    query_param_value = f"select {query_columns} from {table}".replace(" ", "+")

    return f"{base_url}?query={query_param_value}&format={format}"