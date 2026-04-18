import io

import pdfplumber
from docx import Document
from fastapi import status

from utils.errors import APIError


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract text from all pages of a PDF file."""
    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            if not pdf.pages:
                raise APIError(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    code="PARSE_FAILED",
                    message="The PDF file has no pages.",
                )

            extracted_pages: list[str] = []
            for page in pdf.pages:
                # Image-only pages return None, which helps us detect scanned PDFs.
                page_text = page.extract_text()
                extracted_pages.append(page_text.strip() if page_text else "")

            full_text = "\n".join(extracted_pages).strip()
            if not full_text:
                raise APIError(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    code="PARSE_FAILED",
                    message=(
                        "No extractable text found in the PDF. "
                        "It may be a scanned image-only document. "
                        "Please upload a text-based PDF."
                    ),
                )

            return full_text
    except APIError:
        raise
    except Exception as exc:
        raise APIError(
            status_code=status.HTTP_400_BAD_REQUEST,
            code="PARSE_FAILED",
            message=f"Failed to parse PDF. The file may be corrupted or unreadable: {exc}",
        ) from exc


def extract_text_from_docx(file_bytes: bytes) -> str:
    """Extract text from all paragraphs of a DOCX file."""
    try:
        document = Document(io.BytesIO(file_bytes))
        lines: list[str] = [paragraph.text for paragraph in document.paragraphs]
        full_text = "\n".join(lines).strip()

        if not full_text:
            raise APIError(
                status_code=status.HTTP_400_BAD_REQUEST,
                code="PARSE_FAILED",
                message="The DOCX file appears to be empty or contains no readable text.",
            )

        return full_text
    except APIError:
        raise
    except Exception as exc:
        raise APIError(
            status_code=status.HTTP_400_BAD_REQUEST,
            code="PARSE_FAILED",
            message=f"Failed to parse DOCX. The file may be corrupted or unreadable: {exc}",
        ) from exc
