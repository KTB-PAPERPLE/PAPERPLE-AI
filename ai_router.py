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
        201: {"description": "Successful Response and Create Newspaper"},
        403: {"description": "Forbidden, The page cannot be crawled"},
        404: {"description": "Not Found, The URL Type is not matched"},
        419: {"description": "Not Support, This platform does not support the service"},
    },
)
async def post_newspaper(
    body: ai_model.APIMODEL.NewsPaperBody,
) -> ai_model.APIMODEL.NewsPaper:
    try:
        # 신문 기사를 크롤링하고 데이터베이스에 저장
        newspaper = ai_service.crawl_and_write_newspaper(body.url)
        
        # 기사 ID로 주식 정보를 추출하고 데이터베이스에 저장
        ai_service.save_stock_info_to_db(newspaper.id)  # newspaper 객체의 id 필드를 사용
        
        return newspaper
    except ai_exception.URLNotCrawlableError as e:
        raise HTTPException(status_code=403, detail={"message": e.args[0]})
    except ai_exception.InvalidURLError as e:
        raise HTTPException(status_code=404, detail={"message": e.args[0]})
    except ai_exception.NotSupportedException as e:
        raise HTTPException(status_code=419, detail={"message": e.args[0]})
    except Exception as e:
        raise HTTPException(status_code=500, detail={"message": e})


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
