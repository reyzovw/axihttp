
def extract_url(url: str) -> dict[str, str]:
    """
    Парсер данных по обычным URL адресам
    :param url: Адрес сайта
    :return: JSON объект с собранными данными
    """

    parts = url.split("/")

    return {
        "protocol": parts[0].replace(":", ""),
        "host": parts[2],
        "path": "/" + "/".join(parts[3:])
    }


