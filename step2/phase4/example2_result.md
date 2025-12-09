# Phase 4 - 예제 2: 수동 실행 루프 결과

## 실행 정보

- **실행 시각**: 2025-12-09
- **테스트 질문**: "서울과 뉴욕의 날씨를 알려주고, 두 도시의 평균 기온을 계산해줘"
- **사용 모델**: claude-3-haiku-20240307
- **Temperature**: 0

---

## 실행 결과

### 전체 흐름

```
[루프 1] LLM 호출 → get_weather('서울') → "맑음, 기온 15도"
[루프 2] LLM 호출 → get_weather('뉴욕') → "흐림, 기온 10도"
[루프 3] LLM 호출 → calculate('(15 + 10) / 2') → "12.5"
[루프 4] LLM 호출 → 최종 답변 (도구 호출 없음)
```

### 최종 답변

```
서울의 현재 날씨는 맑음이며 기온은 15도입니다.
뉴욕의 현재 날씨는 흐림이며 기온은 10도입니다.
두 도시의 평균 기온은 12.5도입니다.
```

---

## 통계

| 항목 | 값 |
|------|-----|
| **총 루프 횟수** | 4회 |
| **총 LLM 호출** | 4회 |
| **총 도구 호출** | 3회 |
| **최종 메시지 수** | 7개 |

### 도구별 사용 횟수

- `get_weather`: 2회 (서울, 뉴욕)
- `calculate`: 1회 (평균 계산)

---

## 메시지 히스토리 분석

```
[1] HumanMessage
    "서울과 뉴욕의 날씨를 알려주고, 두 도시의 평균 기온을 계산해줘"

[2] AIMessage
    tool_calls: [get_weather({'city': '서울'})]

[3] ToolMessage
    "맑음, 기온 15도"

[4] AIMessage
    tool_calls: [get_weather({'city': '뉴욕'})]

[5] ToolMessage
    "흐림, 기온 10도"

[6] AIMessage
    tool_calls: [calculate({'expression': '(15 + 10) / 2'})]

[7] ToolMessage
    "12.5"

[8회차 AIMessage는 최종 답변으로 메시지 히스토리에 추가되지 않음]
```

---

## 핵심 학습 포인트

### 1. 수동 실행 루프의 동작 원리

```python
while True:
    response = llm_with_tools.invoke(messages)

    if not response.tool_calls:
        # 최종 답변
        break

    # 도구 실행 및 메시지 추가
    for tool_call in response.tool_calls:
        result = execute_tool(tool_call)
        messages.append(ToolMessage(...))
```

**특징:**
- `while True` 무한 루프로 반복 실행
- `if not response.tool_calls` 종료 조건으로 루프 탈출
- 메시지 히스토리에 계속 추가하여 컨텍스트 유지

### 2. LLM의 순차적 도구 호출

LLM은 복잡한 질문을 분석하여 **순차적으로 필요한 도구를 호출**:

1. **1단계**: 서울 날씨 필요 → `get_weather('서울')`
2. **2단계**: 뉴욕 날씨 필요 → `get_weather('뉴욕')`
3. **3단계**: 평균 계산 필요 → `calculate('(15 + 10) / 2')`
4. **4단계**: 모든 정보 확보 → 최종 답변 생성

**중요:** LLM은 각 단계마다 이전 도구 실행 결과를 보고 다음 행동을 결정합니다.

### 3. 메시지 히스토리의 중요성

```python
messages = [HumanMessage(...)]  # 초기 1개

# 루프 1회차 후
messages = [
    HumanMessage(...),
    AIMessage(...),
    ToolMessage(...)
]  # 3개

# 루프 2회차 후
messages = [
    HumanMessage(...),
    AIMessage(...),
    ToolMessage(...),
    AIMessage(...),
    ToolMessage(...)
]  # 5개

# 루프 3회차 후 → 7개
```

**메시지 히스토리가 계속 누적되면서:**
- LLM이 전체 대화 컨텍스트 유지
- 이전 도구 실행 결과 참조 가능
- 다음 단계 결정에 활용

### 4. 종료 조건 처리

```python
if not response.tool_calls:
    print(response.content)  # 최종 답변
    break
```

**LLM이 스스로 판단하는 종료 조건:**
- 모든 필요한 정보를 수집했을 때
- 더 이상 도구 호출이 필요 없을 때
- `tool_calls`가 없는 응답 반환

### 5. 안전 장치: 최대 반복 횟수

```python
MAX_ITERATIONS = 10

for iteration in range(MAX_ITERATIONS):
    # 루프 실행
else:
    print("⚠️ 최대 반복 횟수 초과")
```

**무한 루프 방지:**
- LLM이 계속 도구를 호출할 경우를 대비
- 최대 반복 횟수 설정으로 안전성 확보

---

## Phase 3 vs Phase 4 비교

### Phase 3: 단일 함수 Function Calling

```
질문: "서울 날씨 알려줘"

[호출 1] LLM → tool_calls: [get_weather('서울')]
          도구 실행 → "맑음, 15도"
[호출 2] LLM → 최종 답변
```

**특징:**
- 함수 1개만 사용
- LLM 호출 2회 고정
- 단순한 질문만 처리

### Phase 4: 여러 함수 + 수동 루프

```
질문: "서울과 뉴욕의 날씨를 알려주고, 두 도시의 평균 기온을 계산해줘"

[루프 1] LLM → get_weather('서울')
[루프 2] LLM → get_weather('뉴욕')
[루프 3] LLM → calculate('(15 + 10) / 2')
[루프 4] LLM → 최종 답변
```

