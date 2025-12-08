# Function Calling 개념 정리

## Function Calling이란?

**LLM이 필요한 경우 외부 함수를 호출하도록 요청하는 기능**입니다.

---

## 왜 필요한가?

### Step 2의 한계

```python
# Step 2: LLM이 모든 정보를 직접 생성
"서울의 날씨를 알려줘"
→ LLM: "서울은 현재 맑고 기온은 20도입니다." (추측!)
```

**문제점:**
- LLM이 **실시간 데이터**를 알 수 없음
- LLM이 **외부 시스템 데이터**에 접근 불가
- 정확하지 않은 정보 생성 가능 (Hallucination)

### Step 3: Function Calling

```python
# 실제 날씨 API를 호출하는 함수
def get_weather(city: str) -> str:
    # 실제 API 호출
    return weather_api.get(city)

# LLM에 함수 바인딩
llm_with_tools = llm.bind_tools([get_weather])

# LLM이 함수 호출 판단
"서울의 날씨를 알려줘"
→ LLM: "get_weather('서울')을 호출해야 함"
→ 함수 실행: "맑음, 15도"
→ LLM: "서울은 현재 맑고 기온은 15도입니다." (정확!)
```

**장점:**
- ✅ 실시간 데이터 조회
- ✅ 외부 시스템 연동 (DB, API 등)
- ✅ 정확한 정보 제공

---

## Function Calling 동작 원리

### 전체 흐름

```
1. 함수 정의
   def get_weather(city: str) -> str:
       """도시의 날씨를 조회합니다."""
       return "맑음, 15도"
        ↓
2. LLM에 함수 바인딩
   llm_with_tools = llm.bind_tools([get_weather])
        ↓
3. 사용자 질문
   "서울 날씨 알려줘"
        ↓
4. LLM 판단
   → 날씨 정보 필요 → get_weather 호출 필요!
   → tool_calls 반환
        ↓
5. 개발자가 함수 실행
   result = get_weather("서울")
   → "맑음, 15도"
        ↓
6. 결과를 LLM에 피드백
   → LLM이 결과를 바탕으로 최종 응답 생성
        ↓
7. 최종 응답
   "서울은 현재 맑고 기온은 15도입니다."
```

---

## 핵심 구성 요소

### 1. 함수 정의

```python
def get_weather(city: str) -> str:
    """
    지정된 도시의 현재 날씨를 조회합니다.

    Args:
        city: 날씨를 조회할 도시 이름

    Returns:
        날씨 정보 문자열
    """
    # 실제로는 API 호출
    return f"{city}의 날씨는 맑음, 기온 15도"
```

**중요:**
- **Docstring**: LLM이 함수의 용도를 이해하는 데 사용
- **타입 힌트**: 매개변수와 반환값의 타입 지정
- **명확한 이름**: 함수가 무엇을 하는지 명확히 표현

### 2. bind_tools()로 바인딩

```python
from langchain_anthropic import ChatAnthropic

llm = ChatAnthropic(model="claude-3-haiku-20240307")

# 함수를 LLM에 바인딩
llm_with_tools = llm.bind_tools([get_weather])
```

**내부 동작:**
- LLM에게 "이런 함수들을 사용할 수 있어"라고 알려줌
- 함수 시그니처(이름, 매개변수, docstring)를 JSON 스키마로 변환
- LLM이 필요할 때 해당 함수를 호출하도록 요청

### 3. tool_calls 확인

```python
response = llm_with_tools.invoke("서울 날씨 알려줘")

print(response.tool_calls)
# [
#   {
#     "name": "get_weather",
#     "args": {"city": "서울"},
#     "id": "call_abc123"
#   }
# ]
```

**tool_calls:**
- LLM이 호출해야 할 함수 정보
- `name`: 함수 이름
- `args`: 함수 매개변수 (딕셔너리)
- `id`: 호출 ID (추적용)

### 4. 함수 실행

```python
# tool_calls에서 정보 추출
tool_call = response.tool_calls[0]
function_name = tool_call["name"]      # "get_weather"
function_args = tool_call["args"]      # {"city": "서울"}

# 실제 함수 실행
if function_name == "get_weather":
    result = get_weather(**function_args)
    print(result)  # "서울의 날씨는 맑음, 기온 15도"
```

### 5. 결과를 LLM에 피드백

```python
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

messages = [
    HumanMessage(content="서울 날씨 알려줘"),
    AIMessage(content="", tool_calls=response.tool_calls),
    ToolMessage(content=result, tool_call_id=tool_call["id"])
]

# LLM에 다시 전달
final_response = llm_with_tools.invoke(messages)
print(final_response.content)
# "서울은 현재 맑고 기온은 15도입니다."
```

---

## Step 2 vs Step 3 비교

### Step 2: Output Parsing

```python
# LLM이 모든 정보를 생성
chain = prompt | llm | parser

result = chain.invoke({"movie_query": "인셉션"})
# LLM이 알고 있는 정보로 응답
print(result.title)  # "Inception"
```

**용도:**
- LLM이 알고 있는 정보 추출
- 구조화된 데이터 생성

### Step 3: Function Calling

