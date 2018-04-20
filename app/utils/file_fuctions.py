def file_ext_checker(file_name, ext):

    if file_name.lower().endswith(ext.lower()):
        return True
    else:
        return False
