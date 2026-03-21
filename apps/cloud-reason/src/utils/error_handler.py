class APIError(Exception):
    pass

class YandexGPTError(APIError):
    pass

class ValidationError(APIError):
    pass