```python
# LLM이 함수 호출 판단
llm_with_tools = llm.bind_tools([get_weather])

response = llm_with_tools.invoke("서울 날씨 알려줘")
# LLM이 모르는 정보 → 함수 호출 요청
result = get_weather(**response.tool_calls[0]["args"])
```

**용도:**
- 실시간 데이터 조회
- 외부 시스템 연동
- 계산, 검색 등 LLM이 직접 못 하는 작업

---

## 언제 Function Calling을 사용하나?

### ✅ Function Calling 필요한 경우

1. **실시간 데이터**
   - 날씨, 주식, 뉴스 등
   - LLM은 학습 시점까지의 데이터만 알고 있음

2. **외부 시스템 데이터**
   - 데이터베이스 조회
   - API 호출
   - 파일 읽기/쓰기

3. **계산/처리**
   - 복잡한 수학 계산
   - 데이터 분석
   - 이미지 처리

4. **액션 실행**
   - 이메일 발송
   - 예약 생성
   - 주문 처리

### ❌ Function Calling 불필요한 경우

1. **일반 지식**
   - "파이썬이 뭐야?" → LLM이 직접 답변 가능

2. **구조화된 응답 생성**
   - Step 2의 Output Parsing으로 충분

---

## 실전 예시

### 예시 1: 날씨 조회

```python
def get_weather(city: str) -> str:
    """도시의 날씨를 조회합니다."""
    # 실제 API 호출
    return weather_api.get(city)

llm_with_tools = llm.bind_tools([get_weather])

# 사용자: "서울 날씨 알려줘"
# LLM: get_weather("서울") 호출 → "맑음, 15도"
# LLM: "서울은 현재 맑고 기온은 15도입니다."
```

### 예시 2: 계산기

```python
def calculate(expression: str) -> float:
    """수학 표현식을 계산합니다."""
    return eval(expression)  # 실전에서는 안전한 방법 사용

llm_with_tools = llm.bind_tools([calculate])

# 사용자: "123 곱하기 456은?"
# LLM: calculate("123 * 456") 호출 → 56088
# LLM: "123 곱하기 456은 56,088입니다."
```

### 예시 3: 데이터베이스 조회

```python
def get_user_info(user_id: int) -> dict:
    """사용자 정보를 조회합니다."""
    return db.query("SELECT * FROM users WHERE id = ?", user_id)

llm_with_tools = llm.bind_tools([get_user_info])

# 사용자: "ID 123 사용자 정보 알려줘"
# LLM: get_user_info(123) 호출 → {"name": "철수", "age": 25}
# LLM: "ID 123 사용자는 철수님이고 25세입니다."
```

---

## LLM이 함수 호출을 판단하는 방법

### 1. 사용자 질문 분석

```
질문: "서울 날씨 알려줘"
→ LLM 판단: "날씨 정보가 필요함"
→ 사용 가능한 함수 확인: get_weather
→ 함수 호출 결정!
```

### 2. 함수 스키마 확인

```python
# LLM이 보는 함수 정보
{
  "name": "get_weather",
  "description": "도시의 날씨를 조회합니다.",
  "parameters": {
    "city": {
      "type": "string",
      "description": "날씨를 조회할 도시 이름"
    }
  }
}
```

### 3. 매개변수 추출

```
질문: "서울 날씨 알려줘"
→ 도시 = "서울"
→ tool_calls: {"name": "get_weather", "args": {"city": "서울"}}
```

---

## 주요 메시지 타입

### 1. HumanMessage
```python
HumanMessage(content="서울 날씨 알려줘")
```
- 사용자의 질문/요청

### 2. AIMessage (tool_calls 포함)
```python
AIMessage(
    content="",
    tool_calls=[{
        "name": "get_weather",
        "args": {"city": "서울"},
        "id": "call_123"
    }]
)
```
- LLM의 함수 호출 요청

### 3. ToolMessage
```python
ToolMessage(
    content="맑음, 15도",
    tool_call_id="call_123"
)
```
- 함수 실행 결과

### 4. AIMessage (최종 응답)
```python
AIMessage(content="서울은 현재 맑고 기온은 15도입니다.")
```
- LLM의 최종 답변

---

## Step 3에서 학습할 내용

### 예제 1: 함수 정의 및 바인딩
- Python 함수 정의 (docstring, 타입 힌트)
- `bind_tools()` 사용법
- `tool_calls` 확인

### 예제 2: 함수 호출 전체 플로우
- 사용자 질문 → tool_calls 확인
- 함수 실행
- 결과를 LLM에 피드백
- 최종 응답 생성

### 예제 3: 여러 시나리오 테스트
- 함수 호출이 필요한 질문
- 함수 호출이 불필요한 질문
- LLM의 판단 로직 이해

---

## 핵심 정리

1. **Function Calling**: LLM이 외부 함수를 호출하도록 요청하는 기능
2. **용도**: 실시간 데이터, 외부 시스템 연동, 계산 등
3. **핵심 메서드**: `bind_tools()`
4. **흐름**: 질문 → tool_calls 확인 → 함수 실행 → 결과 피드백 → 최종 응답
5. **Step 2와 차이**: Step 2는 구조화된 데이터 파싱, Step 3은 외부 함수 호출
