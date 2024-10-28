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
        
    class StockInfo(BaseModel):
        link_hash: str  # 뉴스 해시값
        stock_name: str
        stock_code: str


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

    class StockInfo(SQLModel, table=True):
        __tablename__ = "stock_info"
        link_hash: str = Field(default=None, foreign_key="news_paper.link_hash", primary_key=True)  # 뉴스 해시값을 기본 키(foreign key)로 사용
        stock_name: str = Field(max_length=255)  # 관련 종목명
        stock_code: str = Field(max_length=10)  # 종목코드
        # current_price: str  # 현재가격 //쉼표표시를 위해 문자열
        # price_change: str  # 전일대비 등락가격 //쉼표표시를 위해 문자열
