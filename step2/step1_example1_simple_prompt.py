"""
Step 1 - 예제 1: 간단한 PromptTemplate 사용

학습 목표:
- PromptTemplate의 기본 사용법 이해
- 변수를 사용한 동적 프롬프트 생성
"""

from langchain.prompts import PromptTemplate


def main():
    print("=" * 50)
    print("예제 1: 간단한 PromptTemplate")
    print("=" * 50)

    # 1. PromptTemplate 정의
    template = "안녕하세요, {name}님! {greeting}"
    prompt = PromptTemplate(
        input_variables=["name", "greeting"],
        template=template
    )

    # 2. 프롬프트 생성 (변수 삽입)
    result = prompt.format(name="철수", greeting="오늘 날씨가 좋네요.")
    print(f"\n생성된 프롬프트:\n{result}\n")

    # 3. 다른 값으로 재사용
    result2 = prompt.format(name="영희", greeting="반갑습니다!")
    print(f"생성된 프롬프트 2:\n{result2}\n")

    print("=" * 50)
    print("학습 포인트:")
    print("1. PromptTemplate은 변수를 포함한 템플릿을 정의합니다.")
    print("2. input_variables로 사용할 변수를 선언합니다.")
    print("3. format() 메서드로 변수에 값을 삽입합니다.")
    print("4. 같은 템플릿을 다른 값으로 재사용할 수 있습니다.")
    print("=" * 50)


if __name__ == "__main__":
    main()
