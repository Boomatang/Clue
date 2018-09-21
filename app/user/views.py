from flask import render_template, request, current_app

from app.models import BomResult, Project
from app.user import user


@user.route('/dashboard', methods=['POST', 'GET'])
def dashboard():

    page = request.args.get('page', 1, type=int)
    pagination = BomResult.query.order_by(
            BomResult.timestamp.desc()).paginate(page,
                                                 per_page=current_app.config['POSTS_PER_PAGE'],
                                                 error_out=False)
    temp = pagination.items

    projects = Project.query.order_by(Project.last_active.desc())[:5]

    return render_template('user/dashboard.html', BOM_results=temp, pagination=pagination, projects=projects)
