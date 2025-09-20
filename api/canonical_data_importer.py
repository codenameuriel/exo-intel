import json
from pathlib import Path

from django.db import transaction

from .models import PlanetDiscovery, StarSystem, Star, Planet

APP_ROOT = Path(__file__).resolve().parent.parent

APP_TABLE_IMPORT_CONFIG = {
    "star_systems": {
        "model": StarSystem,
        "source_file": f"{APP_ROOT}/data/canonical_star_systems.json",
        "unique_on": "name",
        "field_map": {
            "sy_name": "name",
            "sy_snum": "num_stars",
            "sy_pnum": "num_planets",
            "sy_mnum": "num_moons",
            "sy_dist": "distance_parsecs",
            "ra": "ra",
            "dec": "dec",
        }
    },
    "planet_discoveries": {
        "model": PlanetDiscovery,
        "source_file": f"{APP_ROOT}/data/canonical_planet_discoveries.json",
        "unique_on": ["method", "year", "locale", "facility"],
        "field_map": {
            "discoverymethod": "method",
            "disc_year": "year",
            "disc_locale": "locale",
            "disc_facility": "facility",
        }
    },
    "stars": {
        "model": Star,
        "source_file": f"{APP_ROOT}/data/canonical_stars.json",
        "unique_on": "name",
        "field_map": {
            "hostname": "name",
            "st_spectype": "spectral_type",
            "st_mass": "mass_sun",
            "st_rad": "radius_sun",
            "st_teff": "effective_temperature_k",
            "st_lum": "luminosity_sun",
            "st_age": "age_gya",
        },
        "relationships": {
            "system": {
                "model": StarSystem,
                "lookup_keys": ["sy_name"],
                "lookup_fields": ["name"],
            }
        }
    },
    "planets": {
        "model": Planet,
        "source_file": f"{APP_ROOT}/data/canonical_planets.json",
        "unique_on": "name",
        "field_map": {
            "pl_name": "name",
            "pl_orbper": "orbital_period_days",
            "pl_rade": "radius_earth",
            "pl_masse": "mass_earth",
            "pl_eqt": "equilibrium_temperature_k",
            "pl_orbsmax": "semi_major_axis_au",
            "pl_insol": "insolation_flux_earth",
            "pl_orbeccen": "orbital_eccentricity",
        },
        "relationships": {
            "host_star": {
                "model": Star,
                "lookup_keys": ["hostname"],
                "lookup_fields": ["name"],
            },
            "discovery": {
                "model": PlanetDiscovery,
                "lookup_keys": ["discoverymethod", "disc_year", "disc_locale", "disc_facility"],
                "lookup_fields": ["method", "year", "locale", "facility"],
            }
        }
    }
}

IMPORT_ORDER = [
    "star_systems",
    "planet_discoveries",
    "stars",
    "planets",
]


def run_canonical_data_import(dry_run=False, logger=print):
    """
    Reads from the pre-processed canonical JSON files and populates the database
    in a specific, dependency-aware order.
    """
    logger("--- Starting Import from Canonical Data Files ---")

    result_message = ""

    try:
        with transaction.atomic():
            for app_table in IMPORT_ORDER:
                config = APP_TABLE_IMPORT_CONFIG[app_table]
                import_message = _import_app_table_data_from_file(app_table, config, dry_run, logger)
                result_message += import_message

            if dry_run:
                raise InterruptedError("[DRY RUN] No changes were made to the database")
    except InterruptedError as e:
        logger(f"{str(e)}")
    except Exception as e:
        raise Exception("An unexpected error occurred during the canonical data import") from e

    logger("--- Finished Import from Canonical Data Files ---")
    logger(result_message)

    return result_message


def _import_app_table_data_from_file(app_table, config, dry_run, logger):
    """
    Import data for a single app table from a JSON file.
    """
    source_file = config["source_file"]

    logger(f"\nImporting '{app_table}' from '{source_file}'...")

    model = config["model"]

    try:
        with open(source_file, "r") as f:
            canonical_records = json.load(f)
            logger(f"Loaded {len(canonical_records)} records from source file.")
    except FileNotFoundError as e:
        raise FileNotFoundError(f"Source file '{source_file}' not found") from e

    created_count, updated_count, skipped_count = 0, 0, 0

    for canonical_record in canonical_records:
        defaults = {
            app_field: canonical_record.get(nasa_field)
            for nasa_field, app_field in config["field_map"].items()
        }
        lookup = _build_lookup(defaults, config)

        if not lookup:
            skipped_count += 1
            continue

        if dry_run:
            continue

        if "relationships" in config:
            _link_relationships(defaults, canonical_record, config["relationships"])

        _, created = model.objects.update_or_create(**lookup, defaults=defaults)
        if created:
            created_count += 1
        else:
            updated_count += 1

    result_message = f"'{app_table}' import finished. Created: {created_count}, Updated: {updated_count}, Skipped: {skipped_count}\n"
    logger(result_message)
    return result_message


def _build_lookup(defaults, config):
    """
    Builds the lookup dictionary for update_or_create and validates identifiers.
    """
    unique_on = config["unique_on"]
    if isinstance(unique_on, list):
        lookup = {field: defaults.get(field) for field in unique_on}
        if any(v is None for v in lookup.values()):
            return None  # all unique on field values must be present to be valid
        return lookup
    else:
        value = defaults.pop(unique_on, None)
        if value is None:
            return None
        return {unique_on: value}


def _link_relationships(defaults, canonical_record, relationships_config):
    """
    Fetches related objects and adds them to the defaults.
    """
    for model_field, rel_config in relationships_config.items():
        related_model = rel_config["model"]
        lookup = {
            field: canonical_record.get(key) for field, key in
            zip(rel_config["lookup_fields"], rel_config["lookup_keys"])
        }
        related_obj = related_model.objects.get(**lookup)
        defaults[model_field] = related_obj
