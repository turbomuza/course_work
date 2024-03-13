import pytest
from unittest.mock import patch


@pytest.fixture(scope='module', autouse=True)
def mock_env_vars():
    with patch.dict('os.environ', {
        'TG_ALERT_TOKEN': 'test_token',
        'BOT_USER_ID': '123456'
    }):
        yield
