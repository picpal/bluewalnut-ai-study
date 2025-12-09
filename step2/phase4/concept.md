# Phase 4: Tool Use — 여러 함수 + 수동 실행 루프

## Phase 4란?

**여러 도구(함수)를 LLM이 선택하고, 수동 루프로 반복 실행하는 단계**

---

## Phase 3 vs Phase 4

### Phase 3: 단일 함수 Function Calling

```python
# 함수 1개만
def get_weather(city: str) -> str:
    """날씨 조회"""
    return "맑음, 15도"

llm_with_tools = llm.bind_tools([get_weather])

# 사용자 질문
"서울 날씨 알려줘"
    ↓
# LLM 호출 (1회)
response = llm_with_tools.invoke(질문)
    ↓
# 함수 실행 (1회)
result = get_weather(**tool_call['args'])
    ↓
# 최종 응답 (1회)
final = llm_with_tools.invoke(messages)
```

**특징:**
- ✅ 함수 1개
- ✅ 단일 호출
- ✅ 간단한 흐름

---

### Phase 4: 여러 함수 + 반복 실행 루프

```python
# 여러 함수
def get_weather(city: str) -> str:
    """날씨 조회"""
    return "맑음, 15도"

def calculate(expression: str) -> float:
    """계산"""
    return eval(expression)

def search_web(query: str) -> str:
    """웹 검색"""
    return "검색 결과..."

llm_with_tools = llm.bind_tools([get_weather, calculate, search_web])

# 사용자 질문
"서울 날씨와 뉴욕 날씨를 비교해줘"
    ↓
# 수동 루프 시작
while True:
    # LLM 호출
    response = llm_with_tools.invoke(messages)

    # tool_calls 확인
    if not response.tool_calls:
        # 최종 답변
        break

    # 각 tool_call 실행
    for tool_call in response.tool_calls:
        result = execute_tool(tool_call)
        messages.append(ToolMessage(...))

    # 다시 루프 (LLM이 더 호출할 수 있음)
```

**특징:**
- ✅ 여러 함수 (3개 이상)
- ✅ 반복 호출 (while 루프)
- ✅ LLM이 도구 선택
- ✅ 복잡한 시나리오 처리

---

## 왜 Phase 4가 필요한가?

### Phase 3의 한계

```
질문: "서울 날씨와 뉴욕 날씨를 비교해줘"

Phase 3 방식:
1. LLM 호출 → get_weather('서울')
2. 함수 실행 → "맑음, 15도"
3. 최종 응답 생성

❌ 문제: 뉴욕 날씨를 못 가져옴!
```

**Phase 3은 한 번의 함수 호출만 처리**

---

### Phase 4로 해결

```
질문: "서울 날씨와 뉴욕 날씨를 비교해줘"

Phase 4 방식:
1. LLM 호출 → get_weather('서울')
2. 함수 실행 → "맑음, 15도"
3. 다시 LLM 호출 → get_weather('뉴욕')
4. 함수 실행 → "흐림, 18도"
5. 최종 응답 → "서울(맑음, 15도)과 뉴욕(흐림, 18도) 비교..."

✅ 여러 함수 호출로 복잡한 질문 처리!
```

---

## 핵심 개념

### 1. 여러 도구 정의

```python
tools = [
    get_weather,    # 날씨 조회
    calculate,      # 계산
    search_web,     # 검색
    get_user_info,  # 사용자 정보
]

llm_with_tools = llm.bind_tools(tools)
```

**LLM이 상황에 따라 적절한 도구를 선택**

---

### 2. 수동 실행 루프

```python
messages = [HumanMessage(content=user_query)]

while True:
    # LLM 호출
    response = llm_with_tools.invoke(messages)

    # 종료 조건: tool_calls가 없으면 최종 답변
    if not response.tool_calls:
        print(response.content)
        break

    # tool_calls 처리
    messages.append(AIMessage(content="", tool_calls=response.tool_calls))

    for tool_call in response.tool_calls:
        # 함수 실행
        result = execute_tool(tool_call)

        # 결과 추가
        messages.append(ToolMessage(
            content=result,
            tool_call_id=tool_call['id']
        ))

    # 다시 루프 (LLM이 추가 도구를 호출할 수 있음)
```

