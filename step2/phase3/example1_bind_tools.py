"""
Step 3 - 예제 1: 함수 정의 및 bind_tools() 기본

목표:
- Python 함수 정의 (docstring, 타입 힌트)
- bind_tools()로 LLM에 함수 바인딩
- tool_calls 확인하기
"""

import os
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic

# 환경 변수 로드
load_dotenv()

print("=" * 50)
print("예제 1: 함수 정의 및 bind_tools() 기본")
print("=" * 50)
print()

# 1. Python 함수 정의
def get_weather(city: str) -> str:
    """
    지정된 도시의 현재 날씨를 조회합니다.

    Args:
        city: 날씨를 조회할 도시 이름

    Returns:
        날씨 정보 문자열
    """
    # 실제로는 날씨 API를 호출하지만, 예제에서는 간단히 하드코딩
    weather_data = {
        "서울": "맑음, 기온 15도",
        "부산": "흐림, 기온 18도",
        "제주": "비, 기온 20도"
    }

    return weather_data.get(city, f"{city}의 날씨 정보를 찾을 수 없습니다.")

print("📌 1. Python 함수 정의 완료")
print()
print("함수 정보:")
print(f"  - 이름: {get_weather.__name__}")
print(f"  - Docstring: {get_weather.__doc__.strip().split(chr(10))[0]}")
print(f"  - 매개변수: city (str)")
print(f"  - 반환값: str")
print()

# 2. 함수 직접 호출 테스트
print("📌 2. 함수 직접 호출 테스트")
result = get_weather("서울")
print(f"  get_weather('서울') → {result}")
print()

# 3. LLM 설정 (함수 바인딩 없음)
llm = ChatAnthropic(
    model="claude-3-haiku-20240307",
    temperature=0
)

print("📌 3. LLM 설정 완료 (함수 바인딩 없음)")
print()

# 4. bind_tools()로 함수 바인딩
llm_with_tools = llm.bind_tools([get_weather])

print("📌 4. bind_tools()로 함수 바인딩 완료")
print(f"  바인딩된 함수: {[get_weather.__name__]}")
print()

# 5. tool_calls 확인 (LLM 호출)
print("📌 5. tool_calls 확인")
print()
print("⚠️  이제 LLM API를 호출합니다.")
print()

input("Enter를 눌러 계속 진행하세요...")
print()

print("[실행 중...]")
print()

# 함수 호출이 필요한 질문
response = llm_with_tools.invoke("서울의 날씨를 알려주세요")

print("=" * 50)
print("📌 6. 실행 결과")
print("=" * 50)
print()

# 6-1. response 전체 확인
print("📌 6-1. Response 객체")
print(f"  타입: {type(response)}")
print(f"  content: {response.content}")
print()

# 6-2. tool_calls 확인
print("📌 6-2. tool_calls (핵심!)")
if response.tool_calls:
    print(f"  함수 호출 요청이 있습니다!")
    print()

    for i, tool_call in enumerate(response.tool_calls, 1):
        print(f"  [{i}] Tool Call:")
        print(f"      - name: {tool_call['name']}")
        print(f"      - args: {tool_call['args']}")
        print(f"      - id: {tool_call['id']}")
        print()
else:
    print(f"  함수 호출 요청이 없습니다.")
    print()

# 6-3. 함수 호출 여부 판단
print("📌 6-3. LLM의 판단")
if response.tool_calls:
    tool_call = response.tool_calls[0]
    print(f"  ✅ LLM이 판단: '{tool_call['name']}' 함수 호출 필요")
    print(f"  ✅ 매개변수: {tool_call['args']}")
    print()

    # 실제로 함수 호출해보기
    print("📌 6-4. 실제 함수 호출")
    function_name = tool_call['name']
    function_args = tool_call['args']

    if function_name == "get_weather":
        result = get_weather(**function_args)
        print(f"  {function_name}({function_args}) → {result}")
else:
    print(f"  ❌ LLM이 판단: 함수 호출 불필요")

print()

print("=" * 50)
print("✅ 예제 1 완료!")
print()
print("핵심 학습 포인트:")
print("1. Python 함수에 docstring과 타입 힌트 필수")
print("2. bind_tools([함수])로 LLM에 함수 바인딩")
print("3. response.tool_calls로 함수 호출 요청 확인")
print("4. tool_calls[0]['name'], tool_calls[0]['args'] 사용")
print("=" * 50)
