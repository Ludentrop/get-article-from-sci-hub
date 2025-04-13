import requests
from bs4 import BeautifulSoup as bs
import re
import os


scihub_request = "https://sci-hub.ru/"


def main():
    urls_file = input("File with links or a link: ").strip()
    destination_folder = input("Destination folder: ").strip()

    # Проверка и нормализация пути сохранения
    if not destination_folder.endswith(os.sep):
        destination_folder += os.sep  # Добавляем разделитель, если его нет

    # Проверяем, существует ли указанная директория
    if not os.path.exists(destination_folder):
        print(f"Error: The directory '{destination_folder}' does not exist.")
        return

    if urls_file[-3:] == "txt":
        articles = get_urls_from_file(urls_file)
        urls = {}

        for article in articles:
            urls[article] = get_internal_url(article)

        for internal_url in urls.values():
            if isinstance(internal_url, str):
                filename = download_to(internal_url, destination_folder).split(".")[0]
                print(f'"{filename}" has been downloaded')
            else:
                print(internal_url[1])
    else:
        internal_url = get_internal_url(urls_file)
        if isinstance(internal_url, str):
            filename = download_to(internal_url, destination_folder).split(".")[0]
            print(f'"{filename}" has been downloaded')
        else:
            print(internal_url[1])


def get_urls_from_file(filename):
    urls = []
    try:
        with open(filename, "r", encoding="utf-8") as file:
            for line in file:
                urls.append(line.strip())
    except FileNotFoundError:
        print(f"Error: The file '{filename}' was not found.")
        return []
    except Exception as e:
        print(f"Error reading the file: {e}")
        return []

    return urls


def get_internal_url(url):
    try:
        # Получаем ответ от Sci-Hub
        response = requests.get(scihub_request + url).text

        # Парсим HTML для получения внутренней ссылки
        soup = bs(response, "lxml")
        for button in soup.find_all("button"):
            onclick = button.get("onclick")
            if onclick:
                internal_url = onclick.split("=", 1)[-1]
                internal_url = re.findall(r"\w.+e", internal_url)[0]

                if "sci-hub" not in internal_url:
                    return scihub_request + internal_url
                return "https://" + internal_url

        return 0, "Sorry, but the article is not in the Sci-Hub database."
    except Exception as e:
        return 0, f"Error fetching the article: {e}"


def download_to(url, path):
    try:
        # Получаем имя файла из URL
        filename = re.findall(r"\w+\d+.pdf", url)[0]
        full_path = os.path.join(path, filename)  # Используем os.path.join для кроссплатформенности

        # Скачиваем файл
        article = requests.get(url).content
        with open(full_path, "wb") as file:
            file.write(article)

        return filename
    except Exception as e:
        print(f"Error downloading the file: {e}")
        return None


if __name__ == "__main__":
    main()
    
