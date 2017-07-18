import os
import re
import shutil
import tempfile
from contextlib import closing
from unittest import mock

import pytest

from rpmlb.work import Work


def test_init():
    work = None
    mock_recipe = mock.MagicMock()
    mock_recipe.num_of_package.return_value = 2
    try:
        work = Work(mock_recipe)
        assert work
    finally:
        working_dir = work.working_dir
        assert working_dir
        assert re.findall(r'/tmp/', working_dir)
        if os.path.isdir(working_dir):
            shutil.rmtree(working_dir)


def test_init_work_directory():
    work = None
    arg_working_dir = None
    mock_recipe = mock.MagicMock()
    mock_recipe.num_of_package.return_value = 2
    try:
        arg_working_dir = tempfile.mkdtemp(prefix='rpmlb-test-')
        work = Work(mock_recipe, work_directory=arg_working_dir)
        assert work
    finally:
        working_dir = work.working_dir
        assert working_dir
        assert working_dir == arg_working_dir
        if os.path.isdir(working_dir):
            shutil.rmtree(working_dir)


def test_close():
    mock_recipe = mock.MagicMock()
    type(mock_recipe).num_of_package = mock.PropertyMock(return_value=2)
    work = Work(mock_recipe)
    assert work
    work.close()
    assert not os.path.isdir(work.working_dir)


def test_num_name_from_count():
    mock_recipe = mock.MagicMock()
    type(mock_recipe).num_of_package = mock.PropertyMock(return_value=11)

    with closing(Work(mock_recipe)) as work:
        assert work
        assert work.num_name_from_count(2) == '02'
        assert work.num_name_from_count(10) == '10'


def test_each_num_dir():
    mock_recipe = mock.MagicMock()
    type(mock_recipe).num_of_package = mock.PropertyMock(return_value=2)
    package_dicts = [
        {'name': 'a'},
        {'name': 'b'},
    ]
    mock_recipe.each_normalized_package.return_value = iter(package_dicts)

    with closing(Work(mock_recipe)) as work:
        assert work

        for package_dict, num_name in work.each_num_dir():
            assert package_dict
            assert num_name
            assert re.match('^[12]$', num_name)
            assert re.match('^.+/[12]$', os.getcwd())

        with pytest.helpers.pushd(work.working_dir):
            assert os.path.isdir('1')
            assert os.path.isdir('2')
