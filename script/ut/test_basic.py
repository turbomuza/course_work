import pytest
from unittest.mock import patch, Mock
from script.main import save_photo, hide_controls, send_telegram_message, TOKEN, bot_user_id


@pytest.fixture(scope='module', autouse=True)
def mock_env_vars():
    with patch.dict('os.environ', {
        'TG_ALERT_TOKEN': 'test_token',
        'BOT_USER_ID': '123456'
    }):
        yield


@pytest.fixture
def mock_requests_post(mocker):
    return mocker.patch('requests.post')


@pytest.fixture
def mock_webdriver(mocker):
    return mocker.patch('selenium.webdriver.Chrome')


@pytest.fixture
def mock_webdriver_wait(mocker):
    return mocker.patch('selenium.webdriver.support.ui.WebDriverWait')


@pytest.fixture
def mock_time_sleep(mocker):
    return mocker.patch('time.sleep')


@pytest.fixture
def mock_os_makedirs(mocker):
    return mocker.patch('os.makedirs')


@pytest.fixture
def mock_open(mocker):
    return mocker.patch('builtins.open', mocker.mock_open())


def test_send_telegram_message(mock_requests_post):
    mock_requests_post.return_value.status_code = 200
    message = "Test message"

    send_telegram_message(message)

    mock_requests_post.assert_called_once_with(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        params={"chat_id": bot_user_id, "text": message}
    )


def test_save_photo(mock_webdriver, mock_webdriver_wait, mock_time_sleep, mock_os_makedirs, mock_open):
    mock_browser = Mock()
    mock_webdriver.return_value = mock_browser

    mock_wait = Mock()
    mock_wait.until.return_value = True
    mock_webdriver_wait.return_value = mock_wait

    mock_browser.find_element.return_value = Mock()

    save_photo("http://example.com", 1)

    mock_browser.get.assert_called_once_with("http://example.com")
    mock_browser.quit.assert_called_once()

    mock_os_makedirs.assert_called_once_with('/tm_dataset/photos_1', exist_ok=True)
    mock_open.assert_called()

    hide_controls(mock_browser)

    assert mock_browser.find_element.assert_called()
    assert mock_browser.execute_script.assert_called()
