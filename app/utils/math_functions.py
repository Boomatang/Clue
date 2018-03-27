def isFloat(num):
    try:
        float(str(num))
        return True
    except ValueError:
        return False


def isInt(num):
    try:
        int(str(num))
        return True
    except ValueError:
        return False
