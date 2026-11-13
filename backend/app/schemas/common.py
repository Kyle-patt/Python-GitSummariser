"""
Common schemas for health check and error responses.
"""
from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Health check response schema."""
    status: str = Field("ok", description="Application status")
    app_name: str = Field(..., description="Application name")
    version: str = Field(..., description="API version")
    database: str = Field("connected", description="Database connection status")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ErrorResponse(BaseModel):
    """Standardized API error response schema."""
    error: str = Field(..., description="Error category or class name")
    detail: str = Field(..., description="Human-readable error description")
    status_code: int = Field(..., description="HTTP status code")
    context: Optional[Any] = Field(None, description="Optional diagnostic details")

