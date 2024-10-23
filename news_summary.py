from dotenv import load_dotenv
import openai
import json
import os
from openai import OpenAI
import pandas as pd


# OpenAI API 키 설정
load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

# 템플릿 문자열 정의
template_string = """
작업: 다음 기사의 내용을 면밀히 분석하여 가장 중요하고 관련성 높은 정보를 바탕으로 3줄 문장으로 요약하세요. 1줄당 10토큰 이하로 반환. 3가지 포인트를 추출하기에 정보가 충분하지 않다면, 추출할 수 있는 포인트는 기입하고 그 외에는 '정보불충분'이라고 적어주십시오. 각 포인트는 간결하게 한 문장으로 작성하되, 핵심 정보를 포함해야 합니다.

* 문장1
* 문장2
* 문장3
기사본문 내용: {text}
"""

def gpt_summarize(article_content):
    """
    해당 내용을 GPT API로 분석하여 요약하는 함수.

    Args:
        article_content (str): 기사 내용

    Returns:
        dict: 요약된 포인트를 포함한 결과 딕셔너리
    """
    # 템플릿 문자열을 대화 내용으로 완성
    prompt = template_string.format(text=article_content)

    try:

        client = OpenAI(
            api_key=openai.api_key,
        )


        # OpenAI API 호출
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )

        # 응답 메시지를 추출
        customer_response = response.choices[0].message.content

        return customer_response

    except Exception as e:
        # 오류가 발생할 경우 로깅
        print(f"OpenAI API 호출 중 오류 발생: {e}")
        return None
    
def get_summary(text: str) -> str:
    summary = gpt_summarize(text)
    return summary

