"""
Step 1 - 예제 3: 여러 입력으로 체인 반복 실행

학습 목표:
- 한 번 정의한 체인을 다양한 입력값으로 재사용
- 체인의 재사용성과 효율성 이해
"""

import os
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain.prompts import PromptTemplate

# 환경 변수 로드
load_dotenv()


def main():
    # API 키 확인
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("ERROR: ANTHROPIC_API_KEY가 설정되지 않았습니다.")
        print(".env 파일을 생성하고 API 키를 설정해주세요.")
        return

    print("=" * 50)
    print("예제 3: 여러 입력으로 체인 반복 실행")
    print("=" * 50)

    # 1. PromptTemplate 정의
    template = "{country}의 수도는 어디인가요? 간단히 답변해주세요."
    prompt = PromptTemplate(
        input_variables=["country"],
        template=template
    )

    # 2. LLM 설정 (temperature=0으로 일관된 답변, Anthropic Claude)
    llm = ChatAnthropic(
        model="claude-3-haiku-20240307",  # Claude 3 Haiku (가장 저렴)
        temperature=0
    )

    # 3. 체인 구성
    chain = prompt | llm

    # 4. 여러 국가에 대해 반복 실행 (3회)
    countries = ["대한민국", "일본", "프랑스"]

    print("\n[실행 중...]\n")
    for country in countries:
        response = chain.invoke({"country": country})
        print(f"{country}: {response.content}")

    print("\n" + "=" * 50)
    print("학습 포인트:")
    print("1. 한 번 정의한 체인을 여러 입력값으로 재사용할 수 있습니다.")
    print("2. temperature=0은 일관되고 결정적인 답변을 생성합니다.")
    print("3. 반복문으로 대량의 데이터를 효율적으로 처리할 수 있습니다.")
    print("4. 프롬프트 템플릿을 사용하면 코드 재사용성이 높아집니다.")
    print("=" * 50)


if __name__ == "__main__":
    main()
