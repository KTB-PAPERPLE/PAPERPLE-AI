from pydantic import BaseModel
from sqlmodel import SQLModel, Field, Text, Column
from typing import Optional
from datetime import datetime, timezone
from sqlalchemy import JSON  # JSON 타입을 가져옵니다.

class APIMODEL:
    class NewsPaper(BaseModel):
        title: str
        summary: list[str]  # List로 변경
        link: str
        image: Optional[str] = None
        source: str
        published_at: str

    class Newspapers(BaseModel):
        page: int
        page_count: int
        newspapers: list["APIMODEL.NewsPaper"]

    class NewsPaperBody(BaseModel):
        url: str


class SQLMODEL:
    class NewsPaper(SQLModel, table=True):
        __tablename__ = "news_paper"
        id: int = Field(default=None, primary_key=True)
        title: str = Field(max_length=255)
        body: str = Field(sa_column=Text())
        summary: list =Field(sa_column=Column(JSON))
        link: str = Field(max_length=2048)
        link_hash: str = Field(max_length=255, sa_column_kwargs={"unique": True})
        image: Optional[str] = Field(default=None, max_length=2048)
        source: str = Field(max_length=255)
        created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
        published_at: datetime = Field(
            default_factory=lambda: datetime.now(timezone.utc)
        )
