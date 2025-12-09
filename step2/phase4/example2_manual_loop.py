"""
Phase 4 - 예제 2: 수동 실행 루프 (Manual Execution Loop)

목표:
- while 루프로 도구 반복 실행
- 메시지 히스토리 관리
- 종료 조건 처리
- Phase 3 (단일 호출) vs Phase 4 (반복 루프) 비교
"""

import os
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

# 환경 변수 로드
load_dotenv()

print("=" * 50)
print("예제 2: 수동 실행 루프 (Manual Execution Loop)")
print("=" * 50)
print()

# 1. 도구 정의 (예제 1과 동일)
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
        "도쿄": "비, 기온 18도"
    }
    return weather_data.get(city, f"{city}의 날씨 정보를 찾을 수 없습니다.")


def calculate(expression: str) -> float:
    """
    수학 표현식을 계산합니다.

    Args:
        expression: 계산할 수학 표현식 문자열

    Returns:
        계산 결과
    """
    try:
        result = eval(expression)
        return str(float(result))
    except Exception as e:
        return f"계산 오류: {str(e)}"


print("📌 1. 도구 정의 완료")
print("  - get_weather: 날씨 조회")
print("  - calculate: 수학 계산")
print()

# 2. LLM 설정 및 도구 바인딩
llm = ChatAnthropic(
    model="claude-3-haiku-20240307",
    temperature=0
)

tools = [get_weather, calculate]
llm_with_tools = llm.bind_tools(tools)

print("📌 2. LLM 및 도구 바인딩 완료")
print()

# 3. 테스트 질문
user_query = "서울과 뉴욕의 날씨를 알려주고, 두 도시의 평균 기온을 계산해줘"

print("📌 3. 사용자 질문")
print(f"  '{user_query}'")
print()

print("⚠️  예상 동작:")
print("  1. get_weather('서울') 호출")
print("  2. get_weather('뉴욕') 호출")
print("  3. calculate('평균 계산') 호출")
print("  4. 최종 답변 생성")
print()

print("⚠️  이제 LLM API를 여러 번 호출합니다.")
print()

input("Enter를 눌러 계속 진행하세요...")
print()

# 4. 수동 실행 루프 시작
print("=" * 50)
print("📌 수동 실행 루프 시작")
print("=" * 50)
print()

# 메시지 히스토리 초기화
messages = [HumanMessage(content=user_query)]

# 최대 반복 횟수 (무한 루프 방지)
MAX_ITERATIONS = 10
iteration = 0

while iteration < MAX_ITERATIONS:
    iteration += 1

    print(f"--- 루프 {iteration}회차 ---")
    print()

    # LLM 호출
    print(f"[{iteration}] LLM 호출 중...")
    response = llm_with_tools.invoke(messages)
    print()

    # tool_calls 확인
    if not response.tool_calls:
        # 최종 답변
        print(f"✅ 최종 답변 생성 (도구 호출 없음)")
        print(f"  '{response.content}'")
        print()
        break

    # 도구 호출 정보
    print(f"✅ 도구 호출 요청: {len(response.tool_calls)}개")
    print()

    # AIMessage 추가
    messages.append(AIMessage(content="", tool_calls=response.tool_calls))

    # 각 도구 실행
    for i, tool_call in enumerate(response.tool_calls, 1):
        tool_name = tool_call['name']
        tool_args = tool_call['args']
        tool_id = tool_call['id']

        print(f"  [{i}] 도구: {tool_name}")
        print(f"      매개변수: {tool_args}")

        # 도구 실행
        if tool_name == "get_weather":
            result = get_weather(**tool_args)
        elif tool_name == "calculate":
            result = calculate(**tool_args)
        else:
            result = f"알 수 없는 도구: {tool_name}"

        print(f"      결과: {result}")
        print()

        # ToolMessage 추가
        messages.append(ToolMessage(
            content=result,
            tool_call_id=tool_id
        ))

    print(f"📌 메시지 히스토리 길이: {len(messages)}")
    print()

else:
    # 최대 반복 횟수 초과
    print(f"⚠️  최대 반복 횟수({MAX_ITERATIONS}) 초과")
    print()

# 5. 루프 종료 후 요약
print("=" * 50)
print("📌 실행 요약")
print("=" * 50)
print()

print(f"✅ 총 루프 횟수: {iteration}회")
print(f"✅ 총 LLM 호출: {iteration}회")
print(f"✅ 총 도구 호출: {len([m for m in messages if isinstance(m, ToolMessage)])}회")
print()

# 6. 메시지 히스토리 분석
print("=" * 50)
print("📌 메시지 히스토리 상세")
print("=" * 50)
print()

for i, msg in enumerate(messages, 1):
    msg_type = type(msg).__name__
    print(f"[{i}] {msg_type}")

    if isinstance(msg, HumanMessage):
        print(f"    사용자: '{msg.content[:50]}...'")
    elif isinstance(msg, AIMessage):
        if msg.tool_calls:
            print(f"    AI: 도구 호출 요청 ({len(msg.tool_calls)}개)")
            for tc in msg.tool_calls:
                print(f"        - {tc['name']}({tc['args']})")
        else:
            print(f"    AI: '{msg.content[:50]}...'")
    elif isinstance(msg, ToolMessage):
        print(f"    Tool 결과: '{msg.content[:50]}...'")

    print()

# 7. Phase 3 vs Phase 4 비교
print("=" * 50)
print("📌 Phase 3 vs Phase 4 비교")
print("=" * 50)
print()

print("Phase 3 (단일 호출):")
print("  - 함수 1개만 사용")
print("  - LLM 호출 2회 고정 (tool_calls + 최종)")
print("  - 단순한 질문만 처리 가능")
print("  예: '서울 날씨 알려줘'")
print()

print("Phase 4 (반복 루프):")
print("  - 여러 함수 사용 가능")
print(f"  - LLM 호출 {iteration}회 (동적)")
print("  - 복잡한 질문 처리 가능")
print(f"  예: '{user_query}'")
print()

# 8. 루프 패턴 설명
print("=" * 50)
print("📌 수동 실행 루프 패턴")
print("=" * 50)
print()

print("기본 패턴:")
print("""
messages = [HumanMessage(content=질문)]

while True:
    # LLM 호출
    response = llm_with_tools.invoke(messages)

    # 종료 조건
    if not response.tool_calls:
        print(response.content)  # 최종 답변
        break

    # AIMessage 추가
    messages.append(AIMessage(..., tool_calls=...))

    # 각 도구 실행
    for tool_call in response.tool_calls:
        result = execute_tool(tool_call)
        messages.append(ToolMessage(...))

    # 다시 루프 (LLM이 추가 도구를 호출할 수 있음)
""")
print()

print("핵심 포인트:")
print("1️⃣  while True: 반복 루프")
print("2️⃣  if not response.tool_calls: 종료 조건")
print("3️⃣  messages 리스트에 계속 추가하여 컨텍스트 유지")
print("4️⃣  MAX_ITERATIONS로 무한 루프 방지")
print()

print("=" * 50)
print("✅ 예제 2 완료!")
print()
print("핵심 학습 포인트:")
print("1. 수동 while 루프로 도구 반복 실행")
print("2. tool_calls 확인하여 종료 조건 처리")
print("3. 메시지 히스토리로 전체 대화 컨텍스트 유지")
print("4. 여러 도구를 순차적으로 호출 가능")
print("5. 최대 반복 횟수로 무한 루프 방지")
print("=" * 50)
