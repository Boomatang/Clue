def hasName(string):
    """Checks if a string is longer than zero"""
    if len(string) > 0:
        return True
    else:
        return False


def hasValues(values):
    """Checks if a list is longer than zero"""
    return hasName(values)
