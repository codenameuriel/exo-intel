import csv
import io
import json
import re
from html.parser import HTMLParser

import requests

from api.utils import build_nasa_tap_url

TABLE_FIELD_SELECTION_CONFIG = {
    "ps": {
        "planets": [
            "pl_name",  # planet name
            "hostname",  # host star name
            "pl_orbper",  # orbital period in days (orbit around star)
            "pl_rade",  # planet radius (measured in units of Earth radius)
            "pl_masse",  # planet mass (Earth mass)
            "pl_eqt",  # equilibrium temperature (K)
            "pl_orbsmax",  # orbit semi-major-axis (longest radius of elliptic orbit)
            "pl_insol",  # insolation flux (Earth flux)
            "pl_orbeccen",  # orbital eccentricity (how much orbit deviates from a circle)
            "pl_refname",  # reference of publication
            "discoverymethod",
            "disc_year",
            "disc_locale",
            "disc_facility",
        ],
    },
    "stellarhosts": {
        "stars": [
            "hostname",  # star name
            "sy_name",  # star system name
            "st_spectype",  # spectral type
            "st_mass",  # solar mass - amount of mass contained in a star
            "st_rad",  # solar radius - length from the center of star to surface
            "st_teff",  # effective temperature (K) - temperature of a star
            "st_lum",  # amount of energy emitted by a star
            "st_age",  # age of star
            "st_refname",  # reference of publication
            "sy_snum",  # num of stars in star system
            "sy_pnum",  # num of planets in star system
            "sy_mnum",  # num of moons in star system
            "sy_dist",  # distance to a star system in parsecs
            "ra",  # right ascension of a star system (longitude)
            "dec",  # declination of a star system (latitude)
        ],
    },
}


class LinkTextParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text = ""

    def handle_data(self, data):
        self.text += data


def get_publication_year_from_reference(reference_string):
    """
    Extracts the latest plausible year from a reference string, which may contain HTML.
    """
    default_year = 1900

    if not isinstance(reference_string, str):
        return default_year

    parser = LinkTextParser()
    parser.feed(reference_string)
    clean_text = parser.text or reference_string

    found_years = re.findall(r'\b(19|20)\d{2}\b', clean_text)
    if found_years:
        return max([int(year) for year in found_years])

    return default_year


def fetch_raw_nasa_data(nasa_table, app_table, logger=print):
    """
    Fetches raw data from the NASA API for a given table and returns it as a
    list of dictionaries (one for each row).
    """
    logger(f"Starting data extraction for '{app_table}' from NASA table '{nasa_table}'...")

    columns = TABLE_FIELD_SELECTION_CONFIG[nasa_table][app_table]

    try:
        url = build_nasa_tap_url(nasa_table, columns)

        logger(f"Fetching data from: {url}")

        response = requests.get(url)
        response.raise_for_status()

        csv_data = io.StringIO(response.text)
        reader = csv.DictReader(csv_data)

        # convert the reader object to a list of dictionaries
        data = [{k: v if v != "" else None for k, v in row.items()} for row in reader]

        logger(f"Successfully extracted {len(data)} raw records for '{app_table}'.")

        return data
    except AttributeError as e:
        raise e
    except requests.exceptions.RequestException as e:
        logger(f"[ERROR] Failed to fetch data from NASA TAP service: {e}")
        raise e
    except Exception as e:
        logger("[ERROR] An unexpected error occurred")
        raise e


def transform_and_consolidate(raw_data, group_by_key, sort_config):
    """
    Groups, sorts and merges fragmented records into a single canonical record.
    """
    grouped_data = {}
    for record in raw_data:
        key = record.get(group_by_key)
        if key:
            grouped_data.setdefault(key, []).append(record)

    canonical_records = []
    for key, records in grouped_data.items():
        if sort_config.get("derive_sort_key"):
            # generate a sort key for each record by parsing the reference string
            for record in records:
                record[sort_config["sort_key_name"]] = (
                    get_publication_year_from_reference(record[sort_config["source_field_name"]])
                )

            records.sort(key=lambda r: int(r.get(sort_config["sort_key_name"]) or 0), reverse=True)

        canonical_record = {}
        for record in records:
            for field, value in record.items():
                if canonical_record.get(field) is None and value is not None:
                    canonical_record[field] = value

        # create a set of all fields across all records
        all_fields = {k for r in records for k in r.keys()}
        for field in all_fields:
            if field not in canonical_record:
                canonical_record[field] = None

        canonical_records.append(canonical_record)

    return canonical_records


def extract_unique_from_raw_data(raw_data, unique_on_keys):
    """
    Extracts unique records based on a composite key.
    """
    unique_records = set()
    for row in raw_data:
        unique_vals = tuple(row.get(key) for key in unique_on_keys)
        if any(item is not None for item in unique_vals):
            unique_records.add(unique_vals)

    record_list = [dict(zip(unique_on_keys, unique_vals)) for unique_vals in unique_records]
    return record_list


def write_data_to_file(data, filepath):
    """
    Writes canonical data to JSON file.
    """
    try:
        with open(filepath, "w") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        raise e


def run_canonical_data_consolidation(logger=print):
    """
    Runs the canonical data consolidation process.
    """
    try:
        logger("--- Starting Canonical Data Consolidation ---")

        star_system_sort_config = {"sort_key_name": "sy_name"}
        star_sort_config = {
            "sort_key_name": "publication_year",
            "source_field_name": "st_refname",
            "derive_sort_key": True
        }
        planet_sort_config = {
            "sort_key_name": "publication_year",
            "source_field_name": "pl_refname",
            "derive_sort_key": True
        }

        raw_star_data = fetch_raw_nasa_data(nasa_table="stellarhosts", app_table="stars", logger=logger)
        raw_planet_data = fetch_raw_nasa_data(nasa_table="ps", app_table="planets", logger=logger)

        unique_star_system_keys = ["sy_name", "sy_snum", "sy_pnum", "sy_mnum", "sy_dist", "ra", "dec"]
        raw_star_system_data = extract_unique_from_raw_data(raw_star_data, unique_star_system_keys)

        unique_planet_discovery_keys = ["discoverymethod", "disc_year", "disc_locale", "disc_facility"]
        canonical_discoveries = extract_unique_from_raw_data(raw_planet_data, unique_planet_discovery_keys)

        canonical_planets = transform_and_consolidate(raw_planet_data, "pl_name", planet_sort_config)
        canonical_stars = transform_and_consolidate(raw_star_data, "hostname", star_sort_config)
        canonical_star_systems = transform_and_consolidate(raw_star_system_data, "sy_name", star_system_sort_config)

        write_data_to_file(canonical_stars, "data/canonical_stars.json")
        write_data_to_file(canonical_planets, "data/canonical_planets.json")
        write_data_to_file(canonical_star_systems, "data/canonical_star_systems.json")
        write_data_to_file(canonical_discoveries, "data/canonical_planet_discoveries.json")

        return "Successfully completed canonical data consolidation."
    except Exception as e:
        message = "[ERROR] An error occurred while fetching data from NASA TAP service"
        logger(message)
        raise Exception(message) from e


if __name__ == "__main__":
    run_canonical_data_consolidation()
