from fastapi import FastAPI
import ai_router
from zoneinfo import ZoneInfo
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from contextlib import asynccontextmanager
from crawling import crawling_naver

KST = ZoneInfo("Asia/Seoul")

scheduler = BackgroundScheduler(timezone=KST)


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.start()

    scheduler.add_job(
        crawling_naver.run, trigger=CronTrigger(hour="7,16", timezone=KST)
    )
    
    # 현재 yahoo 스크롤링 이슈
    # scheduler.add_job(
    #     crawling_yahoo.run, trigger=CronTrigger(hour=14, minute=11, timezone=KST)
    # )

    print("[스케줄링] 시작")
    
    yield
    
    scheduler.shutdown()
    print("[스케줄러]종료")

app = FastAPI(lifespan=lifespan)


@app.get("/health")
async def welcome():
    return {"message": "Hello Lunch!"}


app.include_router(ai_router.ai_router)

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(
#         "main:app",  # main.py 파일의 app 객체
#         host="0.0.0.0",  # 외부에서 접속 가능
#         port=8000,       # 포트 8080에서 실행
#         reload=True      # 코드 변경 시 자동 재시작 (개발 환경용)
#     )