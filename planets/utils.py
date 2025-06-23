from urllib.parse import quote_plus

git a
def build_nasa_tap_url(table, columns, format='csv'):
    if not columns:
        raise ValueError("columns cannot be empty")

    query = f"select {','.join(columns)} from {table}"
    encoded_query = quote_plus(query)
    return f"https://exoplanetarchive.ipac.caltech.edu/TAP/sync?query={encoded_query}&format={format}"

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