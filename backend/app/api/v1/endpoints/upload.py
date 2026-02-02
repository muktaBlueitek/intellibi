from typing import Dict, Any
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.api.v1.deps import get_current_active_user
from app.services.file_upload import FileUploadService

router = APIRouter()
file_upload_service = FileUploadService()


@router.post("/preview", response_model=Dict[str, Any])
async def preview_file(
    file: UploadFile = File(...),
    clean_data: bool = True,
    preview_rows: int = 10,
    current_user: User = Depends(get_current_active_user)
):
    """Preview uploaded file without saving it."""
    try:
        result = await file_upload_service.process_upload(
            file=file,
            user_id=current_user.id,
            clean=clean_data,
            preview_rows=preview_rows
        )
        
        # Clean up the file after preview
        import os
        if os.path.exists(result["file_info"]["file_path"]):
            os.remove(result["file_info"]["file_path"])
        
        return {
            "metadata": result["metadata"],
            "preview": result["preview"],
            "file_info": {
                "file_name": result["file_info"]["file_name"],
                "file_size": result["file_info"]["file_size"],
                "file_type": result["file_info"]["file_type"]
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
