import ai_model
import ai_crud
import ai_exception
from util.hash_utils import get_sha256_hash
from util.url_util import get_domain_and_path
from util.datetime_util import convert_str_to_datetime
from model import platform
from news_summary import get_summary
from extract_stock import process_and_save_stock_info
import json

def decode_summary(summary):
    """
    JSON 데이터를 디코딩하며, 유니코드 이스케이프를 처리합니다.
    리스트 항목에 대해 각각 디코딩을 수행합니다.
    """
    if isinstance(summary, list):
        return [json.loads(f'"{item}"') if isinstance(item, str) else item for item in summary]
    return summary

def crawl_and_write_newspaper(url: str) -> ai_model.SQLMODEL.NewsPaper:
    """
    1. 해당 URL의 뉴스를 크롤링하고, 요약합니다
    2. 요약한 정보를 RDS에 저장합니다
    3. 뉴스 정보를 리턴합니다

    Raises:
        ai_exception.InvalidURLError: The URL Type is not matched
        ai_exception.URLNotFoundError: The provided URL was not found
        ai_exception.URLNotCrawlableError: URL Is Not Crawlable

    Args:
        url (str): 크롤링 하고자 하는 뉴스의 URL
    """
    print("[START]crawl_and_write_newspaper, url:", url)
    # URL 도메인 추출
    try:
        domain, path = get_domain_and_path(url)
        link = domain + path
    except Exception:
        raise ai_exception.InvalidURLError

    # 지원하는 도메인인지 확인
    if not platform.Platform.isSupported(domain=domain):
        raise ai_exception.NotSupportedException

    # RDS에 존재하는지 확인
    link_hash = get_sha256_hash(link)
    try:
        newspaper = ai_crud.read_newspaper(link_hash=link_hash)
        return newspaper  # DB에 이미 존재하는 경우 객체 반환

    except Exception:
        # news 크롤링
        try:
            title, body, image, source, published_at = (
                platform.Platform.get_crawling_method(domain=domain)(link)
            )

            summary = get_summary(body)
            published_at = convert_str_to_datetime(
                date_str=published_at,
                date_format=platform.Platform.get_date_format(domain=domain),
            )

            # 주식 정보를 분석하고 저장하기 위해 처리
            stock_name, stock_code = process_and_save_stock_info(body)
            
            # DB 저장
            sql_newspaper = ai_model.SQLMODEL.NewsPaper(
                title=title,
                body=body,
                summary=summary or [],
                link=link,
                link_hash=link_hash,
                image=image,
                source=source,
                published_at=published_at,
                stock_name=stock_name,
                stock_code=stock_code
            )
            ai_crud.upsert_newspapers([sql_newspaper])

            # 방금 저장한 뉴스의 ID를 DB에서 가져오기
            return ai_crud.read_newspaper(link_hash=link_hash)

        except Exception as e:
            raise e


# def save_stock_info_to_db(news_id: int):
#     """
#     주식 정보를 DB에 저장합니다.

#     Args:
#         news_id (int): 뉴스 ID
#     """
#     print("[START] extract stock about news_id:", news_id)
    
#     # news_id에 해당하는 뉴스 본문을 DB에서 읽어오기
#     try:
#         body = ai_crud.read_newspaper_by_id(news_id=news_id)
#         if not body:
#             print(f"[ERROR] No newspaper found with ID: {news_id}")
#             return None
#     except Exception as e:
#         print("[EXCEPTION] Failed to read newspaper:", e)
#         return

#     try:
#         # 주식 정보를 분석하고 저장하기 위해 처리
#         stock_name, stock_code = process_and_save_stock_info(body)
        
#         # 주식 정보를 unpacking
#         # stock_name, stock_code, current_price, last_price_change = stock_info

#         # DB에 저장할 주식 정보 객체 생성
#         sql_stock_info = ai_model.SQLMODEL.StockInfo(
#             news_id=news_id,  # 뉴스 ID 참조
#             stock_name=stock_name,
#             stock_code=stock_code,
#             #current_price=current_price,
#             #price_change=last_price_change,
#         )
        
#         # DB에 저장
#         if sql_stock_info:
#             ai_crud.upsert_stocks([sql_stock_info])
#         else:
#             print("[ERROR] Stock information is empty and cannot be saved.")
#             return None
        
#         return ai_model.APIMODEL.StockInfo(
#                 news_id=news_id,  # 뉴스 ID 참조
#                 stock_name=stock_name,
#                 stock_code=stock_code,
#             )
#     except Exception as e:
#         print(f"[ERROR] Failed to save stock info: {e}")
#         return None  # 오류 발생 시 None 반환
    
# def get_newspapers_for_user(user_id: int) -> ai_model.APIMODEL.Newspapers:
#     # 1. User ID로 페이지 리스트 받아오기
#     page = 0
#     page_count = 10
#     newspapers = []

#     return ai_model.APIMODEL.Newspapers(
#         page=page, page_count=page_count, newspapers=newspapers
#     )
