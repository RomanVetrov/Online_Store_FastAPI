from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class CategoryCreate(BaseModel):
    name: str = Field(max_length=50)
    slug: str = Field(max_length=50)


class CategoryUpdatePatch(BaseModel):
    model_config = ConfigDict(extra='forbid')
    name: str | None = Field(None, max_length=50)
    slug: str | None = Field(None, max_length=50)



class CategoryRead(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        extra='forbid' # лишние входные - 422 Unprocessable Entity
        )
    id: int
    name: str
    slug: str
    is_active: bool
    created_at: datetime