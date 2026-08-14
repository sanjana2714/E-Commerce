from typing import Any


class DomainException(Exception):
    def __init__(self, message: str, code: str = "BAD_REQUEST", status_code: int = 400, details: Any | None = None):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details
        super().__init__(message)

class ResourceNotFoundError(DomainException):
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message=message, code="NOT_FOUND", status_code=404)

class ValidationError(DomainException):
    def __init__(self, message: str = "Validation failed", details: Any | None = None):
        super().__init__(message=message, code="VALIDATION_ERROR", status_code=422, details=details)

class InsufficientInventoryError(DomainException):
    def __init__(self, message: str = "Insufficient inventory available"):
        super().__init__(message=message, code="INSUFFICIENT_INVENTORY", status_code=409)

class DuplicateRequestError(DomainException):
    def __init__(self, message: str = "Duplicate request detected"):
        super().__init__(message=message, code="DUPLICATE_REQUEST", status_code=409)

class UnauthorizedError(DomainException):
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(message=message, code="UNAUTHORIZED", status_code=401)

class ForbiddenError(DomainException):
    def __init__(self, message: str = "Permission denied"):
        super().__init__(message=message, code="FORBIDDEN", status_code=403)

class ExternalServiceError(DomainException):
    def __init__(self, message: str = "External service failure"):
        super().__init__(message=message, code="EXTERNAL_SERVICE_ERROR", status_code=502)

class EventProcessingError(DomainException):
    def __init__(self, message: str = "Failed to process event"):
        super().__init__(message=message, code="EVENT_PROCESSING_ERROR", status_code=500)
