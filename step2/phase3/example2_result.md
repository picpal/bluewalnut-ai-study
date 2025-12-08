# Step 3 - 예제 2 실행 결과

## 실행 일시
2025-12-08

## 사용 모델
- **LLM**: Anthropic Claude 3 Haiku (claude-3-haiku-20240307)
- **Temperature**: 0 (정확한 판단)

---

## 예제 목표

**Function Calling 전체 플로우**
- 사용자 질문 → tool_calls 확인
- 함수 실행
- **결과를 LLM에 피드백** (핵심!)
- **최종 응답 생성**

**예제 1과의 차이:**
- 예제 1: tool_calls 확인 + 함수 실행 (1회 LLM 호출)
- 예제 2: 전체 플로우 + 최종 응답 생성 (2회 LLM 호출)

---

## 코드 구조

### 1. 함수 정의 (예제 1과 동일)

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

---

### 2. LLM 설정 및 함수 바인딩

```python
llm = ChatAnthropic(
    model="claude-3-haiku-20240307",
    temperature=0
)

llm_with_tools = llm.bind_tools([get_weather])
```

---

### 3. 사용자 질문

```python
user_query = "서울의 날씨를 알려주세요"
```

---

## 실행 결과: 전체 플로우

### 4. 첫 번째 LLM 호출 (tool_calls 확인)

```python
response = llm_with_tools.invoke([HumanMessage(content=user_query)])
```

**Response 내용:**
```python
# content (내부 구조)
response.content = [
    {
        'id': 'toolu_01AKAfRqHZqsh1XCDr3zkmSd',
        'input': {'city': '서울'},
        'name': 'get_weather',
        'type': 'tool_use'
    }
]

# tool_calls 개수
len(response.tool_calls)  # 1
```

**LLM의 판단:**
- ✅ "날씨 정보가 필요하다"
- ✅ "get_weather 함수를 사용해야 한다"
- ✅ "매개변수는 city='서울'"

---

### 5. tool_call 정보 추출

```python
tool_call = response.tool_calls[0]

print(tool_call['name'])  # "get_weather"
print(tool_call['args'])  # {'city': '서울'}
print(tool_call['id'])    # "toolu_01AKAfRqHZqsh1XCDr3zkmSd"
```

**tool_call 구조:**
```python
{
    'name': 'get_weather',
    'args': {'city': '서울'},
    'id': 'toolu_01AKAfRqHZqsh1XCDr3zkmSd'
}
```

---

### 6. 함수 실행

```python
function_name = tool_call['name']      # "get_weather"
function_args = tool_call['args']      # {'city': '서울'}

if function_name == "get_weather":
    function_result = get_weather(**function_args)
    print(function_result)  # "맑음, 기온 15도"
```

**실행 결과:**
```
get_weather({'city': '서울'}) → 맑음, 기온 15도
```

**예제 1은 여기서 종료!**
예제 2는 이 결과를 LLM에 다시 전달합니다.

---

### 7. 메시지 히스토리 구성 (핵심!)

```python
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

messages = [
    # 1. 사용자의 원래 질문
    HumanMessage(content=user_query),

    # 2. AI의 함수 호출 요청 (첫 번째 LLM의 응답)
    AIMessage(content=response.content, tool_calls=response.tool_calls),

    # 3. 함수 실행 결과
    ToolMessage(content=function_result, tool_call_id=tool_call['id'])
]
```

**각 메시지의 역할:**

#### [1] HumanMessage
```python
HumanMessage(content="서울의 날씨를 알려주세요")
```
- **역할**: 사용자가 무엇을 물어봤는지
- **내용**: 원래 질문

#### [2] AIMessage
```python
AIMessage(
    content="[{'id': 'toolu_01...', 'input': {'city': '서울'}, ...}]",
    tool_calls=[{
        'name': 'get_weather',
        'args': {'city': '서울'},
        'id': 'toolu_01AKAfRqHZqsh1XCDr3zkmSd'
    }]
)
```
- **역할**: AI가 어떤 함수를 호출하려고 했는지
- **content**: 첫 번째 LLM의 응답 내용
- **tool_calls**: 함수 호출 요청 정보

