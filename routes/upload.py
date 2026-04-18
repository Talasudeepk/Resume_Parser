from pathlib import Path

from fastapi import APIRouter, File, UploadFile, status
from fastapi.responses import JSONResponse

from utils.errors import APIError
from utils.parser import parse_resume
from utils.text_extractor import extract_text_from_docx, extract_text_from_pdf

router = APIRouter(tags=["Upload"])

MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB
ALLOWED_EXTENSIONS = {".pdf", ".docx"}


def _validate_filename(filename: str | None) -> tuple[str, str]:
    """Return a safe filename and validated lowercase extension."""
    if not filename:
        raise APIError(
            status_code=status.HTTP_400_BAD_REQUEST,
            code="VALIDATION_ERROR",
            message="Uploaded file must include a filename.",
        )

    safe_name = Path(filename).name
    extension = Path(safe_name).suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise APIError(
            status_code=status.HTTP_400_BAD_REQUEST,
            code="UNSUPPORTED_TYPE",
            message="Only PDF and DOCX files are supported.",
        )

    return safe_name, extension


@router.post("/upload")
async def upload_resume(file: UploadFile = File(...)) -> JSONResponse:
    """Accept a resume upload, validate it, and return parsed resume data."""
    file_name, file_extension = _validate_filename(file.filename)

    try:
        file_bytes = await file.read()
    except Exception as exc:
        raise APIError(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            code="PARSE_FAILED",
            message=f"Unable to read uploaded file: {exc}",
        ) from exc
    finally:
        try:
            await file.close()
        except Exception:
            pass

    if not file_bytes:
        raise APIError(
            status_code=status.HTTP_400_BAD_REQUEST,
            code="VALIDATION_ERROR",
            message="Uploaded file is empty. Please provide a valid PDF or DOCX file.",
        )

    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        raise APIError(
            status_code=status.HTTP_400_BAD_REQUEST,
            code="FILE_TOO_LARGE",
            message="File too large. Max size is 10MB.",
        )

    if file_extension == ".pdf":
        raw_text = extract_text_from_pdf(file_bytes)
        file_type = "pdf"
    else:
        raw_text = extract_text_from_docx(file_bytes)
        file_type = "docx"

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "filename": file_name,
            "file_type": file_type,
            "parsed": parse_resume(raw_text),
        },
    )
