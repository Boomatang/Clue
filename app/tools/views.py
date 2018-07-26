from flask import flash, redirect, url_for, render_template

from app.smart import BarSpacingCalculator
from app.tools import tools
from app.tools.forms import BarSpacer
from app.utils import isFloat


@tools.route('/bar-spacer', methods=['POST', 'GET'])
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
                flash('All you\'re input needs to be a number.', 'error')
                return redirect(url_for('.bar_spacer'))

        bar = BarSpacingCalculator(float(gap), float(between_post), float(size))
        return render_template('utls/bar-spacer.html', form=form, bar=bar)

    return render_template('utls/bar-spacer.html', form=form, bar=bar)
