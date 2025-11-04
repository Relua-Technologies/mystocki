def extract_street_type_abbreviation(street_with_street_type):
    for max_caracter in  range(3, 0, -1):
        if len(street_with_street_type) >= max_caracter:
            if street_with_street_type[max_caracter] == ' ':
                return street_with_street_type[:max_caracter]
    return None