class OcrUnavailableError(RuntimeError): pass
def extract_text(_: bytes, content_type: str) -> str:
    """OCR provider hook. Production must configure a secure, approved OCR service."""
    raise OcrUnavailableError(f"OCR is not configured for {content_type}; document remains available without extracted text.")