**핵심:**
- `while True`: 반복 루프
- `if not response.tool_calls`: 종료 조건
- 메시지 히스토리 누적

---

### 3. LLM의 도구 선택

```python
tools = [get_weather, calculate, search_web]

질문: "서울 날씨 알려줘"
    ↓
LLM 판단: get_weather 사용
    ↓
tool_calls = [{'name': 'get_weather', 'args': {'city': '서울'}}]

질문: "123 곱하기 456은?"
    ↓
LLM 판단: calculate 사용
    ↓
tool_calls = [{'name': 'calculate', 'args': {'expression': '123 * 456'}}]
```

**LLM이 질문을 분석하여 적절한 도구 자동 선택**

---

## 동작 흐름 상세

### 예시: "서울 날씨와 뉴욕 날씨를 비교해줘"

```
[초기]
messages = [HumanMessage("서울 날씨와 뉴욕 날씨를 비교해줘")]

[루프 1차]
→ LLM 호출
→ LLM 판단: "서울 날씨가 필요하다"
→ tool_calls: [get_weather('서울')]
→ 함수 실행: "맑음, 15도"
→ messages에 추가:
  - AIMessage(tool_calls=[...])
  - ToolMessage("맑음, 15도")

[루프 2차]
messages = [
    HumanMessage("서울 날씨와 뉴욕 날씨를 비교해줘"),
    AIMessage(tool_calls=[get_weather('서울')]),
    ToolMessage("맑음, 15도")
]
→ LLM 호출
→ LLM 판단: "뉴욕 날씨도 필요하다"
→ tool_calls: [get_weather('뉴욕')]
→ 함수 실행: "흐림, 18도"
→ messages에 추가:
  - AIMessage(tool_calls=[...])
  - ToolMessage("흐림, 18도")

[루프 3차]
messages = [
    HumanMessage("서울 날씨와 뉴욕 날씨를 비교해줘"),
    AIMessage(tool_calls=[get_weather('서울')]),
    ToolMessage("맑음, 15도"),
    AIMessage(tool_calls=[get_weather('뉴욕')]),
    ToolMessage("흐림, 18도")
]
→ LLM 호출
→ LLM 판단: "모든 정보 확보, 이제 답변 생성"
→ tool_calls: None (최종 답변)
→ response.content: "서울은 맑고 15도, 뉴욕은 흐리고 18도입니다..."
→ 루프 종료
```

---

## 종료 조건

### 정상 종료

```python
if not response.tool_calls:
    # LLM이 더 이상 함수 호출 불필요하다고 판단
    print(response.content)
    break
```

### 안전 장치: 최대 반복 횟수

```python
MAX_ITERATIONS = 10

for iteration in range(MAX_ITERATIONS):
    response = llm_with_tools.invoke(messages)

    if not response.tool_calls:
        print(response.content)
        break

    # 도구 실행...
else:
    print("⚠️ 최대 반복 횟수 초과")
```

**무한 루프 방지**

---

## 여러 도구의 실전 예시

### 도구 조합 1: 날씨 + 계산

```
질문: "서울과 부산의 평균 기온은?"

1. get_weather('서울') → 15도
2. get_weather('부산') → 18도
3. calculate('(15 + 18) / 2') → 16.5
4. 최종 답변: "평균 기온은 16.5도입니다"
```

### 도구 조합 2: 검색 + 날씨

```
질문: "오늘 서울 날씨가 좋으면 추천 장소 알려줘"

1. get_weather('서울') → "맑음, 20도"
2. search_web('서울 야외 추천 장소') → "한강공원, 남산..."
3. 최종 답변: "날씨가 좋으니 한강공원이나 남산을 추천합니다"
```

### 도구 조합 3: 사용자 정보 + 날씨

```
질문: "내 위치 날씨 알려줘"

1. get_user_info() → {"location": "서울"}
2. get_weather('서울') → "맑음, 15도"
3. 최종 답변: "서울의 날씨는 맑고 15도입니다"
```

---

## Phase 4에서 구현할 것

### 예제 1: 여러 도구 정의
- 3개 이상의 도구 정의
- 각 도구의 명확한 docstring
- LLM이 도구를 구별하는 방법

