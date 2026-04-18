from fastapi.responses import JSONResponse


class APIError(Exception):
    """Application error with a stable response code."""

    def __init__(self, status_code: int, code: str, message: str) -> None:
        self.status_code = status_code
        self.code = code
        self.message = message
        super().__init__(message)


def build_error_response(status_code: int, code: str, message: str) -> JSONResponse:
    """Build the standard API error response payload."""
    return JSONResponse(
        status_code=status_code,
        content={
            "error": True,
            "message": message,
            "code": code,
        },
    )
