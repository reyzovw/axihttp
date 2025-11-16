
class AxiHTTPException(Exception):
    """Базовый класс для всех AxiHttp исключений"""
    pass

class JsonNotFoundError(AxiHTTPException):
    """Исключение говорит о том, что вы не можете использовать <Response>.json() ведь ответ не содержит валидный Json"""
    def __init__(self, content_type: str, original_exception: Exception = None):
        message = f"Cannot parse JSON. Content-Type: {content_type}"
        super().__init__(message, original_exception)
        self.content_type = content_type


class SocketEstablishedError(AxiHTTPException):
    """Исключение говорит о том, что сайт не может установить с вами соединение"""
    def __init__(self):
        message = f"Cannot established socket connection"
        super().__init__(message)


