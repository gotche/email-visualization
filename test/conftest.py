import os
import shutil
import tempfile
import pytest


@pytest.fixture
def messages_directory():
    return os.path.join(
        os.path.dirname(__file__),
        'messages_directory')


@pytest.fixture(scope='module')
def output_directory(request):
    directory = tempfile.mkdtemp()

    def fin():
        shutil.rmtree(directory)
    request.addfinalizer(fin)

    return directory


@pytest.fixture
def email_file():
    return os.path.join(
        os.path.dirname(__file__),
        'messages_directory',
        '20150426-100141-140328102776560.log')


@pytest.fixture
def email_id():
    return '20150426100141'
