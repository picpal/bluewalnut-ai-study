# Step 3 - 예제 1 실행 결과

## 실행 일시
2025-12-08

## 사용 모델
- **LLM**: Anthropic Claude 3 Haiku (claude-3-haiku-20240307)
- **Temperature**: 0 (정확한 판단)

---

## 예제 목표

**함수 정의 및 bind_tools() 기본**
- Python 함수 정의 (docstring, 타입 힌트)
- `bind_tools()`로 LLM에 함수 바인딩
- `tool_calls` 확인하기
- LLM이 함수 호출 여부를 자동으로 판단하는 과정 이해

---

## 코드 구조

### 1. Python 함수 정의

```python
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
```

**핵심 요소:**
- **docstring**: LLM이 함수의 목적을 이해하는 데 사용
- **타입 힌트**: `city: str`, `-> str`로 매개변수와 반환값 타입 지정
- **명확한 설명**: "지정된 도시의 현재 날씨를 조회합니다"

---

### 2. 함수 직접 호출 테스트

```python
result = get_weather("서울")
print(result)  # "맑음, 기온 15도"
```

**목적:** LLM 없이 함수가 제대로 동작하는지 먼저 확인

---

### 3. LLM 설정 및 함수 바인딩

```python
from langchain_anthropic import ChatAnthropic

# 1. LLM 생성 (함수 바인딩 없음)
llm = ChatAnthropic(
    model="claude-3-haiku-20240307",
    temperature=0
)

# 2. bind_tools()로 함수 바인딩
llm_with_tools = llm.bind_tools([get_weather])
```

**bind_tools()의 역할:**
- Python 함수를 JSON 스키마로 변환
- LLM에게 "이런 함수들을 사용할 수 있어"라고 알림
- 함수 시그니처(이름, 매개변수, docstring)를 LLM에 전달

**내부 변환 예시:**
```json
{
  "name": "get_weather",
  "description": "지정된 도시의 현재 날씨를 조회합니다.",
  "parameters": {
    "type": "object",
    "properties": {
      "city": {
        "type": "string",
        "description": "날씨를 조회할 도시 이름"
      }
    },
    "required": ["city"]
  }
}
```

---

### 4. LLM 호출 및 tool_calls 확인

```python
response = llm_with_tools.invoke("서울의 날씨를 알려주세요")
```

---

## 실행 결과

### Response 객체 분석

```python
# Response 타입
type(response)  # <class 'langchain_core.messages.ai.AIMessage'>

# Response content (내부 구조)
response.content = [
    {
        'id': 'toolu_01TPAr7r83PkfHP9AaTmmXra',
        'input': {'city': '서울'},
        'name': 'get_weather',
        'type': 'tool_use'
    }
]
```

**주목할 점:**
- `type: 'tool_use'` → LLM이 도구(함수) 사용을 결정
- `name: 'get_weather'` → 어떤 함수를 호출할지 결정
- `input: {'city': '서울'}` → 함수에 전달할 매개변수

---

### tool_calls 분석 (핵심!)

```python
if response.tool_calls:
    tool_call = response.tool_calls[0]
    print(tool_call)
```

**tool_call 구조:**
```python
{
    'name': 'get_weather',              # 호출할 함수 이름
    'args': {'city': '서울'},           # 함수 매개변수
    'id': 'toolu_01TPAr7r83PkfHP9AaTmmXra'  # 호출 추적 ID
}
```

**의미:**
- ✅ LLM이 "get_weather 함수를 호출해야 한다"고 판단
- ✅ 매개변수로 `city='서울'`을 전달해야 함
- ✅ 개발자가 이 정보를 바탕으로 실제 함수 실행

---

### LLM의 판단 과정

```
사용자 질문: "서울의 날씨를 알려주세요"
        ↓
LLM 분석:
  1. "날씨" 키워드 발견
  2. "서울"이라는 도시 이름 추출
  3. 사용 가능한 함수 확인: get_weather
  4. get_weather의 docstring 확인:
     "지정된 도시의 현재 날씨를 조회합니다"
  5. 매개변수 확인: city (str)
        ↓
LLM 결정:
  ✅ get_weather('서울')을 호출해야 함!
        ↓
tool_calls 반환:
  {
    'name': 'get_weather',
    'args': {'city': '서울'}
  }
```

---

### 실제 함수 실행

```python
# tool_calls에서 정보 추출
tool_call = response.tool_calls[0]
function_name = tool_call['name']      # "get_weather"
function_args = tool_call['args']      # {'city': '서울'}

# 실제 함수 호출
if function_name == "get_weather":
    result = get_weather(**function_args)
    print(result)  # "맑음, 기온 15도"
```

**실행 결과:**
```
get_weather({'city': '서울'}) → 맑음, 기온 15도
```

---

## 전체 흐름 요약

