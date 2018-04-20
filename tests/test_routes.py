import pytest
from flask import url_for

paths = ['main.index', 'user.dashboard', 'cutlist.bom_start',
         'BOM.BOM_upload', 'tools.bar_spacer', 'library.material_library']


@pytest.mark.single_thread
@pytest.mark.parametrize('path', paths)
def test_main_nav_paths(client, path):

    assert client.get(url_for(path)).status_code == 200
