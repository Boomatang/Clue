from flask import render_template

from app.models import BomResult
from app.user import user


@user.route('/dashboard', methods=['POST', 'GET'])
def dashboard():

    BOM_results = BomResult.query.order_by(BomResult.timestamp).all()
    temp = []
    for r in BOM_results:
        temp.append(r)

    BOM_results = temp.reverse()
    return render_template('user/dashboard.html', BOM_results=temp)
