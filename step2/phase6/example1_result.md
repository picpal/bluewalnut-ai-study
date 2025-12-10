# Phase 6 - 예제 1: 기본 Agent 생성 실행 결과

## 실행 정보

- **실행 시각**: 2025-12-10
- **테스트 시나리오**: 기본 ReAct Agent 생성 및 테스트
- **사용 모델**: claude-3-haiku-20240307
- **Temperature**: 0
- **LangChain 버전**: 0.2.16

---

## 실행 결과

### Agent 설정

```python
# 도구 정의
tools = [get_weather, calculate]

# ReAct Agent 생성
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

# AgentExecutor 설정
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    max_iterations=10,
    early_stopping_method="generate",
    handle_parsing_errors=True,
    return_intermediate_steps=True
)
```

### 테스트 결과

#### 테스트 1: 간단한 날씨 질문

**입력**: "서울의 날씨를 알려줘"

**실행 과정**:
```
> Entering new AgentExecutor chain...
Question: 서울의 날씨를 알려줘
Thought: 서울의 날씨 정보를 조회해야 합니다.
Action: get_weather
Action Input: 서울
[도구 실행] get_weather('서울') → 맑음, 기온 15도
Observation: 맑음, 기온 15도
Thought: 서울의 날씨 정보를 얻었습니다. 이 정보로 최종 답변을 할 수 있습니다.
Final Answer: 서울의 날씨는 맑음, 기온 15도입니다.
> Finished chain.
```

**결과**: ✅ 성공
- Agent가 정확히 날씨 도구를 선택하고 실행
- 적절한 최종 답변 생성

#### 테스트 2: 간단한 계산 질문

**입력**: "123 + 456을 계산해줘"

**실행 과정**:
```
> Entering new AgentExecutor chain...
Question: 123 + 456을 계산해줘
Thought: To answer this question, I need to calculate the expression "123 + 456".
Action: calculate
Action Input: 123 + 456
Observation: 579.0
Thought: I have the calculation result. I can now provide the final answer.
Final Answer: 579.0
> Finished chain.
```

**결과**: ✅ 성공
- Agent가 계산 도구를 정확히 선택
- 수학 연산 정확히 수행

#### 테스트 3: 복합 질문

**입력**: "서울과 뉴욕의 날씨를 알려주고, 두 도시의 평균 기온을 계산해줘"

**실행 과정**:
```
> Entering new AgentExecutor chain...
Question: 서울과 뉴욕의 날씨를 알려주고, 두 도시의 평균 기온을 계산해줘
Thought: To answer this question, I need to get the current weather for both Seoul and New York, and then calculate the average temperature.
Action: get_weather
Action Input: Seoul
Observation: Seoul의 날씨 정보를 찾을 수 없습니다.
Thought: I will now get the weather for New York.
Action: get_weather
Action Input: New York
Observation: New York의 날씨 정보를 찾을 수 없습니다.
```

**결과**: ❌ 부분 실패
- 도시 이름 매칭 문제 (한글 vs 영문)
- Agent가 올바른 reasoning은 했지만 데이터 부족으로 완료 실패

---

## ReAct 패턴 분석

### Agent의 사고 과정

#### 1. Thought (사고)
```
Thought: 서울의 날씨 정보를 조회해야 합니다.
```
- 현재 질문 분석
- 필요한 행동 결정
- 적절한 도구 선택

#### 2. Action (행동)
```
Action: get_weather
Action Input: 서울
```
- 선택된 도구 실행
- 적절한 파라미터 전달

#### 3. Observation (관찰)
```
Observation: 맑음, 기온 15도
```
- 도구 실행 결과 수신
- 결과 분석 및 이해

#### 4. Final Answer (최종 답변)
```
Final Answer: 서울의 날씨는 맑음, 기온 15도입니다.
```
- 목표 달성 확인
- 최종 답변 생성

### ReAct 사이클의 장점

1. **명확한 사고 과정**: 각 단계가 명시적으로 표시됨
2. **디버깅 용이**: 어느 단계에서 문제가 발생했는지 쉽게 파악
3. **자율적 의사결정**: Agent가 스스로 다음 행동 결정
4. **반복적 개선**: 목표 달성 시까지 과정 반복

---

## Phase 4와의 비교

