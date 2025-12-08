"""
Step 3 - 예제 4: 함수 호출이 불필요한 질문 테스트

목표:
- 함수 호출 없이 LLM이 직접 답변하는 케이스 확인
- 예제 3과 비교하여 LLM 판단 기준 명확히 이해
- 어떤 질문이 함수 호출을 트리거하지 않는지 확인
"""

import os
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage

# 환경 변수 로드
load_dotenv()

print("=" * 50)
print("예제 4: 함수 호출이 불필요한 질문 테스트")
print("=" * 50)
print()

# 1. 함수 정의 (예제 3과 동일)
def get_weather(city: str) -> str:
    """
    지정된 도시의 현재 날씨를 조회합니다.

    Args:
        city: 날씨를 조회할 도시 이름

    Returns:
        날씨 정보 문자열
    """
    weather_data = {
        "서울": "맑음, 기온 15도",
        "부산": "흐림, 기온 18도",
        "제주": "비, 기온 20도"
    }
    return weather_data.get(city, f"{city}의 날씨 정보를 찾을 수 없습니다.")

print("📌 1. 함수 정의 완료: get_weather()")
print()

# 2. LLM 설정 및 함수 바인딩
llm = ChatAnthropic(
    model="claude-3-haiku-20240307",
    temperature=0
)

llm_with_tools = llm.bind_tools([get_weather])

print("📌 2. LLM 설정 및 함수 바인딩 완료")
print()

# 3. 테스트 시나리오 (함수 호출 불필요한 질문들)
scenarios = [
    {
        "query": "날씨란 무엇인가요?",
        "expected": "함수 호출 불필요",
        "reason": "날씨의 개념/정의에 대한 질문 (일반 지식)"
    },
    {
        "query": "파이썬으로 Hello World를 출력하는 방법은?",
        "expected": "함수 호출 불필요",
        "reason": "날씨와 전혀 무관한 프로그래밍 질문"
    },
    {
        "query": "오늘 점심 메뉴 추천해줘",
        "expected": "함수 호출 불필요",
        "reason": "음식 추천 질문 (날씨 함수와 무관)"
    },
    {
        "query": "기온이 뭐예요?",
        "expected": "함수 호출 불필요",
        "reason": "기온의 개념 설명 (일반 지식)"
    },
    {
        "query": "어제 서울 날씨 어땠어?",
        "expected": "함수 호출 불필요",
        "reason": "과거 날씨 (get_weather는 '현재' 날씨만 조회)"
    }
]

print(f"📌 3. 테스트 시나리오 ({len(scenarios)}개)")
print("   ⚠️  모두 함수 호출이 불필요한 질문입니다")
print()
for i, scenario in enumerate(scenarios, 1):
    print(f"  [{i}] '{scenario['query']}'")
    print(f"      예상: {scenario['expected']}")
    print(f"      이유: {scenario['reason']}")
    print()

print("⚠️  이제 LLM API를 호출합니다.")
print(f"  최대 호출 횟수: {len(scenarios)}회 (함수 호출 없으면 각 1회)")
print()

input("Enter를 눌러 계속 진행하세요...")
print()

# 4. 시나리오별 실행
results = []

for i, scenario in enumerate(scenarios, 1):
    print("=" * 50)
    print(f"📌 시나리오 {i}: '{scenario['query']}'")
    print("=" * 50)
    print()

    # LLM 호출
    print(f"[실행 중...]")
    response = llm_with_tools.invoke([HumanMessage(content=scenario['query'])])
    print()

    # tool_calls 확인
    if response.tool_calls:
        print("⚠️  판단: 함수 호출 필요 (예상과 다름!)")
        tool_call = response.tool_calls[0]
        print(f"  함수: {tool_call['name']}")
        print(f"  매개변수: {tool_call['args']}")
        print()

        results.append({
            "query": scenario['query'],
            "expected": "함수 호출 불필요",
            "actual": "함수 호출함",
            "tool_called": True,
            "function": tool_call['name'],
            "args": tool_call['args']
        })
    else:
        print("✅ 판단: 함수 호출 불필요 (예상대로!)")
        print(f"  직접 응답: '{response.content}'")
        print()

        results.append({
            "query": scenario['query'],
            "expected": "함수 호출 불필요",
            "actual": "직접 답변",
            "tool_called": False,
            "direct_answer": response.content
        })

    print()

# 5. 전체 결과 요약
print("=" * 50)
print("📌 전체 결과 요약")
print("=" * 50)
print()

for i, result in enumerate(results, 1):
    print(f"[{i}] '{result['query']}'")
    print(f"    예상: {result['expected']}")
    print(f"    실제: {result['actual']}")

    if result['tool_called']:
        print(f"    ⚠️  함수 호출: {result['function']}({result['args']})")
    else:
        print(f"    ✅ 직접 답변: '{result['direct_answer'][:100]}...'")
    print()

# 6. 통계 분석
print("=" * 50)
print("📌 결과 통계")
print("=" * 50)
print()

direct_answer_count = sum(1 for r in results if not r['tool_called'])
function_call_count = sum(1 for r in results if r['tool_called'])

print(f"✅ 직접 답변한 경우: {direct_answer_count}개")
print(f"⚠️  함수 호출한 경우: {function_call_count}개")
print()

if direct_answer_count > 0:
    print("✅ 직접 답변한 질문들:")
    for r in results:
        if not r['tool_called']:
            print(f"  - '{r['query']}'")
    print()

if function_call_count > 0:
    print("⚠️  함수 호출한 질문들 (예상과 다름):")
    for r in results:
        if r['tool_called']:
            print(f"  - '{r['query']}'")
    print()

# 7. 예제 3과 비교
print("=" * 50)
print("📌 예제 3 vs 예제 4 비교")
print("=" * 50)
print()

print("예제 3: 날씨 관련 질문")
print("  - 시나리오 1: '서울의 날씨를 알려주세요' → ✅ 함수 호출")
print("  - 시나리오 2: '날씨가 좋으면 무엇을 하면 좋을까요?' → ⚠️ 함수 호출 (예상 외)")
print("  - 시나리오 3: '부산 날씨 어때?' → ✅ 함수 호출")
print("  → 결과: 3개 모두 함수 호출")
print()

print("예제 4: 날씨 무관 질문")
print(f"  → 결과: {direct_answer_count}/{len(scenarios)}개 직접 답변")
print()

print("📌 핵심 차이점:")
print("1. 예제 3: '날씨' 키워드 → 함수 호출 트리거")
print("2. 예제 4: 날씨와 무관하거나 개념 질문 → 직접 답변")
print("3. LLM은 키워드와 질문 의도를 종합적으로 판단")
print()

print("=" * 50)
print("✅ 예제 4 완료!")
print()
print("핵심 학습 포인트:")
print("1. 일반 지식 질문은 LLM이 직접 답변")
print("2. 날씨와 무관한 질문은 함수 호출 안 함")
print("3. 과거/미래 날씨는 '현재' 날씨 함수로 해결 불가")
print("4. 개념/정의 질문은 직접 답변")
print("5. LLM은 함수의 용도와 질문 의도를 매칭하여 판단")
print("=" * 50)
