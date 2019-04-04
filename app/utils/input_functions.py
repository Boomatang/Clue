def hasName(string):
    """Checks if a string is longer than zero"""
    try:
        if len(string) > 0:
            return True
        else:
            return False
    except TypeError:
        return False


def hasValues(values):
    """Checks if a list is longer than zero"""
    return hasName(values)


def hasGroup(group):
    """Checks for a group value"""
    return hasName(group)
