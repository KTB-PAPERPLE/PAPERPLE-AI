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
    
def get_summary(text: str) -> list[str]:  # 반환 타입을 List[str]로 변경
    try:
        summary = gpt_summarize(text)  # GPT 기반 요약 함수 호출
        if summary:
            # 요약 결과를 줄바꿈 기준으로 분리하고 각 줄을 정리
            summary_list = summary.splitlines()
            summary_list = [line.strip("* ").strip() for line in summary_list if line.strip()]
            return summary_list
    except Exception as e:
        # 예외 발생 시 오류 로그 출력
        print(f"[ERROR] Summary generation failed: {e}")
    return []

# # test
# print(get_summary('''한국에서도 비만 치료제 ‘위고비’ 대란이 시작됐다. 지난 10월 15일 국내 출시된 위고비는 의사 처방이 필요한 전문의약품이다. 위고비는 일론 머스크 테슬라 최고경영자와 할리우드 배우 등 유명인사들이 체중 감량 비법으로 소개해 ‘꿈의 비만 치료제’로 명성을 얻었다. 국내 출시 후 사회관계망서비스(SNS) 에는 비만 질환이 없는 사람에게도 위고비를 처방해주는 ‘병원 성지 리스트’가 돌고 있다. 비대면 진료와 해외직구 등을 통해 무분별하게 유통돼 품귀현상도 빚어졌다. 오남용 우려가 커지자 보건복지부는 지난 10월 23일 비대면 진료 처방 제외를 검토하겠다고 밝혔다.

# 국내 제약·바이오 업계는 위고비 출시가 비만 치료제 시장 판도를 어떻게 바꿀지 주목하고 있다. 비만에 대한 인식이 개인의 의지 문제가 아닌, 치료가 필요한 질환으로 재정의되면 관련 산업에 파급 효과를 줄 수 있어서다. 위고비가 한국에서도 성공하면 경쟁사인 일라이릴리의 비만 치료제 ‘마운자로’의 국내 출시도 당겨져 시장은 더 커질 전망이다. 위고비보다 뛰어난 체중 감량 효과를 내는 마운자로는 지난 7월 국내 판매 허가를 받았으나 공급량 부족 등으로 출시 일정이 정해지지 않았다. 제약 업계는 향후 체중 감량의 질을 높이는 치료제 경쟁이 이어져 환자의 편의성이 높아질 것으로 기대한다. 의료계에서는 위고비를 계기로 비만 치료제 오남용에 대한 부작용이 커질 것이라고 우려한다.'''))