from apps.utils.extractions.extract_street_type_abbreviation import extract_street_type_abbreviation
from apps.utils.choices.street_type import STREET_TYPE_DICT


def extract_street_and_type(street_with_street_type):
    street_type_abbreviation = extract_street_type_abbreviation(street_with_street_type)
    if street_type_abbreviation:
        street = street_with_street_type.replace(street_type_abbreviation, '', 1).strip()
        street_type = STREET_TYPE_DICT.get(street_type_abbreviation)
        return street_type, street
    else:
        return None, street_with_street_type
