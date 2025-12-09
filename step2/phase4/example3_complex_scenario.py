"""
Phase 4 - 예제 3: 복잡한 시나리오

목표:
- 여러 도구를 조합하여 복잡한 질문 처리
- 도구 실행 결과를 다른 도구의 입력으로 사용
- 실전 활용 예시
"""

import os
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

# 환경 변수 로드
load_dotenv()

print("=" * 50)
print("예제 3: 복잡한 시나리오")
print("=" * 50)
print()

# 1. 여러 도구 정의
def get_weather(city: str) -> str:
    """
    지정된 도시의 현재 날씨를 조회합니다.

    Args:
        city: 날씨를 조회할 도시 이름

    Returns:
        현재 날씨 정보 문자열
    """
    weather_data = {
        "서울": "맑음, 기온 15도",
        "뉴욕": "흐림, 기온 10도",
        "도쿄": "비, 기온 18도",
        "파리": "눈, 기온 2도",
        "런던": "안개, 기온 8도"
    }
    result = weather_data.get(city, f"{city}의 날씨 정보를 찾을 수 없습니다.")
    print(f"    [도구 실행] get_weather('{city}') → {result}")
    return result


def calculate(expression: str) -> str:
    """
    수학 표현식을 계산합니다.

    Args:
        expression: 계산할 수학 표현식

    Returns:
        계산 결과
    """
    try:
        result = eval(expression)
        result_str = str(float(result))
        print(f"    [도구 실행] calculate('{expression}') → {result_str}")
        return result_str
    except Exception as e:
        error_msg = f"계산 오류: {str(e)}"
        print(f"    [도구 실행] calculate('{expression}') → {error_msg}")
        return error_msg


def search_web(query: str) -> str:
    """
    웹에서 정보를 검색합니다.

    Args:
        query: 검색 쿼리

    Returns:
        검색 결과
    """
    mock_results = {
        "파이썬": "Python은 1991년 귀도 반 로섬이 개발한 프로그래밍 언어입니다.",
        "langchain": "LangChain은 LLM 애플리케이션 개발 프레임워크입니다.",
        "날씨 추천": "날씨가 좋을 때는 한강공원, 비가 올 때는 박물관 방문을 추천합니다."
    }

    for key in mock_results:
        if key in query.lower():
            result = mock_results[key]
            print(f"    [도구 실행] search_web('{query}') → {result[:50]}...")
            return result

    result = f"'{query}'에 대한 검색 결과를 찾았습니다."
    print(f"    [도구 실행] search_web('{query}') → {result}")
    return result


print("📌 1. 도구 정의 완료")
print("  - get_weather: 날씨 조회")
print("  - calculate: 수학 계산")
print("  - search_web: 웹 검색")
print()

# 2. LLM 설정
llm = ChatAnthropic(
    model="claude-3-haiku-20240307",
    temperature=0
)

tools = [get_weather, calculate, search_web]
llm_with_tools = llm.bind_tools(tools)

print("📌 2. LLM 및 도구 바인딩 완료")
print()

# 3. 복잡한 시나리오 테스트
scenarios = [
    {
        "name": "시나리오 1: 두 도시 날씨 비교",
        "query": "서울과 뉴욕의 날씨를 비교해줘",
        "expected_tools": ["get_weather(서울)", "get_weather(뉴욕)"],
        "description": "두 도시의 날씨를 각각 조회하고 비교"
    },
    {
        "name": "시나리오 2: 날씨 + 계산",
        "query": "서울, 뉴욕, 도쿄의 평균 기온을 계산해줘",
        "expected_tools": ["get_weather(서울)", "get_weather(뉴욕)", "get_weather(도쿄)", "calculate"],
        "description": "세 도시 날씨 조회 후 평균 계산"
    },
    {
        "name": "시나리오 3: 날씨 + 검색",
        "query": "서울 날씨가 좋으면 추천 장소 알려줘",
        "expected_tools": ["get_weather(서울)", "search_web"],
        "description": "날씨 확인 후 조건부 검색"
    }
]

print(f"📌 3. 테스트 시나리오 ({len(scenarios)}개)")
for i, scenario in enumerate(scenarios, 1):
    print(f"  [{i}] {scenario['name']}")
    print(f"      질문: '{scenario['query']}'")
    print(f"      예상 도구: {', '.join(scenario['expected_tools'])}")
    print()

print("⚠️  이제 LLM API를 여러 번 호출합니다.")
print()

input("Enter를 눌러 계속 진행하세요...")
print()

