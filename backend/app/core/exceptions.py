from typing import Optional, Dict, Any

class ErrorCode:
    BAD_REQUEST = "BAD_REQUEST"
    AUTHENTICATION_FAILED = "AUTHENTICATION_FAILED"
    AUTHORIZATION_FAILED = "AUTHORIZATION_FAILED"
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    DATABASE_ERROR = "DATABASE_ERROR"
    AI_SERVICE_ERROR = "AI_SERVICE_ERROR"
    DOCUMENT_PROCESSING_ERROR = "DOCUMENT_PROCESSING_ERROR"
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"

class AppException(Exception):
    """
    Base application exception for handled domain errors.
    """
    def __init__(
        self,
        status_code: int = 400,
        error_code: str = ErrorCode.BAD_REQUEST,
        message: str = "An application error occurred.",
        details: Optional[Any] = None,
        headers: Optional[Dict[str, str]] = None
    ):
        self.status_code = status_code
        self.error_code = error_code
        self.message = message
        self.details = details
        self.headers = headers
        super().__init__(message)

class DatabaseException(AppException):
    def __init__(self, message: str = "Unable to complete database operation right now.", details: Optional[Any] = None):
        super().__init__(
            status_code=500,
            error_code=ErrorCode.DATABASE_ERROR,
            message=message,
            details=details
        )

class AIServiceException(AppException):
    def __init__(self, message: str = "AI service is temporarily unavailable. Please try again.", status_code: int = 503, details: Optional[Any] = None):
        super().__init__(
            status_code=status_code,
            error_code=ErrorCode.AI_SERVICE_ERROR,
            message=message,
            details=details
        )

class DocumentProcessingException(AppException):
    def __init__(self, message: str = "Unable to process the uploaded document.", status_code: int = 400, details: Optional[Any] = None):
        super().__init__(
            status_code=status_code,
            error_code=ErrorCode.DOCUMENT_PROCESSING_ERROR,
            message=message,
            details=details
        )