### Phase 4 (수동 루프)
```python
# 개발자가 직접 제어
while not done:
    response = llm_with_tools.invoke(messages)
    
    if response.tool_calls:
        for tool_call in response.tool_calls:
            result = tool_call.invoke(tool_call.args)
            messages.append(ToolMessage(result, tool_call_id=tool_call.id))
    else:
        final_answer = response.content
        done = True
```

**특징**:
- 개발자가 모든 로직 직접 구현
- 메시지 히스토리 수동 관리
- 종료 조건 직접 판단
- 완전한 제어권

### Phase 6 (Agent)
```python
# Agent가 자율적으로 실행
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True
)

result = agent_executor.invoke({"input": user_query})
```

**특징**:
- Agent가 자율적으로 도구 선택 및 실행
- ReAct 패턴으로 자동 reasoning
- 메시지 히스토리 자동 관리
- 개발자는 설정만 담당

### 핵심 차이점

| 항목 | Phase 4 (수동) | Phase 6 (Agent) |
|------|----------------|-----------------|
| **자율성** | 개발자 완전 제어 | Agent 자율 판단 |
| **코드 복잡도** | 높음 (직접 구현) | 낮음 (설정만) |
| **확장성** | 제한적 (수동 수정) | 높음 (도구 추가만) |
| **디버깅** | 직접 로깅 필요 | 자동 상세 로그 |
| **안정성** | 개발자 의존적 | LangChain 검증 로직 |

---

## 발견된 문제점 및 해결 방안

### 1. 도시 이름 매칭 문제

**문제**: 한글 도시 이름("서울") vs 영문 키("Seoul")

**해결 방안**:
```python
@tool
def get_weather(city: str) -> str:
    # 도시 이름 매핑 테이블
    city_mapping = {
        "서울": "서울",
        "seoul": "서울", 
        "뉴욕": "뉴욕",
        "new york": "뉴욕",
        "뉴욕시": "뉴욕"
    }
    
    normalized_city = city_mapping.get(city.lower(), city)
    return weather_data.get(normalized_city, f"{city}의 날씨 정보를 찾을 수 없습니다.")
```

### 2. early_stopping_method 오류

**문제**: `generate` 메서드가 지원되지 않음

**해결 방안**:
```python
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    max_iterations=10,
    early_stopping_method="force"  # 또는 "iter"
)
```

### 3. ReAct 프롬프트 최적화

**개선 사항**:
- 더 명확한 지시문 추가
- 예제 포함
- 에러 처리 가이드라인 추가

---

## 성능 평가

### 실행 시간 분석

| 테스트 | 도구 호출 횟수 | 총 실행 시간 | 성공 여부 |
|--------|--------------|--------------|------------|
| 날씨 질문 | 1회 | 약 2초 | ✅ |
| 계산 질문 | 1회 | 약 1.5초 | ✅ |
| 복합 질문 | 2회 | 약 5초 | ❌ (데이터 부족) |

### Agent의 장점

1. **자율성**: 개발자 개입 없이 스스로 문제 해결
2. **확장성**: 새로운 도구 추가가 매우 쉬움
3. **관찰 가능성**: verbose 모드로 상세한 실행 과정 추적
4. **안정성**: LangChain의 검증된 로직 사용

### 개선이 필요한 부분

1. **도구 견고성**: 더 강력한 에러 처리 필요
2. **프롬프트 최적화**: 더 명확한 지시문
3. **종료 조건 개선**: 더 지능적인 종료 판단

---

## 핵심 학습 포인트

### 1. ReAct Agent의 기본 구조
- `create_react_agent()`로 Agent 생성
- `AgentExecutor`로 실행 환경 설정
- ReAct 프롬프트로 사고 과정 가이드

### 2. Agent vs 수동 루프
- Agent: 자율성, 단순성, 확장성
- 수동: 제어권, 맞춤화, 디버깅 용이성

### 3. 실전 적용 고려사항
- 도구의 견고성 확보
- 명확한 프롬프트 설계
- 적절한 종료 조건 설정
- 에러 처리 및 fallback 메커니즘

---

## 다음 단계

예제 2에서는:
- ReAct 패턴의 더 깊은 분석
- 다양한 종료 조건 테스트
- Agent의 사고 과정 최적화
- 복잡한 시나리오에서의 동작 검증

**Phase 6 예제 1의 핵심 성과**: 기본 Agent의 동작 원리 이해 및 Phase 4와의 차이점 명확히 인식