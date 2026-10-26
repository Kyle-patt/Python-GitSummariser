from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.schemas.repository import RepositoryInfo
from app.services.github_service import get_repository_info


router = APIRouter(prefix="/api/repository", tags=["Repository"])


class RepositoryRequest(BaseModel):
    repository_url: str = Field(
        min_length=1,
        max_length=500,
    )


@router.post("/info", response_model=RepositoryInfo)
async def repository_info(request: RepositoryRequest):
    return await get_repository_info(request.repository_url)