```
1. 함수 정의
   def get_weather(city: str) -> str:
       """지정된 도시의 현재 날씨를 조회합니다."""
        ↓
2. 함수 바인딩
   llm_with_tools = llm.bind_tools([get_weather])
        ↓
3. 사용자 질문
   "서울의 날씨를 알려주세요"
        ↓
4. LLM 호출
   response = llm_with_tools.invoke(질문)
        ↓
5. LLM 판단
   → "날씨 정보 필요" → get_weather 호출 필요!
   → tool_calls 반환
        ↓
6. tool_calls 확인
   if response.tool_calls:
       tool_call = response.tool_calls[0]
       # {'name': 'get_weather', 'args': {'city': '서울'}}
        ↓
7. 함수 실행
   result = get_weather(**tool_call['args'])
   # → "맑음, 기온 15도"
        ↓
8. (예제 2에서 계속)
   결과를 LLM에 피드백 → 최종 응답 생성
```

---

## 핵심 학습 포인트

### 1. docstring의 중요성

```python
def get_weather(city: str) -> str:
    """
    지정된 도시의 현재 날씨를 조회합니다.  # ← LLM이 이것만 봄!
    """
    # 이 코드는 LLM이 보지 못함
```

**LLM은 docstring만 보고 함수 호출 여부를 판단합니다!**

---

### 2. bind_tools()의 역할

```python
llm_with_tools = llm.bind_tools([get_weather])
#                                ↑ 리스트로 전달 (여러 함수 가능)
```

**동작:**
- Python 함수 → JSON 스키마 변환
- LLM에게 함수 정보 전달
- LLM이 필요할 때 함수 호출 요청 가능

---

### 3. response.tool_calls로 판단 확인

```python
if response.tool_calls:
    # ✅ LLM이 함수 호출 필요하다고 판단
    tool_call = response.tool_calls[0]
    print(tool_call['name'])  # 함수 이름
    print(tool_call['args'])  # 매개변수
else:
    # ❌ LLM이 직접 답변 가능하다고 판단
    print(response.content)
```

**핵심:** `tool_calls`의 존재 여부로 LLM의 판단 확인

---

### 4. 실제 함수 실행은 개발자가

```python
# LLM은 함수를 직접 실행하지 않음!
# tool_calls는 "이 함수를 호출해야 해"라는 요청일 뿐

# 개발자가 직접 실행
result = get_weather(**tool_call['args'])
```

**중요:**
- LLM은 **함수 호출을 요청만** 함 (tool_calls 반환)
- 개발자가 **실제로 함수를 실행**
- 예제 2에서는 이 결과를 LLM에 다시 전달하여 최종 응답 생성

---

## Step 2 vs Step 3 비교

### Step 2: Output Parsing

```python
# LLM이 모든 정보를 생성
chain = prompt | llm | parser
result = chain.invoke({"movie_query": "인셉션"})
# result.title = "Inception" (LLM이 알고 있는 정보)
```

**용도:** LLM이 알고 있는 정보를 구조화

---

### Step 3: Function Calling

```python
# LLM이 함수 호출 판단
llm_with_tools = llm.bind_tools([get_weather])
response = llm_with_tools.invoke("서울 날씨 알려줘")
# response.tool_calls → get_weather('서울') 호출 요청

# 개발자가 실제 함수 실행
result = get_weather(**response.tool_calls[0]['args'])
# → "맑음, 기온 15도" (실시간 데이터)
```

**용도:**
- 실시간 데이터 조회
- 외부 시스템 연동
- LLM이 직접 할 수 없는 작업

---

## 다음 단계

**예제 2: Function Calling 전체 플로우**

예제 1에서는 `tool_calls` 확인까지만 했습니다.
예제 2에서는:
1. tool_calls 확인
2. 함수 실행
3. **결과를 LLM에 피드백**
4. **최종 응답 생성** (2번째 LLM 호출)

```python
# 예제 2의 흐름
"서울 날씨 알려줘"
  → tool_calls: get_weather('서울')
  → 함수 실행: "맑음, 15도"
  → LLM에 결과 피드백
  → 최종 응답: "서울은 현재 맑고 기온은 15도입니다."
```

---

## 요약

예제 1을 통해 배운 것:
1. ✅ Python 함수에 **docstring과 타입 힌트** 필수
2. ✅ `bind_tools([함수])`로 LLM에 함수 바인딩
3. ✅ `response.tool_calls`로 LLM의 함수 호출 판단 확인
4. ✅ LLM은 **요청만**, 개발자가 **실제 실행**
5. ✅ docstring이 LLM의 판단에 핵심적인 역할
6. ✅ `tool_calls[0]['name']`, `tool_calls[0]['args']` 사용법

**다음 예제에서는 함수 실행 결과를 LLM에 전달하여 자연스러운 최종 응답을 생성하는 전체 플로우를 학습합니다.**