**특징:**
- 여러 함수 사용 (2개)
- LLM 호출 4회 (동적)
- 복잡한 질문 처리 가능

---

## 수동 루프 패턴의 장단점

### 장점

1. **완전한 제어**
   - 각 단계마다 개발자가 직접 제어 가능
   - 디버깅 용이 (각 루프마다 로그 출력)
   - 예외 처리 자유롭게 추가 가능

2. **투명한 실행 흐름**
   - 어떤 도구가 언제 호출되는지 명확
   - 메시지 히스토리 직접 관리
   - LLM의 판단 과정 확인 가능

3. **커스터마이징 가능**
   - 특정 조건에서 루프 중단
   - 도구 실행 전/후 추가 로직 삽입
   - 메시지 히스토리 필터링 가능

### 단점

1. **코드 복잡도**
   - 수동으로 while 루프 작성 필요
   - 메시지 히스토리 관리 부담
   - 종료 조건 직접 구현

2. **보일러플레이트 코드**
   - 매번 비슷한 패턴 반복
   - 도구 실행 로직 중복

3. **에러 처리 부담**
   - 무한 루프 방지 필요
   - 도구 실행 실패 처리
   - 예외 상황 대응

**Phase 6 (Agent)에서는 이러한 수동 루프를 AgentExecutor가 자동으로 처리합니다.**

---

## LLM의 지능적 판단

### 1. 작업 분해 (Task Decomposition)

질문: "서울과 뉴욕의 날씨를 알려주고, 두 도시의 평균 기온을 계산해줘"

**LLM의 분석:**
1. 서울 날씨 필요 → get_weather('서울')
2. 뉴욕 날씨 필요 → get_weather('뉴욕')
3. 두 기온값 확보 → calculate('(15 + 10) / 2')
4. 모든 정보 확보 → 최종 답변 생성

### 2. 순차적 실행

**왜 한 번에 모든 도구를 호출하지 않는가?**

- LLM은 각 단계마다 결과를 확인하고 다음 행동 결정
- 이전 도구 실행 결과가 다음 도구의 입력이 될 수 있음
- 예: 날씨 조회 실패 시 계산 단계로 넘어가지 않음

### 3. 컨텍스트 활용

```
[루프 3]
messages = [
    HumanMessage("...평균 기온을 계산해줘"),
    ToolMessage("맑음, 기온 15도"),  # 서울
    ToolMessage("흐림, 기온 10도"),  # 뉴욕
]

LLM 판단: "서울 15도, 뉴욕 10도 → (15 + 10) / 2"
```

**LLM은 메시지 히스토리를 보고:**
- 서울 기온 15도 추출
- 뉴욕 기온 10도 추출
- 평균 계산식 `(15 + 10) / 2` 생성

---

## 개선 아이디어

### 1. 도구 실행 시간 측정

```python
import time

for tool_call in response.tool_calls:
    start_time = time.time()
    result = execute_tool(tool_call)
    elapsed = time.time() - start_time
    print(f"⏱️ {tool_name} 실행 시간: {elapsed:.2f}초")
```

### 2. 도구 실행 결과 검증

```python
if tool_name == "calculate":
    result = calculate(**tool_args)
    if "오류" in result:
        print(f"⚠️ 계산 오류 발생: {result}")
        # 재시도 또는 에러 처리
```

### 3. 중간 결과 저장

```python
tool_results = []

for tool_call in response.tool_calls:
    result = execute_tool(tool_call)
    tool_results.append({
        'tool': tool_name,
        'args': tool_args,
        'result': result
    })
```

### 4. 도구 호출 히스토리 시각화

```python
print("\n📊 도구 호출 히스토리:")
print("┌─────┬──────────────┬────────────────┬──────────────┐")
print("│ 순서│ 도구         │ 매개변수       │ 결과         │")
print("├─────┼──────────────┼────────────────┼──────────────┤")
for i, tc in enumerate(tool_calls_history, 1):
    print(f"│ {i:2d}  │ {tc['tool']:12s} │ {tc['args']:14s} │ {tc['result']:12s} │")
print("└─────┴──────────────┴────────────────┴──────────────┘")
```

---

## 다음 단계

**예제 3: 복잡한 시나리오**에서는:

1. **시나리오 1**: 두 도시 날씨 비교
   - 여러 도구를 조합하여 비교 분석

2. **시나리오 2**: 날씨 + 계산
   - 세 도시 날씨 조회 후 평균 계산

3. **시나리오 3**: 날씨 + 검색
   - 날씨 확인 후 조건부 검색

**더 복잡한 도구 조합과 LLM의 자율적 판단을 경험합니다.**

---

## 요약

### Phase 4 예제 2의 핵심

1. **수동 while 루프로 도구 반복 실행**
   - `while True` 패턴
   - `if not response.tool_calls` 종료 조건

2. **메시지 히스토리 관리**
   - 대화 컨텍스트 유지
   - 이전 결과 참조 가능

3. **LLM의 순차적 도구 호출**
   - 작업을 단계별로 분해
   - 각 단계마다 결과 확인 후 다음 행동 결정

4. **투명한 실행 흐름**
   - 각 루프마다 무슨 일이 일어나는지 명확
   - 디버깅 및 모니터링 용이

5. **안전 장치**
   - 최대 반복 횟수로 무한 루프 방지

**Phase 6 (Agent)의 자동 루프를 이해하기 위한 필수 기초!**
