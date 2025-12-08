"""
Step 1 - 예제 2: PromptTemplate + LLM 체인

학습 목표:
- PromptTemplate과 LLM을 연결하는 방법 이해
- LCEL의 파이프 연산자 | 사용법 학습
- chain.invoke()로 체인 실행하기
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
    print("예제 2: PromptTemplate + LLM 체인")
    print("=" * 50)

    # 1. PromptTemplate 정의
    template = """당신은 친절한 AI 어시스턴트입니다.
사용자의 이름은 {name}이고, 관심사는 {interest}입니다.

사용자에게 관심사와 관련된 추천을 3가지 해주세요."""

    prompt = PromptTemplate(
        input_variables=["name", "interest"],
        template=template
    )

    # 2. LLM 설정 (Anthropic Claude)
    llm = ChatAnthropic(
        model="claude-3-haiku-20240307",  # Claude 3 Haiku (가장 저렴)
        temperature=0.7
    )

    # 3. LCEL 체인 구성: prompt | llm
    chain = prompt | llm

    # 4. 체인 실행
    print("\n[실행 중...]\n")
    response = chain.invoke({
        "name": "민수",
        "interest": "파이썬 프로그래밍"
    })

    print(f"LLM 응답:\n{response.content}\n")

    print("=" * 50)
    print("학습 포인트:")
    print("1. | (파이프) 연산자로 prompt와 llm을 연결합니다.")
    print("2. chain.invoke()로 체인을 실행하고 결과를 받습니다.")
    print("3. response.content로 LLM의 텍스트 응답에 접근합니다.")
    print("4. temperature는 응답의 창의성을 조절합니다 (0~1).")
    print("=" * 50)


if __name__ == "__main__":
    main()
