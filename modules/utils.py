
def extract_url(url: str) -> dict[str, str]:
    """
    Парсер данных по обычным URL адресам
    :param url: Адрес сайта
    :return: JSON объект с собранными данными
    """

    parts = url.split("/")
    host_part = parts[2] if len(parts) > 2 else ""

    host = host_part.split("?")[0]

    path_parts = parts[3:] if len(parts) > 3 else []
    path = "/" + "/".join(path_parts) if path_parts else "/"

    if "?" in host_part:
        path += "?" + host_part.split("?")[1]

    return {
        "protocol": parts[0].replace(":", ""),
        "host": host,
        "path": path
    }