### 예제 2: 수동 실행 루프
- while 루프 구현
- 종료 조건 설정
- 메시지 히스토리 관리

### 예제 3: 복잡한 시나리오
- 여러 도구를 순차적으로 사용
- 도구 결과를 다른 도구의 입력으로 사용
- 실전 활용 예시

---

## Phase 3과 Phase 4 비교 표

| 항목 | Phase 3 | Phase 4 |
|------|---------|---------|
| **도구 개수** | 1개 | 여러 개 (3개 이상) |
| **실행 방식** | 단일 호출 | 반복 루프 |
| **LLM 호출** | 2회 (tool_calls + 최종) | 여러 회 (루프) |
| **도구 선택** | 자동 (1개만 있음) | LLM이 상황에 맞게 선택 |
| **종료 조건** | 고정 (2회 후) | 동적 (tool_calls 없을 때) |
| **복잡도** | 낮음 | 높음 |
| **시나리오** | 단순 (날씨 조회) | 복잡 (비교, 계산, 조합) |

---

## 수동 루프 vs 자동 루프 (Phase 6 예고)

### Phase 4: 수동 루프

```python
# 직접 while 루프 작성
while True:
    response = llm_with_tools.invoke(messages)
    if not response.tool_calls:
        break
    # 도구 실행...
```

**장점:** 완전한 제어
**단점:** 코드가 길고 복잡

---

### Phase 6: Agent (자동 루프)

```python
# AgentExecutor가 자동으로 루프 처리
agent = create_react_agent(llm, tools)
executor = AgentExecutor(agent=agent, tools=tools)

result = executor.invoke({"input": "서울과 뉴욕 날씨 비교"})
# 자동으로 여러 도구 호출하고 최종 답변 생성
```

**장점:** 간단한 코드
**단점:** 내부 동작 파악 어려움

**Phase 4는 Phase 6의 기초!**

---

## 핵심 학습 포인트

### 1. 여러 도구 정의

```python
tools = [
    get_weather,   # 도구 1
    calculate,     # 도구 2
    search_web,    # 도구 3
]
```

**각 도구는 독립적이고 명확한 역할**

---

### 2. 수동 루프 패턴

```python
while True:
    response = llm_with_tools.invoke(messages)

    if not response.tool_calls:
        break  # 종료

    # 도구 실행 및 메시지 추가
```

**이 패턴이 Tool Use의 핵심!**

---

### 3. 메시지 히스토리 관리

```python
messages = [HumanMessage(...)]

# 루프마다 추가
messages.append(AIMessage(...))
messages.append(ToolMessage(...))
```

**전체 대화 컨텍스트 유지**

---

### 4. 종료 조건

```python
# 정상 종료
if not response.tool_calls:
    break

# 안전 장치
if iteration >= MAX_ITERATIONS:
    break
```

**무한 루프 방지 필수**

---

### 5. 도구 실행 함수

```python
def execute_tool(tool_call):
    """도구를 동적으로 실행"""
    tool_name = tool_call['name']
    tool_args = tool_call['args']

    if tool_name == 'get_weather':
        return get_weather(**tool_args)
    elif tool_name == 'calculate':
        return calculate(**tool_args)
    # ...
```

**도구 이름으로 동적 실행**

---

## Phase 4 학습 순서

1. **예제 1**: 여러 도구 정의
   - 3개 도구 정의 (날씨, 계산기, 검색)
   - 각 도구의 docstring 작성
   - LLM의 도구 선택 확인

2. **예제 2**: 수동 실행 루프
   - while 루프 구현
   - 메시지 히스토리 관리
   - 종료 조건 처리

3. **예제 3**: 복잡한 시나리오
   - 여러 도구 순차 사용
   - "서울과 뉴욕 날씨 비교"
   - "평균 기온 계산"

---

## 요약

**Phase 4 = Phase 3 + 여러 도구 + 반복 루프**

- ✅ 여러 도구를 LLM에 바인딩
- ✅ 수동 while 루프로 반복 실행
- ✅ LLM이 적절한 도구 자동 선택
- ✅ 메시지 히스토리로 컨텍스트 유지
- ✅ 종료 조건으로 무한 루프 방지

**Phase 5, 6으로 가는 중요한 기초 단계!**
