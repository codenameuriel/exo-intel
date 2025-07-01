import csv
import requests
from io import StringIO
from django.db import transaction
from .models import StarSystem, Star, PlanetDiscovery, Planet
from .utils import build_nasa_tap_url

COLUMN_MAPPING = {
    'starsystem': {
        'model': StarSystem,
        'unique_on': 'name',
        'map': {
            'sy_name': 'name',
            'sy_snum': 'num_stars',
            'sy_pnum': 'num_planets',
            'sy_mnum': 'num_moons',
            'sy_dist': 'distance',
            'ra': 'ra',
            'dec': 'dec',
        }
    },
    'star': {
        'model': Star,
        'unique_on': 'name',
        'map': {
            'hostname': 'name',
            'st_spectype': 'spect_type',
            'st_mass': 'mass',
            'st_rad': 'radius',
            'st_teff': 'temperature'
        }
    },
    'planetdiscovery': {
        'model': PlanetDiscovery,
        # A combination of fields makes this unique
        'unique_on': ['method', 'year', 'locale', 'facility'],
        'map': {
            'discoverymethod': 'method',
            'disc_year': 'year',
            'disc_locale': 'locale',
            'disc_facility': 'facility'
        }
    },
    'planet': {
        'model': Planet,
        'unique_on': 'name',
        'map': {
            'pl_name': 'name',
            'pl_orbper': 'orbital_period',
            'pl_rade': 'radius_earth',
            'pl_masse': 'mass_earth',
            'pl_eqt': 'equilibrium_temperature',
            'pl_orbsmax': 'semi_major_axis',
            'pl_insol': 'insolation_flux'
        }
    }
}

TABLE_COLUMNS = {
    "ps": {
        "planet": [
            "pl_name", # planet name
            "hostname", # star name
            "pl_orbper", # orbital period in days (orbit around star)
            "pl_rade", # planet radius (measured in units of radius of Earth)
            "pl_masse", # planet mass (Earth mass)
            "pl_eqt", # equilibrium temperature (K)
            "pl_orbsmax", # orbit semi-major-axis (longest radius of elliptic orbit)
            "pl_insol", # insolation flux (Earth flux)
            "discoverymethod",
            "disc_year",
            "disc_locale",
            "disc_facility"
        ],
        "planetdiscovery": [
            "DISTINCT discoverymethod", # discovery method
            "disc_year", # discovery year
            "disc_locale", # location of planet observation (ground or space)
            "disc_facility" # name of facility of discovery
        ]
    },
    "stellarhosts": {
        "starsystem": [
            "sy_name", # system name
            "sy_snum", # num of stars in system
            "sy_pnum", # num of planets in system
            "sy_mnum", # num of moons in system
            "sy_dist", # distance - distance to system in parsecs
            "ra", # right ascension of system (longitude)
            "dec" # declination of system (latitude)
        ],
        "star": [
            "hostname", # star name
            "sy_name", # star system name
            "st_spectype", # spectral type
            "st_mass", # solar mass - amount of mass contained in star
            "st_rad", # solar radius - length from center of star to surface
            "st_teff" # effective temperature (K) - temperature of star
        ]
    }
}

