import requests
from bs4 import BeautifulSoup as bs
import re


scihub_request = "https://sci-hub.ru/"


def main():
    urls_file = input("File with links or a link: ")
    destination_folder = input("Destination folder: ")

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
    with open(filename, "r", encoding="utf-8") as file:
        for line in file:
            urls.append(line.strip())

    return urls


def get_internal_url(url):
    # Getting response from the sci-hub
    response = requests.get(scihub_request + url).text

    # Getting a new url of a file
    soup = bs(response, "lxml")
    for button in soup.find_all("button"):
        internal_url = button.get("onclick").split("=", 1)[-1]
        internal_url = re.findall(r"\w.+e", internal_url)[0]

        if "sci-hub" not in internal_url:
            return scihub_request + internal_url

        return "https://" + internal_url

    return 0, "Sorry, but the article is not in the Sci-Hub databasse"


def download_to(url, path):
    # Getting file name
    filename = re.findall(r"\w+\d+.pdf", url)[0]
    path = path + filename

    article = requests.get(url).content

    with open(path, "wb") as file:
        file.write(article)

    return filename


if __name__ == "__main__":
    main()
