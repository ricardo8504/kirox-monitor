from typing import Any


class AppError(Exception):
    def __init__(self, message: str, code: str, details: Any = None) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details


class NotFoundError(AppError):
    def __init__(self, resource: str, resource_id: Any = None) -> None:
        if resource_id:
            details: dict = {"resource": resource, "id": str(resource_id)}
        else:
            details = {"resource": resource}
        super().__init__(f"{resource} not found", "NOT_FOUND", details)


class UnauthorizedError(AppError):
    def __init__(self, message: str = "Unauthorized") -> None:
        super().__init__(message, "UNAUTHORIZED")


class ForbiddenError(AppError):
    def __init__(self, message: str = "Forbidden") -> None:
        super().__init__(message, "FORBIDDEN")


class ConflictError(AppError):
    def __init__(self, message: str, details: Any = None) -> None:
        super().__init__(message, "CONFLICT", details)


class ValidationError(AppError):
    def __init__(self, message: str, details: Any = None) -> None:
        super().__init__(message, "VALIDATION_ERROR", details)


class ExternalServiceError(AppError):
    def __init__(self, service: str, message: str) -> None:
        super().__init__(f"{service}: {message}", "EXTERNAL_SERVICE_ERROR", {"service": service})
