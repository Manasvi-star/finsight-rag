from fastapi import APIRouter

router = APIRouter(prefix="/health", tags=["Health"])

@router.get("")
def health_check():
    """
    Simple API health probe endpoint.
    """
    return {"status": "ok"}
