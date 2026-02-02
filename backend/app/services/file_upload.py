import os
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, Tuple
from fastapi import UploadFile, HTTPException, status
from pathlib import Path

from app.core.config import settings


class FileUploadService:
    """Service for handling file uploads, parsing, and validation."""
    
    # Allowed file extensions
    ALLOWED_EXTENSIONS = {".csv", ".xlsx", ".xls"}
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    
    def __init__(self, upload_dir: str = "uploads"):
        """Initialize the file upload service."""
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
    
    def validate_file(self, file: UploadFile) -> Tuple[bool, Optional[str]]:
        """Validate uploaded file."""
        # Check file extension
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in self.ALLOWED_EXTENSIONS:
            return False, f"File type {file_ext} not allowed. Allowed types: {', '.join(self.ALLOWED_EXTENSIONS)}"
        
        # Check file size (we'll need to read it to check size)
        # For now, we'll check after reading
        return True, None
    
    async def save_file(self, file: UploadFile, user_id: int) -> Dict[str, Any]:
        """Save uploaded file and return file metadata."""
        # Validate file
        is_valid, error = self.validate_file(file)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error
            )
        
        # Create user-specific directory
        user_dir = self.upload_dir / str(user_id)
        user_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate unique filename
        file_ext = Path(file.filename).suffix.lower()
        file_name = f"{Path(file.filename).stem}_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}{file_ext}"
        file_path = user_dir / file_name
        
        # Save file
        file_size = 0
        with open(file_path, "wb") as f:
            content = await file.read()
            file_size = len(content)
            
            if file_size > self.MAX_FILE_SIZE:
                os.remove(file_path)
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"File size exceeds maximum allowed size of {self.MAX_FILE_SIZE / (1024*1024):.1f}MB"
                )
            
            f.write(content)
        
        return {
            "file_path": str(file_path),
            "file_name": file_name,
            "file_size": file_size,
            "file_type": file_ext
        }
    
    def parse_file(self, file_path: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """Parse CSV or Excel file and return DataFrame with metadata."""
        file_path_obj = Path(file_path)
        file_ext = file_path_obj.suffix.lower()
        
        try:
            if file_ext == ".csv":
                df = pd.read_csv(file_path, encoding="utf-8")
            elif file_ext in [".xlsx", ".xls"]:
                df = pd.read_excel(file_path, engine="openpyxl")
            else:
                raise ValueError(f"Unsupported file type: {file_ext}")
            
            # Get metadata
            metadata = {
                "row_count": len(df),
                "column_count": len(df.columns),
                "columns": df.columns.tolist(),
                "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
                "has_nulls": df.isnull().any().any(),
                "null_counts": df.isnull().sum().to_dict(),
            }
            
            return df, metadata
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error parsing file: {str(e)}"
            )
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and validate data."""
        # Make a copy to avoid modifying original
        df_cleaned = df.copy()
        
        # Remove completely empty rows
        df_cleaned = df_cleaned.dropna(how="all")
        
        # Remove completely empty columns
        df_cleaned = df_cleaned.dropna(axis=1, how="all")
        
        # Strip whitespace from string columns
        for col in df_cleaned.select_dtypes(include=["object"]).columns:
            df_cleaned[col] = df_cleaned[col].astype(str).str.strip()
            # Replace empty strings with NaN
            df_cleaned[col] = df_cleaned[col].replace("", np.nan)
        
        # Convert numeric columns, handling errors
        for col in df_cleaned.columns:
            if df_cleaned[col].dtype == "object":
                # Try to convert to numeric
                numeric_series = pd.to_numeric(df_cleaned[col], errors="coerce")
                if not numeric_series.isna().all():
                    df_cleaned[col] = numeric_series
        
        return df_cleaned
    
    def validate_data(self, df: pd.DataFrame) -> Tuple[bool, Optional[str]]:
        """Validate parsed data."""
        if df.empty:
            return False, "File contains no data"
        
        if len(df.columns) == 0:
            return False, "File contains no columns"
        
        # Check for reasonable number of rows (optional check)
        if len(df) > 1000000:  # 1 million rows
            return False, "File contains too many rows (maximum 1,000,000)"
        
        return True, None
    
    def get_preview(self, df: pd.DataFrame, n_rows: int = 10) -> Dict[str, Any]:
        """Get preview of data (first n rows)."""
        preview_df = df.head(n_rows)
        
        return {
            "columns": df.columns.tolist(),
            "data": preview_df.to_dict(orient="records"),
            "total_rows": len(df),
            "preview_rows": len(preview_df)
        }
    
    async def process_upload(
        self,
        file: UploadFile,
        user_id: int,
        clean: bool = True,
        preview_rows: int = 10
    ) -> Dict[str, Any]:
        """Complete file upload processing pipeline."""
        # Save file
        file_info = await self.save_file(file, user_id)
        
        # Parse file
        df, metadata = self.parse_file(file_info["file_path"])
        
        # Clean data if requested
        if clean:
            df = self.clean_data(df)
            # Update metadata after cleaning
            metadata["row_count_after_cleaning"] = len(df)
            metadata["columns_after_cleaning"] = df.columns.tolist()
        
        # Validate data
        is_valid, error = self.validate_data(df)
        if not is_valid:
            # Clean up file
            os.remove(file_info["file_path"])
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error
            )
        
        # Get preview
        preview = self.get_preview(df, preview_rows)
        
        return {
            "file_info": file_info,
            "metadata": metadata,
            "preview": preview,
            "dataframe": df  # For further processing if needed
        }