#### [3] ToolMessage
```python
ToolMessage(
    content="맑음, 기온 15도",
    tool_call_id="toolu_01AKAfRqHZqsh1XCDr3zkmSd"
)
```
- **역할**: 함수를 실행한 결과
- **content**: 함수 실행 결과 (실제 데이터)
- **tool_call_id**: 어떤 함수 호출의 결과인지 추적

**메시지 히스토리가 LLM에게 전달하는 컨텍스트:**
```
"사용자가 '서울의 날씨를 알려주세요'라고 물어봤어.
내(AI)가 get_weather('서울')을 호출했고,
그 결과가 '맑음, 기온 15도'야.
이제 이 정보를 바탕으로 자연스러운 답변을 만들어줘!"
```

---

### 8. 두 번째 LLM 호출 (최종 응답 생성)

```python
final_response = llm_with_tools.invoke(messages)

print(final_response.content)
# "서울의 현재 날씨는 맑고 기온은 15도입니다."
```

**LLM의 역할:**
- 함수 실행 결과("맑음, 기온 15도")를 자연스러운 문장으로 변환
- 사용자 질문에 맞는 완전한 답변 생성

**결과 비교:**
- **함수 직접 실행**: `"맑음, 기온 15도"` (데이터만)
- **LLM 최종 응답**: `"서울의 현재 날씨는 맑고 기온은 15도입니다."` (자연스러운 문장)

---

## 전체 흐름 시각화

```
1. 사용자 질문
   "서울의 날씨를 알려주세요"
        ↓
2. 첫 번째 LLM 호출 (LLM API 1회)
   llm_with_tools.invoke([HumanMessage(content=user_query)])
        ↓
   LLM 판단: "get_weather('서울') 호출 필요!"
        ↓
   response.tool_calls = [{'name': 'get_weather', 'args': {'city': '서울'}}]
        ↓
3. 함수 실행 (Python 함수 실행)
   get_weather(city='서울')
        ↓
   function_result = "맑음, 기온 15도"
        ↓
4. 메시지 히스토리 구성
   messages = [
       HumanMessage("서울의 날씨를 알려주세요"),
       AIMessage(tool_calls=[...]),
       ToolMessage("맑음, 기온 15도")
   ]
        ↓
5. 두 번째 LLM 호출 (LLM API 2회)
   llm_with_tools.invoke(messages)
        ↓
   LLM: "함수 결과를 보니 '맑음, 기온 15도'네.
        자연스러운 문장으로 만들어야지."
        ↓
   final_response.content = "서울의 현재 날씨는 맑고 기온은 15도입니다."
        ↓
6. 최종 응답
   "서울의 현재 날씨는 맑고 기온은 15도입니다."
```

---

## 예제 1 vs 예제 2 상세 비교

### 예제 1: bind_tools() 기본

```python
# 1. LLM 호출 (1회)
response = llm_with_tools.invoke("서울의 날씨를 알려주세요")

# 2. tool_calls 확인
tool_call = response.tool_calls[0]

# 3. 함수 실행
result = get_weather(**tool_call['args'])
# → "맑음, 기온 15도"

# ⚠️ 종료! 데이터만 얻음
```

**결과:** `"맑음, 기온 15도"` (원시 데이터)

**한계:**
- 사용자 질문에 대한 완전한 답변이 아님
- 단순 데이터 출력만 가능

---

### 예제 2: 전체 플로우

```python
# 1. 첫 번째 LLM 호출 (1회)
response = llm_with_tools.invoke([HumanMessage(content="서울의 날씨를 알려주세요")])

# 2. 함수 실행
result = get_weather(**response.tool_calls[0]['args'])
# → "맑음, 기온 15도"

# 3. 메시지 히스토리 구성
messages = [
    HumanMessage(content="서울의 날씨를 알려주세요"),
    AIMessage(content="", tool_calls=response.tool_calls),
    ToolMessage(content=result, tool_call_id=...)
]

# 4. 두 번째 LLM 호출 (2회)
final_response = llm_with_tools.invoke(messages)
# → "서울의 현재 날씨는 맑고 기온은 15도입니다."
```

**결과:** `"서울의 현재 날씨는 맑고 기온은 15도입니다."` (자연스러운 답변)

**장점:**
- 완전한 문장으로 된 답변
- 사용자 친화적
- 챗봇/AI 어시스턴트에 적합

---

## LLM API 호출 횟수

