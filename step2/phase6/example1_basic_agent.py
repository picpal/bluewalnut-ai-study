"""
Phase 6 - 예제 1: 기본 Agent 생성

목표:
- create_react_agent() 기본 사용법
- AgentExecutor 기본 설정
- Phase 4(수동 루프)와 비교
- Agent의 자율적 도구 선택 이해
"""

import os
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain.agents import create_react_agent, AgentExecutor
from langchain_core.tools import tool

# 환경 변수 로드
load_dotenv()

print("=" * 70)
print("Phase 6 - 예제 1: 기본 Agent 생성")
print("=" * 70)
print()

# ============================================================================
# 1. 도구 정의 (Phase 4와 동일)
# ============================================================================


@tool
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
        "런던": "안개, 기온 8도",
    }
    result = weather_data.get(city, f"{city}의 날씨 정보를 찾을 수 없습니다.")
    print(f"    [도구 실행] get_weather('{city}') → {result}")
    return result


@tool
def calculate(expression: str) -> str:
    """
    수학 표현식을 계산합니다.

    Args:
        expression: 계산할 수학 표현식 문자열

    Returns:
        계산 결과 문자열
    """
    try:
        # 안전한 계산을 위해 기본적인 수학 연산만 허용
        allowed_chars = set("0123456789+-*/(). ")
        if not all(c in allowed_chars for c in expression):
            return "허용되지 않는 문자가 포함되어 있습니다."

        result = eval(expression)
        return str(float(result))
    except Exception as e:
        return f"계산 오류: {str(e)}"


print("📌 1. 도구 정의 완료")
print("  - get_weather: 날씨 조회")
print("  - calculate: 수학 계산")
print()

# ============================================================================
# 2. LLM 설정
# ============================================================================

llm = ChatAnthropic(
    model_name="claude-3-haiku-20240307", temperature=0, timeout=60, stop=None
)

print("📌 2. LLM 설정 완료")
print(f"  - 모델: claude-3-haiku-20240307")
print(f"  - Temperature: 0")
print()

# ============================================================================
# 3. Agent 생성 (Phase 6의 핵심)
# ============================================================================

tools = [get_weather, calculate]

# ReAct Agent 생성
from langchain_core.prompts import PromptTemplate

react_prompt = PromptTemplate.from_template("""
Answer the following questions as best you can. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought:{agent_scratchpad}""")

agent = create_react_agent(llm, tools, react_prompt)

print("📌 3. ReAct Agent 생성 완료")
print("  - create_react_agent() 사용")
print("  - 도구 바인딩 완료")
print()

# ============================================================================
# 4. AgentExecutor 설정
# ============================================================================

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,  # 상세 로그 출력
    max_iterations=10,  # 최대 반복 횟수
    early_stopping_method="generate",  # 조기 종료 방법
    handle_parsing_errors=True,  # 파싱 에러 처리
    return_intermediate_steps=True,  # 중간 단계 반환
)

print("📌 4. AgentExecutor 설정 완료")
print("  - verbose=True: 상세 로그 활성화")
print("  - max_iterations=10: 최대 10회 반복")
print("  - early_stopping_method='generate': 조기 종료 시 답변 생성")
print("  - handle_parsing_errors=True: 파싱 에러 자동 처리")
print()

# ============================================================================
# 5. 기본 테스트
# ============================================================================

print("=" * 70)
print("📌 5. 기본 테스트 시작")
print("=" * 70)
print()

# 테스트 케이스 1: 간단한 날씨 질문
test_query_1 = "서울의 날씨를 알려줘"

print(f"🔍 테스트 1: {test_query_1}")
print("-" * 50)

try:
    result_1 = agent_executor.invoke({"input": test_query_1})
    print(f"\n✅ 결과: {result_1['output']}")
except Exception as e:
    print(f"❌ 에러: {e}")

print("\n" + "=" * 70)

# 테스트 케이스 2: 간단한 계산 질문
test_query_2 = "123 + 456을 계산해줘"

print(f"🔍 테스트 2: {test_query_2}")
print("-" * 50)

try:
    result_2 = agent_executor.invoke({"input": test_query_2})
    print(f"\n✅ 결과: {result_2['output']}")
except Exception as e:
    print(f"❌ 에러: {e}")

print("\n" + "=" * 70)

# 테스트 케이스 3: 복합 질문 (Phase 4와 비교)
test_query_3 = "서울과 뉴욕의 날씨를 알려주고, 두 도시의 평균 기온을 계산해줘"

print(f"🔍 테스트 3: {test_query_3}")
print("-" * 50)

try:
    result_3 = agent_executor.invoke({"input": test_query_3})
    print(f"\n✅ 결과: {result_3['output']}")

    # 중간 단계 분석
    if "intermediate_steps" in result_3:
        print("\n📊 중간 단계 분석:")
        for i, (action, observation) in enumerate(result_3["intermediate_steps"], 1):
            print(f"  {i}. {action.tool}({action.tool_input}) → {observation}")

except Exception as e:
    print(f"❌ 에러: {e}")

print("\n" + "=" * 70)
print("📌 6. Phase 4와의 비교")
print("=" * 70)

print("""
Phase 4 (수동 루프) vs Phase 6 (Agent):

🔧 Phase 4 - 수동 실행 루프:
- 개발자가 while 루프 직접 제어
- 메시지 히스토리 직접 관리
- 도구 호출 로직 직접 구현
- 종료 조건 직접 판단
- 모든 단계를 명시적으로 제어

🤖 Phase 6 - Agent:
- Agent가 자율적으로 도구 선택
- ReAct 패턴으로 자동 reasoning
- 메시지 히스토리 자동 관리
- 종료 조건 자동 판단
- 개발자는 설정만 담당

🎯 핵심 차이점:
1. 자율성: Agent가 스스로 생각하고 행동
2. 단순성: 코드가 훨씬 간결해짐
3. 확장성: 새로운 도구 추가가 쉬움
4. 안정성: LangChain의 검증된 로직 사용
""")

# ============================================================================
# 7. Agent의 사고 과정 분석
# ============================================================================

print("\n" + "=" * 70)
print("📌 7. Agent의 ReAct 사고 과정")
print("=" * 70)

print("""
ReAct (Reasoning + Acting) 패턴:

1. Thought 💭
   - 현재 상황 분석
   - 목표 확인
   - 다음 행동 결정

2. Action 🛠️
   - 적절한 도구 선택
   - 파라미터 결정
   - 도구 실행

3. Observation 👀
   - 도구 실행 결과 확인
   - 결과 분석
   - 목표 달성 여부 판단

4. 반복 🔄
   - 목표 달성 시까지 1-3 반복
   - 최대 반복 횟수 제한
   - 조기 종료 가능

🎯 Agent의 장점:
- 명확한 사고 과정 추적 가능
- 에러 발생 시 원인 파악 용이
- 단계별 최적화 가능
- 디버깅이 쉬움
""")

print("\n" + "=" * 70)
print("✅ Phase 6 예제 1 완료!")
print("=" * 70)
print()
print("🎉 다음 단계:")
print("  - 예제 2: ReAct 패턴 상세 분석")
print("  - Agent의 사고 과정 더 깊이 이해")
print("  - 다양한 종료 조건 및 최적화 방법 학습")
print()
