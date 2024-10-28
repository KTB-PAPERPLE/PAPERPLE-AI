from dotenv import load_dotenv
import openai
import json
import os
import logging
from openai import OpenAI
import pandas as pd
import time
import ssl
import urllib.request

# OpenAI API 키 설정
load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

# 템플릿 문자열 정의
template_string = """
작업: 다음 기사 내용과 가장 관련있는 주식 종목 1개 이름과 종목 코드를 반환해라. 추출하기에 정보가 충분하지 않다면, '정보불충분'이라고 적어줘라. 이유는 적지마.

관련 종목명:  해당 종목의 이름을 반환

종목 코드: 해당 종목의 코드를 반환

기사본문 내용: {text}
"""

def extract_stock(article_content: str) -> tuple:
    """

    Args:
        article_content (str): 기사 내용
    return:
        종목 코드: 관련 종목명에 따른 주식코드
        관련 종목명: 관련 종목명
    """
    # 템플릿 문자열을 대화 내용으로 완성
    prompt = template_string.format(text=article_content)

    try:
        client = OpenAI(
            api_key=openai.api_key,
        )

        # OpenAI ChatGPT API를 호출하여 응답 받기
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant. "},
                {"role": "user", "content": prompt}
            ],
        )

        # 응답 메시지를 추출
        customer_response = response.choices[0].message.content
        stock_data = customer_response.split('\n')

        # 종목명과 종목코드 추출
        stock_name = stock_data[0].split(":")[1].strip() if len(stock_data) > 0 else '정보불충분'
        stock_code = stock_data[1].split(":")[1].strip() if len(stock_data) > 0 else '정보불충분'
        
        return stock_name, stock_code  # 튜플 형식으로 반환

    except Exception as e:
        # 오류가 발생할 경우 로깅
        logging.error(f"OpenAI API 호출 중 오류 발생: {e}")
        return '정보불충분', '정보불충분'

def process_and_save_stock_info(body: str) -> tuple:
    stock_name, stock_code = extract_stock(body)
    
    # 종목 정보가 '정보불충분'이 아닌 경우 처리
    if '정보불충분' not in stock_code:
        # 종목 정보 가져오기
        return stock_name, stock_code
    elif stock_code=='정보불충분': # 상장 안했을 경우
        return stock_name, 'N/A'
    else:
        # '정보불충분'인 경우 처리
        return 'N/A', 'N/A'

# test
# test='''LG이노텍은 올해 3분기 영업이익이 1304억원을 기록해 전년 동기 대비 28.9% 감소했다고 23일 밝혔다.

# 같은 기간 매출은 5조6851억원으로 19.3% 증가했다.

# 회사 관계자는 "고객사 신모델 양산으로 고부가 카메라 모듈 공급이 확대되고, 반도체 기판, 차량용 통신 모듈의 매출이 늘었다"고 말했다. 다만 "원·달러 환율 하락, 전기차·디스플레이 등 전방 산업의 수요 부진, 광학 사업의 공급 경쟁 심화로 영업이익은 전년 동기 대비 감소했다"고 설명했다.
# '''

# rslt=process_and_save_stock_info(test) #리스트
# print(rslt,type(rslt))


# # 한국 종목 정보 가져오기
# def fetch_korean_stock_info(stock_code: str) -> tuple:
#     if stock_code:
#         url = f"https://m.stock.naver.com/api/stock/{stock_code}/integration"

#         try:
#             # SSL 인증서 무시 설정 (필요한 경우)
#             context = ssl._create_unverified_context()

#             # User-Agent 헤더 추가
#             headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
#             req = urllib.request.Request(url, headers=headers)

#             # URL 열기
#             raw_data = urllib.request.urlopen(req, context=context).read()

#             # JSON 데이터 파싱
#             json_data = json.loads(raw_data)
#             stock_name = json_data.get('stockName', 'N/A')
#             current_price = json_data['dealTrendInfos'][0].get('closePrice', 'N/A')
#             last_price_change = json_data['dealTrendInfos'][0].get('compareToPreviousClosePrice', 'N/A')
#             return stock_name, current_price, last_price_change

#         except Exception as e:
#             logging.error(f"{stock_code}에 해당하는 국내 종목 코드를 찾을 수 없습니다. 오류: {e}")

#     return 'N/A', 'N/A', 'N/A'

