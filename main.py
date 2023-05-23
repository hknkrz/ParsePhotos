import os

from parser import GetCookiesList, GetProxyList, ParallelExecute


def ReadUserData():
    while True:
        try:
            max_workers = int(input("Введите количество потоков "))
            if max_workers > 0:
                break
            else:
                print("Число должно быть строго больше нуля")

        except ValueError as e:
            print("Некорректный ввод:", e)

    while True:
        try:
            cookies_dir = input("Укажите директорию с логами ")
            if not os.path.isdir(cookies_dir):
                print("Некорректный путь, попробуйте еще раз")
            else:
                break

        except ValueError as e:
            print("Некорректный ввод:", e)

    while True:
        try:
            screen_dir = input("Укажите директорию, в которую хотите сохранить фото ")
            if not os.path.isdir(cookies_dir):
                print("Некорректный путь, попробуйте еще раз")
            else:
                break

        except ValueError as e:
            print("Некорректный ввод:", e)

    while True:
        try:
            proxies_file = input("Укажите путь к файлу с прокси ")
            if not os.path.isfile(proxies_file):
                print("Некорректный путь, попробуйте еще раз")
            else:
                break

        except ValueError as e:
            print("Некорректный ввод:", e)

    return max_workers, cookies_dir, screen_dir, proxies_file


if __name__ == "__main__":
    max_workers, cookies_dir, screen_dir, proxies_file = ReadUserData()
    cookies_list, user_list = GetCookiesList(cookies_dir)
    proxy_list = GetProxyList(proxies_file)

    ParallelExecute(max_workers, screen_dir, user_list, cookies_list, proxy_list)