# 4. 시나리오별 실행
for scenario_num, scenario in enumerate(scenarios, 1):
    print("=" * 50)
    print(f"📌 {scenario['name']}")
    print("=" * 50)
    print(f"질문: '{scenario['query']}'")
    print()

    # 메시지 히스토리 초기화
    messages = [HumanMessage(content=scenario['query'])]

    # 실행 통계
    iteration = 0
    tool_calls_count = 0
    MAX_ITERATIONS = 10

    # 수동 실행 루프
    while iteration < MAX_ITERATIONS:
        iteration += 1

        print(f"--- 루프 {iteration}회차 ---")

        # LLM 호출
        response = llm_with_tools.invoke(messages)

        # 종료 조건
        if not response.tool_calls:
            print(f"✅ 최종 답변:")
            print(f"  '{response.content}'")
            print()
            break

        # 도구 호출 처리
        print(f"✅ 도구 호출: {len(response.tool_calls)}개")

        messages.append(AIMessage(content="", tool_calls=response.tool_calls))

        for tool_call in response.tool_calls:
            tool_calls_count += 1
            tool_name = tool_call['name']
            tool_args = tool_call['args']
            tool_id = tool_call['id']

            # 도구 실행
            if tool_name == "get_weather":
                result = get_weather(**tool_args)
            elif tool_name == "calculate":
                result = calculate(**tool_args)
            elif tool_name == "search_web":
                result = search_web(**tool_args)
            else:
                result = f"알 수 없는 도구: {tool_name}"
                print(f"    [오류] {result}")

            # ToolMessage 추가
            messages.append(ToolMessage(
                content=result,
                tool_call_id=tool_id
            ))

        print()

    else:
        print(f"⚠️  최대 반복 횟수({MAX_ITERATIONS}) 초과")
        print()

    # 시나리오 요약
    print(f"📊 시나리오 {scenario_num} 통계:")
    print(f"  - LLM 호출: {iteration}회")
    print(f"  - 도구 호출: {tool_calls_count}회")
    print(f"  - 메시지 수: {len(messages)}개")
    print()
    print()

# 5. 전체 요약
print("=" * 50)
print("📌 Phase 4 전체 요약")
print("=" * 50)
print()

print("Phase 4에서 배운 것:")
print()

print("1️⃣  여러 도구 정의 및 바인딩")
print("  - 3개 이상의 도구를 LLM에 바인딩")
print("  - 각 도구는 명확한 역할과 docstring")
print()

print("2️⃣  LLM의 도구 선택")
print("  - 질문 분석하여 적절한 도구 자동 선택")
print("  - 여러 도구를 순차적으로 호출 가능")
print()

print("3️⃣  수동 실행 루프")
print("  - while True로 반복 실행")
print("  - tool_calls 확인하여 종료 조건 처리")
print("  - 메시지 히스토리로 컨텍스트 유지")
print()

print("4️⃣  복잡한 시나리오 처리")
print("  - 여러 도시 날씨 비교")
print("  - 날씨 조회 후 계산")
print("  - 날씨 확인 후 조건부 검색")
print()

print("5️⃣  실전 활용")
print("  - 도구 결과를 다른 도구의 입력으로 사용")
print("  - 여러 단계를 거쳐 최종 답변 생성")
print("  - LLM이 자율적으로 다음 단계 결정")
print()

# 6. Phase 3 → Phase 4 → Phase 6 흐름
print("=" * 50)
print("📌 학습 로드맵")
print("=" * 50)
print()

print("Phase 3: Function Calling (단일 함수)")
print("  - 함수 1개")
print("  - 단일 호출")
print("  - 기본 개념 학습")
print()

print("Phase 4: Tool Use (여러 함수 + 수동 루프) ← 현재!")
print("  - 여러 함수")
print("  - 반복 호출 (수동 while 루프)")
print("  - 복잡한 시나리오 처리")
print()

print("Phase 6: Agent (자동 루프)")
print("  - AgentExecutor가 자동으로 루프 처리")
print("  - ReAct 패턴")
print("  - Phase 4의 수동 루프를 자동화")
print()

print("=" * 50)
print("✅ Phase 4 완료!")
print()
print("핵심 학습 포인트:")
print("1. 여러 도구를 조합하여 복잡한 질문 처리")
print("2. 도구 실행 결과를 다른 도구의 입력으로 활용")
print("3. 수동 루프로 전체 흐름 제어")
print("4. LLM이 자율적으로 다음 단계 결정")
print("5. Phase 6 (Agent)의 기초 이해")
print("=" * 50)