| 단계 | 호출 | 목적 | 입력 | 출력 |
|------|------|------|------|------|
| **1차** | LLM API | 함수 호출 판단 | `"서울의 날씨를 알려주세요"` | `tool_calls` |
| **함수 실행** | Python | 데이터 조회 | `get_weather(city='서울')` | `"맑음, 기온 15도"` |
| **2차** | LLM API | 최종 응답 생성 | `messages` (히스토리) | `"서울의 현재 날씨는..."` |

**총 LLM API 호출: 2회**

---

## 메시지 타입 심화

### 1. HumanMessage

```python
HumanMessage(content="서울의 날씨를 알려주세요")
```

**역할:** 사용자의 입력
**특징:**
- 대화의 시작점
- 사용자의 의도를 담음

---

### 2. AIMessage (tool_calls 포함)

```python
AIMessage(
    content="[{'id': '...', 'input': {'city': '서울'}, ...}]",
    tool_calls=[{
        'name': 'get_weather',
        'args': {'city': '서울'},
        'id': 'toolu_01...'
    }]
)
```

**역할:** AI의 중간 응답 (함수 호출 요청)
**특징:**
- `content`: LLM의 원본 응답 (내부 구조)
- `tool_calls`: 어떤 함수를 호출할지 명시
- 아직 최종 답변이 아님

---

### 3. ToolMessage

```python
ToolMessage(
    content="맑음, 기온 15도",
    tool_call_id="toolu_01AKAfRqHZqsh1XCDr3zkmSd"
)
```

**역할:** 함수 실행 결과 전달
**특징:**
- `content`: 함수 실행 결과 (실제 데이터)
- `tool_call_id`: 어떤 tool_call의 결과인지 추적
- LLM이 이 정보를 보고 최종 답변 생성

**tool_call_id의 역할:**
- AIMessage의 tool_calls[0]['id']와 일치해야 함
- LLM이 "어떤 함수 호출의 결과인지" 알 수 있음
- 여러 함수를 호출할 때 결과를 정확히 매칭

---

### 4. AIMessage (최종 응답)

```python
AIMessage(content="서울의 현재 날씨는 맑고 기온은 15도입니다.")
```

**역할:** AI의 최종 답변
**특징:**
- 자연스러운 문장
- 함수 결과를 바탕으로 생성
- 사용자 질문에 대한 완전한 답변

---

## 왜 메시지 히스토리가 필요한가?

### 히스토리 없이 호출하면?

```python
# ❌ 잘못된 방법
final_response = llm_with_tools.invoke("맑음, 기온 15도")
```

**문제점:**
- LLM은 "맑음, 기온 15도"가 무엇인지 모름
- 원래 질문("서울의 날씨를 알려주세요")을 모름
- 제대로 된 답변 불가능

---

### 히스토리와 함께 호출하면

```python
# ✅ 올바른 방법
messages = [
    HumanMessage(content="서울의 날씨를 알려주세요"),
    AIMessage(content="", tool_calls=[...]),
    ToolMessage(content="맑음, 기온 15도", tool_call_id="...")
]

final_response = llm_with_tools.invoke(messages)
```

**LLM이 이해하는 컨텍스트:**
1. 사용자가 서울 날씨를 물어봄
2. 내가 get_weather('서울')을 호출했음
3. 그 결과가 "맑음, 기온 15도"
4. 이 정보로 "서울의 현재 날씨는 맑고 기온은 15도입니다" 생성

---

## 실전 활용 예시

### 예시 1: 계산기 함수

```python
def calculate(expression: str) -> float:
    """수학 표현식을 계산합니다."""
    return eval(expression)

# 첫 번째 LLM 호출
response = llm_with_tools.invoke("123 곱하기 456은?")
# → tool_calls: calculate("123 * 456")

# 함수 실행
result = calculate(**response.tool_calls[0]['args'])
# → 56088

# 두 번째 LLM 호출
messages = [
    HumanMessage(content="123 곱하기 456은?"),
    AIMessage(content="", tool_calls=response.tool_calls),
    ToolMessage(content=str(result), tool_call_id=...)
]
final_response = llm_with_tools.invoke(messages)
# → "123 곱하기 456은 56,088입니다."
```

---

### 예시 2: 데이터베이스 조회

