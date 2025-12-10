"""
Phase 6 - 예제 2: ReAct 패턴 상세 분석

목표:
- ReAct 패턴의 Thought → Action → Observation 사이클 상세 분석
- Agent의 사고 과정 추적 및 최적화
- 다양한 종료 조건 및 반복 제어 테스트
- Agent의 reasoning 능력 심화 이해
"""

import os
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain.agents import create_react_agent, AgentExecutor
from langchain_core.tools import tool
from langchain_core.prompts import PromptTemplate

# 환경 변수 로드
load_dotenv()

print("=" * 70)
print("Phase 6 - 예제 2: ReAct 패턴 상세 분석")
print("=" * 70)
print()

# ============================================================================
# 1. 개선된 도구 정의
# ============================================================================


@tool
def get_weather(city: str) -> str:
    """
    지정된 도시의 현재 날씨를 조회합니다.

    Args:
        city: 날씨를 조회할 도시 이름 (한글/영문 모두 가능)

    Returns:
        현재 날씨 정보 문자열
    """
    # 도시 이름 매핑 테이블 (한글/영문 모두 지원)
    city_mapping = {
        "서울": "서울",
        "seoul": "서울",
        "Seoul": "서울",
        "뉴욕": "뉴욕",
        "new york": "뉴욕",
        "New York": "뉴욕",
        "도쿄": "도쿄",
        "tokyo": "도쿄",
        "Tokyo": "도쿄",
        "파리": "파리",
        "paris": "파리",
        "Paris": "파리",
        "런던": "런던",
        "london": "런던",
        "London": "런던",
    }

    weather_data = {
        "서울": "맑음, 기온 15도",
        "뉴욕": "흐림, 기온 10도",
        "도쿄": "비, 기온 18도",
        "파리": "눈, 기온 2도",
        "런던": "안개, 기온 8도",
    }

    normalized_city = city_mapping.get(city, city)
    result = weather_data.get(
        normalized_city, f"{city}의 날씨 정보를 찾을 수 없습니다."
    )
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


@tool
def extract_temperature(weather_info: str) -> str:
    """
    날씨 정보에서 기온만 추출합니다.

    Args:
        weather_info: 날씨 정보 문자열

    Returns:
        추출된 기온 정보
    """
    import re

    # 기온 패턴 찾기 (예: "기온 15도")
    match = re.search(r"기온\s*(\d+(?:\.\d+)?)\s*도", weather_info)
    if match:
        temp = match.group(1)
        print(f"    [도구 실행] extract_temperature('{weather_info}') → {temp}도")
        return f"{temp}도"
    else:
        print(f"    [도구 실행] extract_temperature('{weather_info}') → 기온 정보 없음")
        return "기온 정보를 찾을 수 없습니다."


print("📌 1. 개선된 도구 정의 완료")
print("  - get_weather: 날씨 조회 (한글/영문 지원)")
print("  - calculate: 수학 계산")
print("  - extract_temperature: 기온 추출")
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
# 3. 상세 ReAct 프롬프트
# ============================================================================

detailed_react_prompt = PromptTemplate.from_template("""
You are a helpful assistant that can answer questions using available tools. 
Think step by step and explain your reasoning clearly.

Available tools:
{tools}

Tool names: {tool_names}

Use the following format:
Question: the input question you must answer
Thought: Break down what you need to do step by step
Action: the action to take, should be one of [{tool_names}]
Action Input: the specific input for the action
Observation: the result of the action
Thought: Based on the observation, what's the next step?
Action: [next action if needed]
Action Input: [input for next action]
Observation: [result of next action]
Thought: Continue this pattern until you have all information needed
Final Answer: Provide a comprehensive answer based on all observations

Important guidelines:
1. Always explain your thought process
2. Use tools only when necessary
3. If you get partial information, think about what else you need
4. Combine multiple tool results when needed
5. Provide clear, final answers

Begin!

Question: {input}
Thought:{agent_scratchpad}""")

print("📌 3. 상세 ReAct 프롬프트 작성 완료")
print("  - 단계별 사고 과정 가이드")
print("  - 명확한 지시문 추가")
print("  - 에러 처리 가이드라인 포함")
print()

# ============================================================================
# 4. Agent 생성 (다양한 설정)
# ============================================================================

tools = [get_weather, calculate, extract_temperature]

# 기본 Agent
basic_agent = create_react_agent(llm, tools, detailed_react_prompt)

# 다양한 AgentExecutor 설정
basic_executor = AgentExecutor(
    agent=basic_agent,
    tools=tools,
    verbose=True,
    max_iterations=5,
    early_stopping_method="force",
    handle_parsing_errors=True,
    return_intermediate_steps=True,
)

# 상세 로깅 Agent
detailed_executor = AgentExecutor(
    agent=basic_agent,
    tools=tools,
    verbose=True,
    max_iterations=10,
    early_stopping_method="force",
    handle_parsing_errors=True,
    return_intermediate_steps=True,
)

# 빠른 종료 Agent
quick_executor = AgentExecutor(
    agent=basic_agent,
    tools=tools,
    verbose=True,
    max_iterations=3,
    early_stopping_method="force",
    handle_parsing_errors=True,
    return_intermediate_steps=True,
)

print("📌 4. 다양한 AgentExecutor 설정 완료")
print("  - basic_executor: 최대 5회 반복")
print("  - detailed_executor: 최대 10회 반복 (상세 분석용)")
print("  - quick_executor: 최대 3회 반복 (빠른 응답용)")
print()

# ============================================================================
# 5. ReAct 사이클 상세 분석 테스트
# ============================================================================

