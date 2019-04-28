import os

from flask import flash, redirect, url_for, session, render_template, request
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from app import db
from app.BOM import BOM
from app.BOM.forms import BOMUpload
from app.decorators import company_asset
from app.models import (
    BomFile,
    MaterialSize,
    MaterialLength,
    BomSession,
    BomSessionSize,
    BomResult,
    BomResultMaterial,
    BomResultBeam,
    BomResultBeamPart,
    BomResultMissingPart,
    BomSessionLength,
    Project,
)
from app.smart import RawBomFile, CreateBom, fix_csv_file
from app.utils import file_ext_checker, key_preferred, key_checkboxes, is_number


@BOM.route("/BOM/upload", methods=["POST", "GET"])
def BOM_upload():
    form = BOMUpload(current_user.company.id)

    if form.is_submitted():
        f = form.file_name.data
        filename = secure_filename(f.filename)

        name = os.path.join(
            os.environ.get("CLUE_UPLOADS", "/home/boomatang/Public"), filename
        )

        if not file_ext_checker(str(name), ".csv"):
            flash("File type was not a CSV file type.", "Error")
            return redirect(url_for(".BOM_upload"))

        f.save(name)
        fix_csv_file(name)
        d = RawBomFile(name)

        entry = d.return_entry()
        entry.comment = form.comment.data

        entry.project_id = form.projects.data

        session["job_number"] = form.job_number.data

        print(form.projects.data)

        db.session.add(entry)
        db.session.commit()
        entry.configure_file()

        session["file"] = entry.id

        return redirect(url_for(".BOM_setup"))

    return render_template("BOM/upload.html", form=form)


@BOM.route("/BOM/setup", methods=["POST", "GET"])
def BOM_setup():

    bom = BomFile.query.filter_by(id=session["file"]).first()

    materials = bom.materials_required()
    materials_used = []

    for material in materials:
        item = MaterialSize.query.filter_by(
            size=material, company=current_user.company.id
        ).first()
        if item is not None:
            materials_used.append(item)
        else:
            session["material_missing"] = material
            return redirect(url_for("library.material_missing"))

    if request.method == "POST":
        values = []

        # create a session object
        # passer keys
        # key values to session object
        """
        dict = {material: size,
                lengths: [ints],
                default: int}
        """
        for material in materials:
            value = {"material": material, "lengths": []}
            for item in request.values.items(multi=True):
                if item[0].startswith(material):

                    if key_preferred(item[0]):
                        preferred_length = MaterialLength.query.filter_by(
                            id=int(item[1])
                        ).first()
                        value["default"] = preferred_length.length

                    if key_checkboxes(item[0]):
                        length = MaterialLength.query.filter_by(id=int(item[1])).first()
                        value["lengths"].append(length.length)
            values.append(value)

        entry = BomSession()

        db.session.add(entry)
        db.session.commit()
        for value in values:

            beams = BomSessionSize(size=value["material"], default=value["default"])
            entry.sizes.append(beams)
            db.session.add(beams)
            db.session.commit()
            for length in value.get("lengths", None):
                if length is not None:
                    beam = BomSessionLength(length=length)
                    beams.lengths.append(beam)

        db.session.commit()

        session["session_id"] = entry.id

        return redirect(url_for(".BOM_calculate"))

    return render_template("BOM/setup.html", materials=materials_used)


@BOM.route("/BOM/calculate")
def BOM_calculate():

    setup_id = session["session_id"]
    data_id = session["file"]

    b_o_m = CreateBom(setup_id, data_id)
    b_o_m.run()

    result = b_o_m.create_result()

    return redirect(url_for(".BOM_result", asset=result.asset))


@BOM.route("/BOM/result/<asset>", methods=["POST", "GET"])
@login_required
@company_asset()
def BOM_result(asset):
    result: BomResult = BomResult.query.filter_by(asset=asset).first_or_404()

    session["file"] = result.file_id
    # lengths = [6100, 7500, 12000]
    lengths = result.lengths

    lengths.sort()

    return render_template("BOM/results.html", result=result, lengths=lengths)


@BOM.route("/BOM/results/remove/<asset>", methods=["GET"])
@login_required
@company_asset()
def BOM_remove_result(asset):
    result: BomResult = BomResult.query.filter_by(asset=asset).first_or_404()
    massage = f"Your about to remove result {result.job_number}: {result.comment}"
    session["check"] = result.asset

    return render_template("user/yes_no.html", massage=massage, asset=result.asset)


@BOM.route("/BOM/results/remove/<asset>/agree", methods=["get"])
@login_required
@company_asset()
def BOM_remove_result_agree(asset):
    result: BomResult = BomResult.query.filter_by(asset=asset).first_or_404()
    if result.asset != session["check"]:
        flash("Unkown action")
        return redirect(url_for("user.dashboard"))
    job = result.job_number

    result.delete()
    db.session.commit()

    flash(f"BOM with job number {job} has been removed from the system")
    return redirect(url_for("user.dashboard"))


@BOM.route("/BOM/results/remove/<asset>/disagree", methods=["get"])
@login_required
@company_asset()
def BOM_remove_result_disagree(asset):
    result: BomResult = BomResult.query.filter_by(asset=asset).first_or_404()
    if result.asset != session["check"]:
        flash("Unkown action")
        return redirect(url_for("user.dashboard"))
    job = result.job_number

    flash(f"BOM with job number {job} has not been removed from the system")
    return redirect(url_for("user.dashboard"))
