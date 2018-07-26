from flask import jsonify

from app.models import BomResult
from app.utils import isInt

from app.api import api


def bom_api_test_function(ref):
    if ref.lower() == "tf":
        return {"error": "BOM ID not found \nPlease check your input"}
    else:
        num = int(ref[1:])

        if num > 10**4:
            return {"error": f"What are you playing at.\nYou asked for a result with {num} material types."}

        output = {"job number": f"{ref} test",
                  "material": [],
                  "total": num,
                  "massage": f"Found data for ID {ref}"}

        index = 1

        while index <= num:
            output['material'].append({"size": f"beam size {index}", "qty": f"{index}"})
            index += 1

        return output


def get_bom_ref_data(ID):
    bom: BomResult = BomResult.query.filter_by(id=ID).first_or_404()

    output = {"job number": bom.job_number,
              "material": [],
              "total": 0,
              "massage": f"Found data for ID {ID}",
              "data id": ID}

    for material in bom.material_review():
        for length in bom.required_lengths(material):
            output["material"].append({"size": f"{material} x {length}",
                                       "qty": bom.required_length_qty(material, length)})

    output["total"] = len(output["material"])

    if bom.has_missing_parts():
        output['massage'] = output['massage'] + \
                            "\n\n*** WARNING ***\nThis data reports that \nthere is missing parts"

    return output


@api.app_errorhandler(404)
def page_not_found(e):
    result = jsonify({"error": "Resource not found"})
    result.status_code = 404
    return result


@api.route("/bom/<ref>", methods=['GET'])
def get_one_bom(ref):

    if ref.lower().startswith('t'):
        result = bom_api_test_function(ref)
    else:
        if not isInt(ref):
            return jsonify({"error": "BOM ID not found \nPlease check your input"}), 404

        result = get_bom_ref_data(int(ref))

    return jsonify(result)
