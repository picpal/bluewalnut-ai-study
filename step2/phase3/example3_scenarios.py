"""
Step 3 - 예제 3: 여러 시나리오 테스트

목표:
- 함수 호출이 필요한 질문 vs 불필요한 질문
- LLM의 판단 로직 이해
- 다양한 상황에서 Function Calling 동작 확인
"""

import os
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

# 환경 변수 로드
load_dotenv()

print("=" * 50)
print("예제 3: 여러 시나리오 테스트")
print("=" * 50)
print()

# 1. 함수 정의
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

# 3. 테스트 시나리오
scenarios = [
    {
        "query": "서울의 날씨를 알려주세요",
        "expected": "함수 호출 필요",
        "reason": "실시간 날씨 정보가 필요하므로 get_weather 호출"
    },
    {
        "query": "날씨가 좋으면 무엇을 하면 좋을까요?",
        "expected": "함수 호출 불필요",
        "reason": "일반적인 조언이므로 LLM이 직접 답변 가능"
    },
    {
        "query": "부산 날씨 어때?",
        "expected": "함수 호출 필요",
        "reason": "부산의 실시간 날씨 정보가 필요"
    }
]

print(f"📌 3. 테스트 시나리오 ({len(scenarios)}개)")
for i, scenario in enumerate(scenarios, 1):
    print(f"  [{i}] '{scenario['query']}'")
    print(f"      예상: {scenario['expected']}")
    print(f"      이유: {scenario['reason']}")
    print()

print("⚠️  이제 LLM API를 호출합니다.")
print(f"  총 호출 횟수: {len(scenarios) * 2}회 (각 시나리오당 최대 2회)")
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

    # 첫 번째 호출: tool_calls 확인
    print(f"[실행 중... 1/2]")
    response = llm_with_tools.invoke([HumanMessage(content=scenario['query'])])
    print()

    # tool_calls 확인
    if response.tool_calls:
        print("✅ 판단: 함수 호출 필요")
        tool_call = response.tool_calls[0]
        print(f"  함수: {tool_call['name']}")
        print(f"  매개변수: {tool_call['args']}")
        print()

        # 함수 실행
        function_result = get_weather(**tool_call['args'])
        print(f"  실행 결과: '{function_result}'")
        print()

        # 두 번째 호출: 최종 응답
        print(f"[실행 중... 2/2]")
        messages = [
            HumanMessage(content=scenario['query']),
            AIMessage(content=response.content, tool_calls=response.tool_calls),
            ToolMessage(content=function_result, tool_call_id=tool_call['id'])
        ]
        final_response = llm_with_tools.invoke(messages)
        print()

        print(f"  최종 응답: '{final_response.content}'")

        results.append({
            "query": scenario['query'],
            "tool_called": True,
            "function": tool_call['name'],
            "args": tool_call['args'],
            "function_result": function_result,
            "final_answer": final_response.content
        })
    else:
        print("❌ 판단: 함수 호출 불필요")
        print(f"  직접 응답: '{response.content}'")

        results.append({
            "query": scenario['query'],
            "tool_called": False,
            "final_answer": response.content
        })

    print()

# 5. 전체 결과 요약
print("=" * 50)
print("📌 전체 결과 요약")
print("=" * 50)
print()

for i, result in enumerate(results, 1):
    print(f"[{i}] '{result['query']}'")
    if result['tool_called']:
        print(f"    ✅ 함수 호출: {result['function']}({result['args']})")
        print(f"    → 결과: {result['function_result']}")
    else:
        print(f"    ❌ 함수 호출 없음 (LLM 직접 응답)")
    print(f"    → 최종 답변: '{result['final_answer']}'")
    print()

# 6. LLM 판단 분석
print("=" * 50)
print("📌 LLM 판단 분석")
print("=" * 50)
print()

tool_called_count = sum(1 for r in results if r['tool_called'])
print(f"✅ 함수 호출한 경우: {tool_called_count}개")
print(f"❌ 함수 호출 안 한 경우: {len(results) - tool_called_count}개")
print()

print("📌 LLM이 함수를 호출하는 기준:")
print("1. 실시간 데이터가 필요한 경우")
print("   예: '서울의 날씨를 알려주세요' → get_weather('서울') 호출")
print()
print("2. 함수로 해결 가능한 구체적 질문")
print("   예: '부산 날씨 어때?' → get_weather('부산') 호출")
print()
print("3. 일반적인 지식/조언은 LLM이 직접 응답")
print("   예: '날씨가 좋으면 무엇을 하면 좋을까요?' → 직접 응답")
print()

print("=" * 50)
print("✅ 예제 3 완료!")
print()
print("핵심 학습 포인트:")
print("1. LLM은 질문을 분석해서 함수 호출 여부 자동 판단")
print("2. 실시간 데이터가 필요하면 함수 호출")
print("3. 일반 지식은 LLM이 직접 응답")
print("4. 함수의 docstring과 매개변수 설명이 판단에 중요")
print("=" * 50)