```python
def get_user_info(user_id: int) -> dict:
    """사용자 정보를 조회합니다."""
    return db.query(user_id)

# 첫 번째 LLM 호출
response = llm_with_tools.invoke("ID 123 사용자 이름 알려줘")
# → tool_calls: get_user_info(123)

# 함수 실행
result = get_user_info(**response.tool_calls[0]['args'])
# → {"name": "철수", "age": 25, "email": "chulsoo@example.com"}

# 두 번째 LLM 호출
messages = [...]
final_response = llm_with_tools.invoke(messages)
# → "ID 123 사용자는 철수님이고, 25세이며, 이메일은 chulsoo@example.com입니다."
```

---

## 핵심 학습 포인트

### 1. 2번의 LLM 호출이 필요한 이유

```
1차 LLM: "어떤 함수를 호출할지 판단"
  → tool_calls 반환

함수 실행: "실제 데이터 조회"
  → 함수 결과 반환

2차 LLM: "결과를 자연스러운 문장으로 변환"
  → 최종 답변 반환
```

---

### 2. 메시지 히스토리의 중요성

```python
messages = [
    HumanMessage,    # 사용자가 무엇을 물었는지
    AIMessage,       # AI가 어떤 함수를 호출했는지
    ToolMessage      # 함수 결과가 무엇인지
]
```

**3가지 정보를 모두 LLM에 전달해야 올바른 최종 응답 생성**

---

### 3. tool_call_id의 역할

```python
# AIMessage의 tool_call
tool_calls=[{
    'id': 'toolu_01AKAfRqHZqsh1XCDr3zkmSd',
    'name': 'get_weather',
    'args': {'city': '서울'}
}]

# ToolMessage
ToolMessage(
    content="맑음, 기온 15도",
    tool_call_id="toolu_01AKAfRqHZqsh1XCDr3zkmSd"  # ← 동일한 ID!
)
```

**tool_call_id로 "어떤 함수 호출의 결과인지" 추적**

---

### 4. ToolMessage의 역할

```python
ToolMessage(
    content=function_result,      # 함수 실행 결과
    tool_call_id=tool_call['id']  # 함수 호출 ID
)
```

**ToolMessage는 함수 실행 결과를 LLM에 전달하는 브릿지**

---

### 5. 전체 플로우 패턴

```python
# 패턴 1: 첫 번째 LLM 호출
response = llm_with_tools.invoke([HumanMessage(content=query)])

# 패턴 2: tool_calls 확인
if response.tool_calls:
    tool_call = response.tool_calls[0]

    # 패턴 3: 함수 실행
    result = function(**tool_call['args'])

    # 패턴 4: 메시지 히스토리 구성
    messages = [
        HumanMessage(content=query),
        AIMessage(content=response.content, tool_calls=response.tool_calls),
        ToolMessage(content=result, tool_call_id=tool_call['id'])
    ]

    # 패턴 5: 두 번째 LLM 호출
    final_response = llm_with_tools.invoke(messages)
```

**이 패턴이 Function Calling의 표준 플로우!**

---

## 다음 단계

**예제 3: 여러 시나리오 테스트**

예제 2에서는 함수 호출이 필요한 질문만 다뤘습니다.
예제 3에서는:
1. **함수 호출이 필요한 질문** (예: "서울의 날씨를 알려주세요")
2. **함수 호출이 불필요한 질문** (예: "날씨가 좋으면 무엇을 하면 좋을까요?")
3. LLM이 언제 함수를 호출하고, 언제 직접 답변하는지 확인

**LLM의 판단 기준:**
- 실시간 데이터 필요 → 함수 호출
- 일반적인 조언/지식 → 직접 답변

---

## 요약

예제 2를 통해 배운 것:
1. ✅ Function Calling은 **2번의 LLM 호출** 필요
2. ✅ **메시지 히스토리** (HumanMessage → AIMessage → ToolMessage)
3. ✅ **ToolMessage**로 함수 결과를 LLM에 피드백
4. ✅ **tool_call_id**로 함수 호출과 결과 매칭
5. ✅ LLM이 함수 결과를 **자연스러운 문장**으로 변환
6. ✅ 전체 플로우 패턴 이해

**다음 예제에서는 LLM이 언제 함수를 호출하고 언제 직접 답변하는지 판단 기준을 학습합니다.**
