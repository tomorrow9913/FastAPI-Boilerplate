# -*- coding: utf-8 -*-
# src/core/exceptions.py
# Custom exceptions for the application


class AppException(Exception):
    def __init__(self, detail: str):
        self.detail = detail
        super().__init__(detail)


class NotFoundException(AppException):
    pass


class DuplicateError(AppException):
    pass


class InvalidOperationError(AppException):
    pass
