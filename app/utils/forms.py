def key_preferred(value: str):
    if value.endswith('preferred'):
        return True
    else:
        return False


def key_checkbox(value: str):
    if value.endswith('checkboxes'):
        return True
    else:
        return False
