"""
Step 3 - 예제 2: Function Calling 전체 플로우

목표:
- 사용자 질문 → tool_calls 확인
- 함수 실행
- 결과를 LLM에 피드백
- 최종 응답 생성
"""

import os
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

# 환경 변수 로드
load_dotenv()

print("=" * 50)
print("예제 2: Function Calling 전체 플로우")
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

# 3. 사용자 질문
user_query = "서울의 날씨를 알려주세요"

print("📌 3. 사용자 질문")
print(f"  '{user_query}'")
print()

print("⚠️  이제 LLM API를 호출합니다 (총 2회).")
print("  - 1회: tool_calls 확인")
print("  - 2회: 최종 응답 생성")
print()

input("Enter를 눌러 계속 진행하세요...")
print()

# 4. 첫 번째 LLM 호출: tool_calls 확인
print("=" * 50)
print("📌 4. 첫 번째 LLM 호출 (tool_calls 확인)")
print("=" * 50)
print()

print("[실행 중...]")
print()

response = llm_with_tools.invoke([HumanMessage(content=user_query)])

print(f"✅ Response 수신")
print(f"  content: '{response.content}'")
print(f"  tool_calls 개수: {len(response.tool_calls) if response.tool_calls else 0}")
print()

if not response.tool_calls:
    print("❌ tool_calls가 없습니다. 함수 호출이 필요 없는 질문입니다.")
    exit()

# 5. tool_call 정보 추출
print("📌 5. tool_call 정보 추출")
tool_call = response.tool_calls[0]

print(f"  함수 이름: {tool_call['name']}")
print(f"  매개변수: {tool_call['args']}")
print(f"  호출 ID: {tool_call['id']}")
print()

# 6. 함수 실행
print("📌 6. 함수 실행")
function_name = tool_call['name']
function_args = tool_call['args']

if function_name == "get_weather":
    function_result = get_weather(**function_args)
    print(f"  {function_name}({function_args})")
    print(f"  → 결과: '{function_result}'")
print()

# 7. 메시지 히스토리 구성
print("📌 7. 메시지 히스토리 구성")
print("  LLM에게 전달할 메시지:")
print()

messages = [
    HumanMessage(content=user_query),
    AIMessage(content=response.content, tool_calls=response.tool_calls),
    ToolMessage(content=function_result, tool_call_id=tool_call['id'])
]

for i, msg in enumerate(messages, 1):
    msg_type = type(msg).__name__
    print(f"  [{i}] {msg_type}")
    if isinstance(msg, HumanMessage):
        print(f"      사용자: '{msg.content}'")
    elif isinstance(msg, AIMessage):
        print(f"      AI: tool_calls 요청")
        if msg.tool_calls:
            print(f"          → {msg.tool_calls[0]['name']}({msg.tool_calls[0]['args']})")
    elif isinstance(msg, ToolMessage):
        print(f"      Tool 결과: '{msg.content}'")
    print()

# 8. 두 번째 LLM 호출: 최종 응답 생성
print("=" * 50)
print("📌 8. 두 번째 LLM 호출 (최종 응답 생성)")
print("=" * 50)
print()

print("[실행 중...]")
print()

final_response = llm_with_tools.invoke(messages)

print(f"✅ 최종 응답:")
print(f"  '{final_response.content}'")
print()

# 9. 전체 흐름 요약
print("=" * 50)
print("📌 9. 전체 흐름 요약")
print("=" * 50)
print()

print("1️⃣  사용자 질문:")
print(f"    '{user_query}'")
print()

print("2️⃣  첫 번째 LLM 호출:")
print(f"    → tool_calls: {tool_call['name']}({tool_call['args']})")
print()

print("3️⃣  함수 실행:")
print(f"    → {function_result}")
print()

print("4️⃣  두 번째 LLM 호출 (결과 피드백):")
print(f"    → 최종 응답: '{final_response.content}'")
print()

print("=" * 50)
print("✅ 예제 2 완료!")
print()
print("핵심 학습 포인트:")
print("1. 첫 번째 LLM 호출로 tool_calls 확인")
print("2. 함수 실행으로 실제 데이터 조회")
print("3. ToolMessage로 결과를 LLM에 피드백")
print("4. 두 번째 LLM 호출로 최종 응답 생성")
print("5. 메시지 히스토리: HumanMessage → AIMessage → ToolMessage")
print("=" * 50)
