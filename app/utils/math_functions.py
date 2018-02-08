def isFloat(num):
    try:
        float(str(num))
        return True
    except ValueError:
        return False
