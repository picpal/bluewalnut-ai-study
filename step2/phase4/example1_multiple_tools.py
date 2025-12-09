"""
Phase 4 - 예제 1: 여러 도구 정의 및 LLM의 도구 선택

목표:
- 3개 이상의 도구(함수) 정의
- LLM에 여러 도구 바인딩
- LLM이 질문에 따라 적절한 도구를 선택하는지 확인
"""

import os
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage

# 환경 변수 로드
load_dotenv()

print("=" * 50)
print("예제 1: 여러 도구 정의 및 LLM의 도구 선택")
print("=" * 50)
print()

# 1. 여러 도구 정의
def get_weather(city: str) -> str:
    """
    지정된 도시의 현재 날씨를 조회합니다.

    실시간 날씨 정보가 필요할 때 사용하세요.

    Args:
        city: 날씨를 조회할 도시 이름 (예: "서울", "뉴욕")

    Returns:
        현재 날씨 정보 문자열
    """
    weather_data = {
        "서울": "맑음, 기온 15도",
        "뉴욕": "흐림, 기온 10도",
        "도쿄": "비, 기온 18도",
        "파리": "눈, 기온 2도"
    }
    return weather_data.get(city, f"{city}의 날씨 정보를 찾을 수 없습니다.")


def calculate(expression: str) -> float:
    """
    수학 표현식을 계산합니다.

    복잡한 수학 계산이 필요할 때 사용하세요.
    예: "123 * 456", "(10 + 5) / 3", "2 ** 10"

    Args:
        expression: 계산할 수학 표현식 문자열

    Returns:
        계산 결과 (실수)
    """
    try:
        result = eval(expression)
        return float(result)
    except Exception as e:
        return f"계산 오류: {str(e)}"


def search_web(query: str) -> str:
    """
    웹에서 정보를 검색합니다.

    실시간 정보나 최신 뉴스, 일반 지식 검색이 필요할 때 사용하세요.

    Args:
        query: 검색할 쿼리 문자열

    Returns:
        검색 결과 요약
    """
    # 실제로는 검색 API를 호출하지만, 예제에서는 하드코딩
    mock_results = {
        "파이썬": "Python은 1991년 귀도 반 로섬이 개발한 프로그래밍 언어입니다.",
        "langchain": "LangChain은 LLM 애플리케이션 개발을 위한 프레임워크입니다.",
        "한강공원": "한강공원은 서울의 대표적인 야외 휴식 공간입니다."
    }

    for key in mock_results:
        if key in query.lower():
            return mock_results[key]

    return f"'{query}'에 대한 검색 결과: 관련 정보를 찾았습니다."


print("📌 1. 도구 정의 완료")
print()
print("정의된 도구:")
print(f"  [1] get_weather: {get_weather.__doc__.strip().split(chr(10))[0]}")
print(f"  [2] calculate: {calculate.__doc__.strip().split(chr(10))[0]}")
print(f"  [3] search_web: {search_web.__doc__.strip().split(chr(10))[0]}")
print()

# 2. LLM 설정 및 도구 바인딩
llm = ChatAnthropic(
    model="claude-3-haiku-20240307",
    temperature=0
)

tools = [get_weather, calculate, search_web]
llm_with_tools = llm.bind_tools(tools)

print("📌 2. LLM에 도구 바인딩 완료")
print(f"  바인딩된 도구 개수: {len(tools)}")
print()

# 3. 테스트 시나리오
test_scenarios = [
    {
        "query": "서울의 날씨를 알려주세요",
        "expected_tool": "get_weather",
        "reason": "날씨 정보 필요 → get_weather 도구 사용"
    },
    {
        "query": "123 곱하기 456은 얼마야?",
        "expected_tool": "calculate",
        "reason": "수학 계산 필요 → calculate 도구 사용"
    },
    {
        "query": "파이썬이 뭐야?",
        "expected_tool": "search_web",
        "reason": "일반 지식 검색 필요 → search_web 도구 사용"
    },
    {
        "query": "안녕하세요",
        "expected_tool": "None",
        "reason": "도구 불필요 → LLM이 직접 답변"
    }
]

print(f"📌 3. 테스트 시나리오 ({len(test_scenarios)}개)")
for i, scenario in enumerate(test_scenarios, 1):
    print(f"  [{i}] '{scenario['query']}'")
    print(f"      예상 도구: {scenario['expected_tool']}")
    print(f"      이유: {scenario['reason']}")
    print()