print("=" * 70)
print("📌 5. ReAct 사이클 상세 분석 테스트")
print("=" * 70)
print()

# 테스트 케이스 1: 단계별 reasoning이 필요한 질문
test_query_1 = "서울의 날씨를 확인하고, 기온만 숫자로 추출해줘"

print(f"🔍 테스트 1: {test_query_1}")
print("-" * 70)

try:
    result_1 = detailed_executor.invoke({"input": test_query_1})
    print(f"\n✅ 최종 결과: {result_1['output']}")

    # 중간 단계 상세 분석
    if "intermediate_steps" in result_1:
        print("\n📊 ReAct 사이클 상세 분석:")
        for i, (action, observation) in enumerate(result_1["intermediate_steps"], 1):
            print(f"\n  단계 {i}:")
            print(f"    💭 Thought: {action.tool} 도구가 필요합니다.")
            print(f"    🛠️  Action: {action.tool}({action.tool_input})")
            print(f"    👀  Observation: {observation}")

except Exception as e:
    print(f"❌ 에러: {e}")

print("\n" + "=" * 70)

# 테스트 케이스 2: 복합적인 reasoning이 필요한 질문
test_query_2 = "서울과 뉴욕의 날씨를 확인하고, 두 도시의 평균 기온을 계산해줘"

print(f"🔍 테스트 2: {test_query_2}")
print("-" * 70)

try:
    result_2 = detailed_executor.invoke({"input": test_query_2})
    print(f"\n✅ 최종 결과: {result_2['output']}")

    # 중간 단계 상세 분석
    if "intermediate_steps" in result_2:
        print("\n📊 ReAct 사이클 상세 분석:")
        for i, (action, observation) in enumerate(result_2["intermediate_steps"], 1):
            print(f"\n  단계 {i}:")
            print(f"    💭 Thought: {action.tool} 도구가 필요합니다.")
            print(f"    🛠️  Action: {action.tool}({action.tool_input})")
            print(f"    👀  Observation: {observation}")

except Exception as e:
    print(f"❌ 에러: {e}")

print("\n" + "=" * 70)

# 테스트 케이스 3: 최대 반복 횟수 테스트
test_query_3 = (
    "서울, 뉴욕, 도쿄, 파리, 런던의 날씨를 모두 확인하고, 가장 따뜻한 도시를 알려줘"
)

print(f"🔍 테스트 3: {test_query_3}")
print("-" * 70)

try:
    result_3 = quick_executor.invoke({"input": test_query_3})
    print(f"\n✅ 최종 결과: {result_3['output']}")

    # 반복 횟수 분석
    if "intermediate_steps" in result_3:
        step_count = len(result_3["intermediate_steps"])
        print(f"\n📊 반복 분석:")
        print(f"  - 총 실행 단계: {step_count}회")
        print(f"  - 최대 반복 횟수: 3회")
        print(f"  - 실행률: {step_count}/3")

except Exception as e:
    print(f"❌ 에러: {e}")

# ============================================================================
# 6. AgentExecutor 설정 비교
# ============================================================================

print("\n" + "=" * 70)
print("📌 6. AgentExecutor 설정 비교")
print("=" * 70)

print("""
AgentExecutor 주요 설정 옵션:

1. max_iterations
   - 최대 반복 횟수 제한
   - 너무 많은 반복 방지 (비용/시간 절약)
   - 기본값: 무제한, 권장: 5-10

2. early_stopping_method
   - "force": 즉시 종료
   - "generate": 최종 답변 생성 후 종료
   - "iter": max_iterations 도달 시 종료

3. verbose
   - True: 상세한 실행 과정 로그 출력
   - False: 최종 결과만 출력
   - 디버깅 및 분석에 필수

4. handle_parsing_errors
   - True: 프롬프트 파싱 에러 자동 처리
   - False: 에러 발생 시 예외 발생
   - 안정성 확보를 위해 권장

5. return_intermediate_steps
   - True: 중간 단계 결과 반환
   - False: 최종 결과만 반환
   - 분석 및 디버깅에 유용
""")

# ============================================================================
# 7. ReAct 패턴 최적화 팁
# ============================================================================

print("\n" + "=" * 70)
print("📌 7. ReAct 패턴 최적화 팁")
print("=" * 70)

print("""
1. 프롬프트 최적화
   - 명확한 지시문 작성
   - 단계별 reasoning 가이드
   - 예제 및 템플릿 제공
   - 에러 처리 방법 명시

2. 도구 설계 원칙
   - 단일 책임 원칙 (하나의 도구는 하나의 기능)
   - 명확한 입력/출력 정의
   - 견고한 에러 처리
   - 일관된 반환 형식

3. AgentExecutor 설정
   - 적절한 max_iterations 설정
   - early_stopping_method 선택
   - verbose 모드 활용 (개발/테스트 시)
   - handle_parsing_errors 활성화

4. 성능 최적화
   - 불필요한 도구 호출 피하기
   - 캐싱 활용 (동일 입력)
   - 병렬 처리 고려 (독립적 도구)
   - 적절한 종료 조건 설정

5. 디버깅 전략
   - 단계별 로그 분석
   - 중간 결과 확인
   - 에러 발생 지점 추적
   - 프롬프트 튜닝 반복
""")

print("\n" + "=" * 70)
print("✅ Phase 6 예제 2 완료!")
print("=" * 70)
print()
print("🎉 다음 단계:")
print("  - 예제 3: 커스텀 도구와 Agent")
print("  - 복잡한 도구 정의 및 조합")
print("  - 동적 도구 선택 능력 검증")
print("  - 실전 시나리오 구현 준비")
print()
