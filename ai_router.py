from fastapi import APIRouter, HTTPException, status
import ai_model
import ai_service
import ai_exception
from pydantic import BaseModel


class Message(BaseModel):
    message: str


ai_router = APIRouter()


@ai_router.post(
    "/newspaper/",
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Successful Response and Create Newspaper ID"},
        403: {"description": "Forbidden, The page cannot be crawled"},
        404: {"description": "Not Found, The URL Type is not matched"},
        419: {"description": "Not Support, This platform does not support the service"},
    },
)
async def post_newspaper(
    body: ai_model.APIMODEL.NewsPaperBody,
) -> int:
    """
    URL로부터 뉴스 정보를 크롤링하고, DB에 저장하며, 생성된 뉴스의 ID를 반환합니다.
    """
    try:
        newspaper = ai_service.crawl_and_write_newspaper(body.url)
        return newspaper.id  # 뉴스 ID만 반환
    except ai_exception.URLNotCrawlableError as e:
        raise HTTPException(status_code=403, detail={"message": e.args[0]})
    except ai_exception.InvalidURLError as e:
        raise HTTPException(status_code=404, detail={"message": e.args[0]})
    except ai_exception.NotSupportedException as e:
        raise HTTPException(status_code=419, detail={"message": e.args[0]})
    except ai_exception.URLNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.to_dict())
    except Exception as e:
        raise HTTPException(status_code=500, detail={"message": str(e)})


# @ai_router.get(
#     "/stocks/{news_id}/",
#     response_model=list[ai_model.APIMODEL.StockInfo],
#     responses={
#         404: {"description": "Stocks not found"},
#     },
# )
# async def get_stocks(news_id: int):
#     try:
#         # 기사 ID로 주식 정보를 추출하고 데이터베이스에 저장
#         stock_info = ai_service.save_stock_info_to_db(news_id)
        
#         if stock_info is None:
#             raise HTTPException(status_code=404, detail="Stocks not found")

#         return [stock_info]  # 리스트 형태로 반환
#     except HTTPException as e:
#         raise e
#     except Exception as e:
#         raise HTTPException(status_code=500, detail={"message": str(e)})



# @ai_router.get(
#     "/newspapaers/{USER_ID}",
#     responses={404: {"description": "Not Found, Check User Id"}},
# )
# def get_newspapers(user_id: int) -> ai_model.APIMODEL.Newspapers:
#     try:
#         return ai_service.get_newspapers_for_user(user_id)
#     except ai_exception.UserNotFoundError as e:
#         raise HTTPException(status_code=404, detail={"message": e.args[0]})
#     except Exception as e:
#         raise HTTPException(status_code=500, detail={"message": e.args[0]})