print("⚠️  이제 LLM API를 호출합니다.")
print(f"  총 호출 횟수: {len(test_scenarios)}회")
print()

input("Enter를 눌러 계속 진행하세요...")
print()

# 4. 시나리오별 실행
results = []

for i, scenario in enumerate(test_scenarios, 1):
    print("=" * 50)
    print(f"📌 시나리오 {i}: '{scenario['query']}'")
    print("=" * 50)
    print()

    print("[실행 중...]")
    response = llm_with_tools.invoke([HumanMessage(content=scenario['query'])])
    print()

    if response.tool_calls:
        tool_call = response.tool_calls[0]
        print(f"✅ LLM 선택: {tool_call['name']} 도구")
        print(f"  매개변수: {tool_call['args']}")
        print()

        # 예상과 일치 확인
        if tool_call['name'] == scenario['expected_tool']:
            print(f"  ✅ 예상과 일치!")
        else:
            print(f"  ⚠️  예상과 다름 (예상: {scenario['expected_tool']})")

        results.append({
            "query": scenario['query'],
            "expected": scenario['expected_tool'],
            "actual": tool_call['name'],
            "matched": tool_call['name'] == scenario['expected_tool']
        })
    else:
        print("✅ LLM 선택: 도구 사용 안 함 (직접 답변)")
        print(f"  직접 응답: '{response.content}'")
        print()

        # 예상과 일치 확인
        if scenario['expected_tool'] == "None":
            print(f"  ✅ 예상과 일치!")
        else:
            print(f"  ⚠️  예상과 다름 (예상: {scenario['expected_tool']})")

        results.append({
            "query": scenario['query'],
            "expected": scenario['expected_tool'],
            "actual": "None",
            "matched": scenario['expected_tool'] == "None"
        })

    print()

# 5. 전체 결과 요약
print("=" * 50)
print("📌 전체 결과 요약")
print("=" * 50)
print()

for i, result in enumerate(results, 1):
    status = "✅" if result['matched'] else "⚠️"
    print(f"{status} [{i}] '{result['query']}'")
    print(f"      예상: {result['expected']}")
    print(f"      실제: {result['actual']}")
    print()

# 6. 통계 분석
print("=" * 50)
print("📌 결과 통계")
print("=" * 50)
print()

matched_count = sum(1 for r in results if r['matched'])
total_count = len(results)
accuracy = (matched_count / total_count) * 100

print(f"✅ 예상과 일치: {matched_count}/{total_count} ({accuracy:.1f}%)")
print()

# 도구별 사용 횟수
tool_usage = {}
for result in results:
    tool = result['actual']
    tool_usage[tool] = tool_usage.get(tool, 0) + 1

print("📌 도구별 사용 횟수:")
for tool, count in tool_usage.items():
    print(f"  {tool}: {count}회")
print()

# 7. LLM의 도구 선택 기준 분석
print("=" * 50)
print("📌 LLM의 도구 선택 기준")
print("=" * 50)
print()

print("1️⃣  get_weather 선택 기준:")
print("  - '날씨', '기온', '날' 등 날씨 관련 키워드")
print("  - 구체적인 도시 이름")
print("  - '현재', '지금' 등 실시간 정보 요청")
print()

print("2️⃣  calculate 선택 기준:")
print("  - 숫자가 포함된 수학 표현식")
print("  - '곱하기', '나누기', '더하기' 등 수학 연산 키워드")
print("  - '계산', '얼마' 등 계산 요청 키워드")
print()

print("3️⃣  search_web 선택 기준:")
print("  - 일반 지식 질문 ('~이 뭐야?', '~란?')")
print("  - LLM이 모르는 최신 정보")
print("  - 구체적인 정보 검색 요청")
print()

print("4️⃣  도구 사용 안 함 (직접 답변):")
print("  - 인사말, 간단한 대화")
print("  - LLM이 알고 있는 일반 지식")
print("  - 도구로 해결할 수 없는 질문")
print()

print("=" * 50)
print("✅ 예제 1 완료!")
print()
print("핵심 학습 포인트:")
print("1. 여러 도구를 동시에 LLM에 바인딩")
print("2. LLM이 질문을 분석하여 적절한 도구 자동 선택")
print("3. 각 도구의 docstring이 선택 기준에 중요한 역할")
print("4. 도구가 필요 없는 경우 LLM이 직접 답변")
print("5. Phase 3 (단일 도구) → Phase 4 (여러 도구)")
print("=" * 50)
