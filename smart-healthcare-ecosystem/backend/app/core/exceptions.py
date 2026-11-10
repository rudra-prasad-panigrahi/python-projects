from fastapi import HTTPException, status

def not_found(resource: str) -> HTTPException:
    return HTTPException(status.HTTP_404_NOT_FOUND, f"{resource} was not found")

def forbidden(detail: str = "You do not have access to this personal health data") -> HTTPException:
    return HTTPException(status.HTTP_403_FORBIDDEN, detail)
