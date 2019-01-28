import pytest
from flask import url_for

from tests.conftest import login_standard_user

paths = ['main.index', 'user.dashboard', 'cutlist.bom_start',
         'BOM.BOM_upload', 'tools.bar_spacer', 'library.material_library',
         'library.material_add', 'library.material_classes', 'cert.index',
         'project.index', 'project.add']


@pytest.mark.single_thread
@pytest.mark.parametrize('path', paths)
def test_main_nav_paths(client, path):
    login_standard_user(client)
    assert client.get(url_for(path)).status_code == 200
