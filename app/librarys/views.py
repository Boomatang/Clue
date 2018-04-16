from flask import render_template, request, flash

from app.librarys import library


@library.route('/materials', methods=['POST', 'GET'])
def material_view():
    return render_template('materials/index.html')


@library.route('/material-edit', methods=['POST', 'GET'])
def material_edit():

    if request.method == 'POST':
        flash('Got Post')

        for item in request.values.items(multi=True):
            print(item)

    return render_template('materials/edit.html')
