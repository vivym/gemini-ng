from functools import wraps

from googleapiclient.errors import HttpError


class ResourceNotFound(Exception):
    def __init__(self, inner_exception: HttpError):
        super().__init__(f"Resource not found: {inner_exception}")

        self.inner_exception = inner_exception


class AccessDenied(Exception):
    def __init__(self, inner_exception: HttpError):
        super().__init__(f"Access denied: {inner_exception}")

        self.inner_exception = inner_exception


class RateLimitExceeded(Exception):
    def __init__(self, inner_exception: HttpError):
        super().__init__(f"Rate limit exceeded: {inner_exception}")

        self.inner_exception = inner_exception


class InternalServerError(Exception):
    def __init__(self, inner_exception: HttpError):
        super().__init__(f"Internal server error: {inner_exception}")

        self.inner_exception = inner_exception


def handle_http_exception(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except HttpError as e:
            if e.resp.status == 404:
                raise ResourceNotFound(e)
            elif e.resp.status == 403:
                raise AccessDenied(e)
            elif e.resp.status == 429:
                raise RateLimitExceeded(e)
            elif e.resp.status == 500:
                raise InternalServerError(e)
            else:
                raise e

    return wrapper