# # 외국 종목 및 가상자산 정보 가져오기
# def fetch_foreign_or_crypto_stock_info(stock_code: str) -> tuple:
#     stock_code=stock_code.upper()
#     base_url = "https://api.stock.naver.com/stock/"
#     index_codes = [
#         f"{stock_code}.O",  # 예: NASDAQ (예: AAPL.O)
#         f"{stock_code}.K",  # 예: 뉴욕거래소 (예: AAPL.K)
#         stock_code,         # 기본 종목 코드 (예: AAPL)
#         f".{stock_code}",   # 그 외 (예: .AAPL)
#         f"{stock_code}.HM"  # 베트남 (예: AAPL.HM)
#     ]

#     for index_code in index_codes:
#         url = f"{base_url}{index_code}/basic"
        
#         try:
#             # SSL 인증서 무시 설정 (필요한 경우)
#             context = ssl._create_unverified_context()

#             # User-Agent 헤더 추가
#             headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
            
#             raw_data = urllib.request.urlopen(url).read()
#             json_data = json.loads(raw_data)
            
#             # 필요한 정보 추출
#             stock_name = json_data.get('stockName', 'N/A')
#             current_price = json_data.get('closePrice', 'N/A')
#             last_price_change = json_data.get('compareToPreviousClosePrice', 'N/A')
            
#             # 유효한 응답을 받으면 반환
#             return stock_name, current_price, last_price_change
        
#         except Exception as e:
#             logging.error(f"{index_code}에 해당하는 해외종목코드를 찾을 수 없습니다.")
    
#     url = f'https://m.stock.naver.com/front-api/crypto/otherExchange?nfTicker={stock_code}&excludeExchange=UPBIT'
#     try:
#         raw_data = urllib.request.urlopen(url).read()
#         json_data = json.loads(raw_data)
#         if json_data['isSuccess']:
#             item = json_data['result'][0]
#             stock_name = item['krName']
#             trade_price = item['tradePrice']
#             change_value = item['changeValue']
#             return stock_name, trade_price, change_value
#         else:
#             logging.error(f"{stock_code}에 해당하는 가상자산 데이터를 가져오는 데 실패했습니다.")
            
#     except Exception as e:
#         logging.error(f"{stock_code}에 해당하는 가상자산을 찾을 수 없습니다.")
    
#     return 'N/A', 'N/A', 'N/A'

# # 주식 정보 가져오기
# def fetch_and_append_stock_info(stock_name: str, stock_code: str) -> tuple:
#     # 국내 종목 처리
#     if stock_code.isdigit():
#         stock_name, current_price, last_price_change = fetch_korean_stock_info(stock_code)
#     # 해외 종목 처리
#     else:
#         stock_name, current_price, last_price_change = fetch_foreign_or_crypto_stock_info(stock_code)

#     return stock_name, stock_code, current_price, last_price_change

# # 종목 정보 처리
# def process_and_save_stock_info(row: str) -> tuple:
#     stock_name, stock_code = extract_stock(row)
    
#     # 종목 정보가 '정보불충분'이 아닌 경우 처리
#     if '정보불충분' not in stock_code:
#         # 종목 정보 가져오기
#         stock_data = fetch_and_append_stock_info(stock_name, stock_code)
#         return stock_data  # 튜플 형식으로 반환
#     elif stock_name: # 상장 안했을 경우
#         return stock_name, 'N/A', 'N/A', 'N/A'
#     else:
#         # '정보불충분'인 경우 처리
#         return 'N/A', 'N/A', 'N/A', 'N/A'

# test
# test='''LG이노텍은 올해 3분기 영업이익이 1304억원을 기록해 전년 동기 대비 28.9% 감소했다고 23일 밝혔다.

# 같은 기간 매출은 5조6851억원으로 19.3% 증가했다.

# 회사 관계자는 "고객사 신모델 양산으로 고부가 카메라 모듈 공급이 확대되고, 반도체 기판, 차량용 통신 모듈의 매출이 늘었다"고 말했다. 다만 "원·달러 환율 하락, 전기차·디스플레이 등 전방 산업의 수요 부진, 광학 사업의 공급 경쟁 심화로 영업이익은 전년 동기 대비 감소했다"고 설명했다.
# '''

# rslt=process_and_save_stock_info(test) #리스트
# print(rslt,type(rslt))

