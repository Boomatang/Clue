from flask import flash


def flash_massages(massage_list):
    for massage in massage_list:
        if massage[1] is None:
            status = "General"
        else:
            status = massage[1]
        flash(massage[0], status)


def error_builder(errors):
    msg = "There was a problem with: "

    for error in errors:
        msg = msg + error + " "

    return msg
