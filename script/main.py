import time
import json
import os
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import concurrent.futures
import telegram

TOKEN = os.environ["TG_ALERT_TOKEN"]
bot_user_id = int(os.environ["BOT_USER_ID"])
bot = telegram.Bot(token=TOKEN)


def send_telegram_message(message, delay_seconds=3):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    params = {"chat_id": bot_user_id, "text": message}
    response = requests.post(url, params=params)
    time.sleep(delay_seconds)
    if response.status_code != 200:
        print(f"Ошибка при отправке сообщения: {response.text}")


def hide_controls(browser):
    browser.execute_script("""
    var top_controls = document.querySelector('.ytp-chrome-top');
    if (top_controls) {
        top_controls.style.display = 'none';
    }
    var bottom_controls = document.querySelector('.ytp-chrome-bottom');
    if (bottom_controls) {
        bottom_controls.style.display = 'none';
    }
    """)


def save_photo(url: str, thread: int):
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('hide-scrollbars')
    browser = webdriver.Chrome(options=options)
    browser.get(url)

    try:
        WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'html5-main-video')))
        send_telegram_message("Видео загружено, начинаем скриншоты.")
        print("Видео загружено, начинаем скриншоты.")
    except Exception as e:
        send_telegram_message(f"Произошла ошибка при ожидании видео: {e}")
        print(f"Произошла ошибка при ожидании видео: {e}")
        browser.quit()
        return

    try:
        play_button = browser.find_element(By.CLASS_NAME, 'ytp-play-button')
        play_button.click()
        send_telegram_message("Нажата кнопка воспроизведения.")
        print("Нажата кнопка воспроизведения.")
    except Exception as e:
        send_telegram_message(f"Произошла ошибка при нажатии кнопки воспроизведения: {e}")
        print(f"Произошла ошибка при нажатии кнопки воспроизведения: {e}")
        browser.quit()
        return

    time.sleep(6)

    hide_controls(browser)

    print(f"Ссылка / поток #{thread} готова к выполнению скриншотов\n.")

    base_dir = os.path.join(os.sep, 'tm_dataset', f'photos_{thread}')
    os.makedirs(base_dir, exist_ok=True)

    counter = 0
    while counter < 1441:
        timestamp = time.strftime("%Y-%m-%d_%H-%M")
        screenshot = browser.find_element(By.CLASS_NAME, 'html5-main-video').screenshot_as_png
        with open(os.path.join(base_dir, f'screen_{timestamp}.png'), 'wb') as file:
            file.write(screenshot)
        send_telegram_message(f"Ссылка / поток #{thread} сделал скриншот в {timestamp} успешно")
        print(f"Ссылка / поток #{thread} сделал скриншот в {timestamp} успешно")

        counter += 1
        time.sleep(60)

    browser.quit()


if __name__ == "__main__":
    with open("config.json", "r") as f:
        config = json.load(f)

    urls = config["urls"]
    thread_count = len(urls)

    with concurrent.futures.ThreadPoolExecutor(max_workers=thread_count) as executor:
        futures = {executor.submit(save_photo, url, i + 1): url for i, url in enumerate(urls)}

        for future in concurrent.futures.as_completed(futures):
            url = futures[future]
            try:
                future.result()
            except Exception as exc:
                send_telegram_message(f"При выполнении потока {url} произошла ошибка: {exc}")
                print(f"При выполнении потока {url} произошла ошибка: {exc}")
