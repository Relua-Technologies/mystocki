def empty_string_to_null(value):
    if value == "":
        return None
    return value


def replace_empty_strings_with_none_in_dict(dictionary):
    for key, value in dictionary.items():
        dictionary[key] = empty_string_to_null(value)
    return dictionary
