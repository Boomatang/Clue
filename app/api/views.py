from flask import jsonify, abort
from app.utils import isInt

from app.api import api


def bom_api_test_function(ref):
    if ref.lower() == "tf":
        return {"error": "BOM ID not found \nPlease check your input"}
    else:
        num = int(ref[1:])

        if num > 10**4:
            return {"error": f"What are you playing at.\nYou asked for a result with {num} material types."}

        output = {"job number": f"{ref} test", "material": [], "total": num}

        index = 1

        while index <= num:
            output['material'].append({"size": f"beam size {index}", "qty": f"{index}"})
            index += 1

        return output


@api.route("/bom/<ref>", methods=['GET'])
def get_one_bom(ref):

    if ref.lower().startswith('t'):
        result = bom_api_test_function(ref)
    else:
        if not isInt(ref):
            return jsonify({"error": "BOM ID not found \nPlease check your input"}), 404

        result = {"error": "This feature is not working just yet!"}

    return jsonify(result)
