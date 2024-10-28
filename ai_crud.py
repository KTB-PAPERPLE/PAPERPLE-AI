import yaml
from fastapi import HTTPException
from sqlmodel import create_engine, SQLModel, Session, select
from sqlalchemy.dialects.mysql import insert
from ai_model import SQLMODEL

db_config: dict[str:str] = None
with open("aws.yaml", "r") as file:
    db_config = yaml.safe_load(file)["database"]

URL_components: list[str] = [
    db_config["drivername"],
    "://",
    db_config["username"],
    ":",
    db_config["password"],
    "@",
    db_config["host"],
    ":",
    db_config["port"],
    "/",
    db_config["database"],
    "?",
    "charset=utf8",
]

engine = create_engine("".join(URL_components))
SQLModel.metadata.create_all(engine)


def upsert_newspapers(newspapers: list[SQLMODEL.NewsPaper]):
    with Session(engine, expire_on_commit=False) as session:
        try:
            for newspaper in newspapers:
                if newspaper.summary is None:
                    raise ValueError("Summary cannot be None")
                stmt = insert(SQLMODEL.NewsPaper).values(newspaper.model_dump())
                stmt = stmt.on_duplicate_key_update(link_hash=stmt.inserted.link_hash)
                session.exec(stmt)
            session.commit()
        except Exception as e:
            session.rollback()
            raise HTTPException(status_code=400, detail="Database integrity error: {}".format(str(e)))


def read_newspaper(link_hash: str) -> SQLMODEL.NewsPaper:
    print("[START]read_newspaper, link_hash:", link_hash)
    with Session(engine, expire_on_commit=False) as session:
        try:
            statement = select(SQLMODEL.NewsPaper).where(
                SQLMODEL.NewsPaper.link_hash == link_hash
            )
            newspaper = session.exec(statement).first()
            if newspaper is None:
                raise HTTPException(status_code=404, detail="Newspaper not found")
            return newspaper
        except Exception as e:
            print("[EXCEPTION]", e)
            raise ValueError

def upsert_stocks(stocks: list[SQLMODEL.StockInfo]):
    saved_stocks = []  # 반환할 주식 정보를 저장할 리스트

    with Session(engine, expire_on_commit=False) as session:
        try:
            for stock in stocks:
                stmt = insert(SQLMODEL.StockInfo).values(stock.model_dump())
                stmt = stmt.on_duplicate_key_update(
                    stock_name=stmt.inserted.stock_name,
                    stock_code=stmt.inserted.stock_code,
                )
                session.exec(stmt)
                
                # 삽입 또는 업데이트 후 주식 정보 추가
                saved_stocks.append({
                    "stock_name": stock.stock_name,
                    "stock_code": stock.stock_code
                })
            session.commit()
        except Exception as e:
            session.rollback()
            raise HTTPException(status_code=400, detail="Database integrity error: {}".format(str(e)))

# def read_stock(stock_id: int) -> SQLMODEL.StockInfo:
#     print("[START] read_stock, stock_id:", stock_id)
#     with Session(engine, expire_on_commit=False) as session:
#         try:
#             statement = select(SQLMODEL.StockInfo).where(
#                 SQLMODEL.StockInfo.id == stock_id
#             )
#             stock = session.exec(statement).first()
#             if stock is None:
#                 raise HTTPException(status_code=404, detail="Stock not found")
#             return stock
#         except Exception as e:
#             print("[EXCEPTION]", e)
#             raise ValueError
# def test():
#     try:
#         newspaper = read_newspaper(
#             link_hash="a2de8839d7f32bb07bd9505612796d7abda66a8bc2a32e0a7ac046f20f279fb2"
#         )
#         print(newspaper.__dir__)
#     except Exception:
#         print("ERROR")


# test()
