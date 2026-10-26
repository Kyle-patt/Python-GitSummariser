from pydantic import BaseModel


class RepositoryInfo(BaseModel):
    name: str
    full_name: str
    description: str | None
    html_url: str
    stars: int
    language: str | None
    forks: int
    open_issues: int