def run_import(nasa_table, app_table, dry_run=False, logger=print):
    """
    A Celery task to fetch data from NASA and populate the database
    """

    logger(f"Starting background import for '{app_table}'...")

    try:
        columns = TABLE_COLUMNS[nasa_table][app_table]
        meta = COLUMN_MAPPING[app_table]
        model = meta['model']
    except KeyError:
        logger(f"Invalid combination of nasa-table '{nasa_table}' and app-table '{app_table}'")
        return "Import failed due to invalid arguments."

    url = build_nasa_tap_url(nasa_table, columns)
    logger(f"Fetching data from: {url}")

    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger(f"Failed to fetch data from NASA TAP service: {e}")
        return f"Import failed: Could not fetch data. {e}"

    csv_data = StringIO(response.text)
    reader = csv.DictReader(csv_data)
    created_count, updated_count, skipped_count = 0, 0, 0

    try:
        with transaction.atomic():
            for row in reader:
                # any empty string is converted to None
                cleaned_row = {k: v if v != '' else None for k, v in row.items()}

                try:
                    defaults = _build_defaults(cleaned_row, meta['map'])
                    is_identifier_present, lookup = _build_lookup(defaults, meta)

                    if not is_identifier_present:
                        logger(f"Skipping row because a unique identifier is missing: {cleaned_row}")
                        skipped_count += 1
                        continue

                    # prevent object creation or associations
                    if dry_run:
                        logger(f"[DRY RUN] Would update or create {model.__name__} with lookup: {lookup}")
                        continue

                    _add_related_objects_to_defaults(app_table, defaults, cleaned_row)

                    _, created = model.objects.update_or_create(**lookup, defaults=defaults)

                    if created:
                        created_count += 1
                    else:
                        updated_count += 1
                except StarSystem.DoesNotExist:
                    logger(f"Skipping star '{cleaned_row.get('hostname')}' because its host system '{cleaned_row.get('sy_name')}' does not exist. Import star systems first.")
                    skipped_count += 1
                except Star.DoesNotExist:
                    logger(f"Skipping planet '{cleaned_row.get('pl_name')}' because its host star '{cleaned_row.get('hostname')}' does not exist. Import stars first.")
                    skipped_count += 1
                except PlanetDiscovery.DoesNotExist:
                    logger(f"Skipping planet '{cleaned_row.get('pl_name')}' because its discovery record was not found. Import planet discoveries first.")
                    skipped_count += 1
                except Exception as e:
                    logger(f"Error processing row {row}: {e}")
                    skipped_count += 1

            # prevent committing empty transaction and carry out a rollback
            if dry_run:
                raise InterruptedError("Dry run complete, rolling back transaction")
    except InterruptedError:
        logger("\n[DRY RUN] Finished. No changes were made to the database.")
        return "Dry run complete."
    except Exception as e:
        logger(f"An error occurred during the database transaction: {e}")
        return f"Import failed: Transaction error. {e}"

    result_message = f"\nImporting complete! Created: {created_count}, Updated: {updated_count}, Skipped: {skipped_count}"
    logger(result_message)
    return result_message

def _build_defaults(row, field_map):
    """Builds a dictionary of model fields from the API row data"""
    return {model_field: row.get(api_field) for api_field, model_field in field_map.items()}

def _build_lookup(defaults, meta):
    """Builds the lookup dictionary and checks for identifiers."""
    is_identifier_present = True
    if isinstance(meta['unique_on'], list):
        lookup = {field: defaults.get(field) for field in meta['unique_on']}
        if any(v is None for v in lookup.values()):
            is_identifier_present = False
    else:
        unique_model_field = meta['unique_on']
        lookup_value = defaults.pop(unique_model_field, None)
        lookup = {unique_model_field: lookup_value}
        if lookup_value is None:
            is_identifier_present = False
    return is_identifier_present, lookup

def _add_related_objects_to_defaults(app_table, defaults, row):
    """Fetches/creates related objects and adds them to the defaults. ONLY RUNS ON NON-DRY RUNS."""
    if app_table == 'star':
        system_name = row.get('sy_name')
        if system_name:
            system = StarSystem.objects.get(name=system_name)
            defaults['system'] = system

    if app_table == 'planet':
        star_name = row.get('hostname')
        if star_name:
            star = Star.objects.get(name=star_name)
            defaults['host_star'] = star

        method = row.get('discoverymethod')
        year = row.get('disc_year')
        locale = row.get('disc_locale')
        facility = row.get('disc_facility')

        if any(field is not None for field in [method, year, locale, facility]):
            discovery = PlanetDiscovery.objects.get(
                method=method,
                year=year,
                locale=locale,
                facility=facility,
            )
            defaults['discovery'] = discovery