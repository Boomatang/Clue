from flask import flash, redirect, url_for, render_template

from app.smart import BarSpacingCalculator, louver_efficiency
from app.tools import tools
from app.tools.forms import BarSpacer, LouverCalculatorForm
from app.utils import isFloat


@tools.route("/bar-spacer", methods=["POST", "GET"])
def bar_spacer():
    form = BarSpacer()
    bar = None

    if form.is_submitted():
        between_post = form.post_to_post.data
        gap = form.spacing.data
        size = form.bar_size.data

        all = [between_post, gap, size]

        for a in all:
            if isFloat(a):
                pass
            else:
                flash("All you're input needs to be a number.", "error")
                return redirect(url_for(".bar_spacer"))

        bar = BarSpacingCalculator(float(gap), float(between_post), float(size))
        return render_template("utls/bar-spacer.html", form=form, bar=bar)

    return render_template("utls/bar-spacer.html", form=form, bar=bar)


@tools.route("/louver-calculator", methods=["POST", "GET"])
def louver_calculator():

    mesh30 = ""
    mesh70 = ""
    form = LouverCalculatorForm()

    if form.validate_on_submit():

        width = form.width.data
        height = form.height.data

        all = [width, height]

        for a in all:
            if isFloat(a):
                pass
            else:
                flash("All you're input needs to be a number.", "error")
                return redirect(url_for("tools.louver_calculator"))

        mesh30 = louver_efficiency(float(width), float(height), 0.3)
        mesh70 = louver_efficiency(float(width), float(height), 0.7)
        return render_template(
            "utls/louver-calculator.html", mesh30=mesh30, mesh70=mesh70, form=form
        )

    return render_template(
        "utls/louver-calculator.html", mesh30=mesh30, mesh70=mesh70, form=form
    )
