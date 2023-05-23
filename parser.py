import concurrent.futures
import math
import os
import threading
from time import sleep

import requests
from selenium import webdriver
from selenium.webdriver.common.by import By

thread_local = threading.local()


def GetProxyList(proxy_file):
    proxy_list = []
    try:
        with open(proxy_file, 'r') as f:
            content = f.read().split('\n')[:-1]
            for proxy in content:
                proxy_list.append(proxy.split(':'))
    except Exception:
        print("Что-то не так с файлом с прокси")

    return proxy_list


def ParseGooglePhotos(cookie_file, screen_dir, user_folder, proxy):
    options = webdriver.FirefoxOptions()
    options.set_preference('network.proxy.type', 1)
    options.set_preference('network.proxy.socks', proxy[0])
    options.set_preference('network.proxy.socks_port', proxy[1])
    options.set_preference("network.proxy.socks_version", 5)
    options.set_preference("network.proxy.socks_username", proxy[2])
    options.set_preference("network.proxy.socks_password", proxy[3])
    driver = webdriver.Firefox(options=options)

    photo_number = 1
    try:
        driver.install_addon('cookie_quick_manager.xpi', temporary=True)

        driver.get('about:debugging#/runtime/this-firefox')
        sleep(2)
        cookie_manager_id = driver.find_element('xpath',
                                                '/html/body/div/div/main/article/section[1]/div/ul/li/section[1]/dl/div[3]/dd')
        driver.get(f'moz-extension://{cookie_manager_id.text}/cookies.html?parent_url=#')

        file_input = driver.find_element('xpath', '//*[@id="file_elem"]')
        file_input.send_keys(os.path.normpath(cookie_file))
        sleep(1)

        driver.get('https://accounts.google.com/SignOutOptions?hl=en&continue=https://www.google.com/')
        sleep(1)
        valid_accounts_number = len(driver.find_elements(By.CLASS_NAME, 'account-email'))
        user_number = 0
        user_folder_path = os.path.normpath(os.path.join(screen_dir, user_folder))
        os.mkdir(user_folder_path)
        while True:
            if user_number > valid_accounts_number - 1:
                break
            if user_number == 0:
                current_screen_url = 'https://photos.google.com/search/Скриншоты'
            else:
                current_screen_url = f'https://photos.google.com/u/1/search/Скриншоты?pli=1&authuser={user_number}&pageId=none'
            user_number = user_number + 1

            driver.get(current_screen_url)
            sleep(3)

            # Close banners
            try:
                banner_button = driver.find_element('xpath',
                                                    '/html/body/div[1]/div/div[2]/div/div[2]/span/div/button')
                banner_button.click()
            except Exception:
                pass

            try:
                banner_button = driver.find_element('xpath',
                                                    '/html/body/div[1]/div/div[2]/div/div[2]/div[2]/button[2]')
                banner_button.click()
            except Exception:
                pass

            try:
                screenshot_element = driver.find_element(By.CLASS_NAME, 'RY3tic')
                screenshot_element.click()
            except Exception:
                continue

            prev_url = None
            current_url = driver.current_url

            sleep(3)
            while True:
                sleep(2)
                screenshot_element = driver.find_element('xpath',
                                                         '/html/body/div[1]/div/c-wiz/div[4]/c-wiz[2]/div[1]/c-wiz[3]/div[2]/c-wiz[1]/div[2]/div/div/img')
                url = screenshot_element.get_attribute('src')
                response = requests.get(url)
                if response.status_code == 200:
                    with open(os.path.normpath(os.path.join(user_folder_path, f"{photo_number}.jpg")),
                              'wb') as file:
                        file.write(response.content)
                photo_number = photo_number + 1
                try:
                    next_button = driver.find_element('xpath',
                                                      '/html/body/div[1]/div/c-wiz/div[4]/c-wiz[2]/div[1]/c-wiz[3]/div[2]/div[2]')
                    driver.execute_script("arguments[0].click();", next_button)
                except Exception:
                    break
                prev_url = current_url
                current_url = driver.current_url
                if current_url == prev_url:
                    break

    except Exception:
        driver.close()
    driver.close()


def ParallelExecute(max_workers, screen_dir, user_list, cookies_list, proxy_list_):
    proxy_list = proxy_list_ * (math.trunc(len(cookies_list) / len(proxy_list_)) + 1)
    proxy_list = proxy_list[:len(cookies_list)]
    screen_dir_list = [screen_dir] * len(cookies_list)
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        executor.map(ParseGooglePhotos, cookies_list, screen_dir_list, user_list, proxy_list)


def GetCookiesList(cookies_dir):
    cookies_list = []
    user_list = []
    for dir in os.listdir(cookies_dir):
        user_cookies = []
        max_size = 0
        max_path = None
        for file in os.listdir(os.path.join(cookies_dir, os.path.join(dir, 'Cookies'))):
            file_path = os.path.normpath(os.path.join(os.path.join(cookies_dir, os.path.join(dir, 'Cookies'), file)))
            if os.path.getsize(file_path) > max_size:
                max_size = os.path.getsize(file_path)
                max_path = file_path
        cookies_list.append(max_path)
        user_list.append(dir)
        cookies_list.append(user_cookies)
    return cookies_list, user_list
