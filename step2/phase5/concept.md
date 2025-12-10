# Phase 5: Workflow — LCEL 기반 다단계 파이프라인

## Phase 5란?

**여러 단계를 체인으로 연결하여 복잡한 워크플로우를 구성하는 단계**

---

## Phase 4 vs Phase 5

### Phase 4: Tool Use — 수동 실행 루프

```python
# 수동 while 루프로 도구 반복 호출
while True:
    response = llm_with_tools.invoke(messages)

    if not response.tool_calls:
        break

    for tool_call in response.tool_calls:
        result = execute_tool(tool_call)
        messages.append(ToolMessage(...))
```

**특징:**
- ✅ LLM이 도구 선택
- ✅ 수동 루프로 반복 제어
- ✅ 도구 실행 결과를 다시 LLM에 전달

**한계:**
- ❌ 복잡한 다단계 처리 어려움
- ❌ 각 단계의 출력을 다음 단계의 입력으로 연결하는 패턴이 명시적이지 않음
- ❌ 병렬 처리 어려움

---

### Phase 5: Workflow — LCEL 파이프라인

```python
# LCEL로 여러 단계 체인 구성
workflow = (
    summarizer          # 1단계: 요약
    | translator        # 2단계: 번역
    | keyword_extractor # 3단계: 키워드 추출
)

result = workflow.invoke(long_article)
```

**특징:**
- ✅ 명시적인 단계 체인
- ✅ 각 단계의 출력이 자동으로 다음 단계의 입력
- ✅ 병렬 실행 지원 (`RunnableParallel`)
- ✅ 코드가 간결하고 읽기 쉬움

---

## 왜 Phase 5가 필요한가?

### Phase 4의 한계 예시

```
작업: "긴 영문 기사를 요약하고, 한글로 번역한 후, 핵심 키워드 3개를 추출해줘"

Phase 4 방식:
1. LLM 호출 → "요약해줘"
2. 요약 결과 받음
3. LLM 호출 → "번역해줘" + 요약 결과
4. 번역 결과 받음
5. LLM 호출 → "키워드 추출해줘" + 번역 결과
6. 최종 결과

문제점:
- 각 단계를 명시적으로 호출해야 함
- 중간 결과를 수동으로 다음 단계에 전달
- 코드가 길고 반복적
```

---

### Phase 5로 해결

```
Phase 5 방식:
workflow = summarizer | translator | keyword_extractor

result = workflow.invoke(long_article)

장점:
✅ 한 줄로 전체 파이프라인 정의
✅ 각 단계의 출력이 자동으로 다음 단계의 입력
✅ 읽기 쉽고 유지보수 용이
```

---

## 핵심 개념

### 1. LCEL (LangChain Expression Language)

```python
# LCEL의 파이프 연산자 |
chain = step1 | step2 | step3

# 실행
result = chain.invoke(input_data)
```

**LCEL의 장점:**
- 간결한 문법
- 자동 데이터 전달
- 조합 가능성 (composability)

---

### 2. Runnable 인터페이스

**LangChain의 모든 주요 컴포넌트는 Runnable 인터페이스 구현:**

```python
# 모두 Runnable
- PromptTemplate
- ChatModel (LLM)
- OutputParser
- RunnableSequence
- RunnableParallel
- RunnableLambda (커스텀 함수)
```

**Runnable의 핵심 메서드:**
- `invoke(input)`: 단일 입력 처리
- `batch(inputs)`: 여러 입력 배치 처리
- `stream(input)`: 스트리밍 출력

---

### 3. RunnableSequence (순차 실행)

```python
# 명시적 생성
from langchain_core.runnables import RunnableSequence

sequence = RunnableSequence(
    first=summarizer,
    middle=[translator],
    last=keyword_extractor
)

# 파이프 연산자로 생성 (더 일반적)
sequence = summarizer | translator | keyword_extractor
```

**동작 방식:**
```
입력 → [단계1] → 출력1 → [단계2] → 출력2 → [단계3] → 최종 출력
```

---

### 4. RunnableParallel (병렬 실행)

```python
from langchain_core.runnables import RunnableParallel

# 여러 작업을 동시에 실행
parallel = RunnableParallel(
    summary=summarizer,
    sentiment=sentiment_analyzer,
    keywords=keyword_extractor
)

result = parallel.invoke(article)
# {
#   "summary": "요약 결과...",
#   "sentiment": "긍정적",
#   "keywords": ["AI", "기술", "미래"]
# }
```

**동작 방식:**
```
         ┌→ [단계1: 요약] → 출력1
입력 ----┼→ [단계2: 감정] → 출력2
         └→ [단계3: 키워드] → 출력3

최종 출력: {
    "summary": 출력1,
    "sentiment": 출력2,
    "keywords": 출력3
}
```

---

### 5. RunnableLambda (커스텀 함수)

```python
from langchain_core.runnables import RunnableLambda

# 일반 Python 함수를 Runnable로 변환
def extract_first_line(text: str) -> str:
    return text.split('\n')[0]

extract_runnable = RunnableLambda(extract_first_line)

# 체인에 포함
chain = llm | extract_runnable
```

**용도:**
- 데이터 전처리
- 중간 결과 변환
- 커스텀 로직 삽입

---

## 동작 흐름 상세

### 예시: 영문 기사 → 요약 → 번역 → 키워드

```python
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser

# 각 단계 정의
summarizer = (
    PromptTemplate.from_template("다음 기사를 3문장으로 요약:\n\n{article}")
    | ChatOpenAI(model="gpt-4o-mini")
    | StrOutputParser()
)

translator = (
    PromptTemplate.from_template("다음 영문을 한글로 번역:\n\n{text}")
    | ChatOpenAI(model="gpt-4o-mini")
    | StrOutputParser()
)

keyword_extractor = (
    PromptTemplate.from_template("다음 텍스트에서 핵심 키워드 3개 추출:\n\n{text}")
    | ChatOpenAI(model="gpt-4o-mini")
    | StrOutputParser()
)
```

**문제:** 각 단계의 입력 키가 다름!
- summarizer: `{article}`
- translator: `{text}`
- keyword_extractor: `{text}`

**해결:** RunnableLambda로 키 매핑

```python
def map_to_text(output: str) -> dict:
    return {"text": output}

# 전체 워크플로우
workflow = (
    summarizer                          # 입력: {article} → 출력: str
    | RunnableLambda(map_to_text)       # 입력: str → 출력: {text: str}
    | translator                        # 입력: {text} → 출력: str
    | RunnableLambda(map_to_text)       # 입력: str → 출력: {text: str}
    | keyword_extractor                 # 입력: {text} → 출력: str
)

# 실행
article = "Long English article..."
result = workflow.invoke({"article": article})
```

---

## 순차 vs 병렬 실행

### 순차 실행 (RunnableSequence)

```python
# 단계가 서로 의존적일 때
sequence = step1 | step2 | step3

# step2는 step1의 출력 필요
# step3는 step2의 출력 필요
```

**사용 사례:**
- 번역 → 요약 (번역 결과 필요)
- 데이터 수집 → 분석 (데이터 필요)
- 요약 → 키워드 추출 (요약 결과 필요)

---

### 병렬 실행 (RunnableParallel)

```python
# 단계가 독립적일 때
parallel = RunnableParallel(
    task1=step1,
    task2=step2,
    task3=step3
)

# step1, step2, step3 동시 실행
# 모두 같은 입력 받음
```

**사용 사례:**
- 동시에 여러 LLM 호출 (요약 + 감정 분석 + 키워드)
- 여러 데이터 소스 조회
- 독립적인 분석 작업

**장점:**
- ⚡ 속도 향상 (병렬 실행)
- 🎯  효율성 (한 번에 여러 작업)

---

## 순차 + 병렬 조합

```python
# 1단계: 기사 전처리 (순차)
preprocess = clean_text | normalize

# 2단계: 병렬 분석
parallel_analysis = RunnableParallel(
    summary=summarizer,
    sentiment=sentiment_analyzer,
    keywords=keyword_extractor
)

# 3단계: 결과 통합 (순차)
def format_results(results: dict) -> str:
    return f"""
    요약: {results['summary']}
    감정: {results['sentiment']}
    키워드: {results['keywords']}
    """

formatter = RunnableLambda(format_results)

# 전체 워크플로우
workflow = preprocess | parallel_analysis | formatter

# 실행
result = workflow.invoke(raw_article)
```

**흐름:**
```
입력 → [전처리] → 정제된 텍스트
                      ↓
         ┌─────────────┼─────────────┐
         ↓             ↓             ↓
    [요약]        [감정 분석]    [키워드]
         ↓             ↓             ↓
         └─────────────┼─────────────┘
                      ↓
                 [결과 통합]
                      ↓
                  최종 출력
```

---

## 상태 관리

### 문제: 중간 결과 추적

```python
# 각 단계의 중간 결과를 보고 싶을 때?
workflow = step1 | step2 | step3
result = workflow.invoke(input)

# ❌ step1, step2의 중간 결과를 볼 수 없음
```

---

### 해결 1: RunnablePassthrough

```python
from langchain_core.runnables import RunnablePassthrough

# 중간 결과를 다음 단계로 전달하면서 보존
workflow = (
    {"original": RunnablePassthrough(), "processed": step1}
    | step2
)

result = workflow.invoke(input)
# result = {
#   "original": input,
#   "processed": step1의 출력
# }
```

---

### 해결 2: RunnableLambda로 로깅

```python
def log_output(output):
    print(f"중간 결과: {output}")
    return output

workflow = (
    step1
    | RunnableLambda(log_output)
    | step2
    | RunnableLambda(log_output)
    | step3
)
```

---

### 해결 3: 딕셔너리로 상태 관리

```python
# 각 단계가 딕셔너리를 받고 반환
def step1_with_state(state: dict) -> dict:
    result = step1.invoke(state["input"])
    return {**state, "step1_result": result}

def step2_with_state(state: dict) -> dict:
    result = step2.invoke(state["step1_result"])
    return {**state, "step2_result": result}

workflow = (
    RunnableLambda(step1_with_state)
    | RunnableLambda(step2_with_state)
)

final_state = workflow.invoke({"input": data})
# {
#   "input": data,
#   "step1_result": ...,
#   "step2_result": ...
# }
```

---

## Phase 5에서 구현할 것

### 예제 1: 순차 파이프라인
- 기사 요약 → 번역 → 키워드 추출
- RunnableSequence 사용
- 키 매핑 처리

### 예제 2: 병렬 파이프라인
- 동시에 요약 + 감정 분석 + 키워드 추출
- RunnableParallel 사용
- 결과 통합

### 예제 3: 순차 + 병렬 조합
- 전처리 → 병렬 분석 → 결과 통합
- 복잡한 워크플로우
- 상태 관리

### 예제 4: 실전 시나리오
- 뉴스 기사 분석 파이프라인
- 여러 단계 조합
- 에러 처리 및 로깅

---

## Phase 4 vs Phase 5 vs Phase 6 비교

| 항목 | Phase 4 | Phase 5 | Phase 6 |
|------|---------|---------|---------|
| **핵심** | 도구 반복 호출 | 단계 체인 연결 | Agent 자율 실행 |
| **실행 방식** | 수동 while 루프 | LCEL 파이프라인 | AgentExecutor |
| **도구 선택** | LLM이 선택 | 개발자가 단계 정의 | Agent가 자율 선택 |
| **흐름 제어** | 개발자 직접 제어 | 체인으로 자동 연결 | Agent가 자율 제어 |
| **복잡도** | 중간 | 낮음 | 높음 (내부) |
| **유연성** | 높음 | 중간 | 매우 높음 |
| **사용 사례** | 도구 반복 호출 | 정해진 단계 처리 | 복잡한 자율 작업 |

---

## 핵심 학습 포인트

### 1. LCEL 파이프 연산자 `|`

```python
chain = component1 | component2 | component3
```

**왼쪽 출력이 오른쪽 입력으로 자동 전달**

---

### 2. Runnable 인터페이스

```python
# 모든 컴포넌트는 Runnable
result = runnable.invoke(input)
```

**일관된 인터페이스로 조합 가능**

---

### 3. 순차 vs 병렬

```python
# 순차
sequence = step1 | step2 | step3

# 병렬
parallel = RunnableParallel(
    task1=step1,
    task2=step2
)
```

**상황에 맞게 선택**

---

### 4. RunnableLambda

```python
custom = RunnableLambda(my_function)
chain = llm | custom | parser
```

**커스텀 로직을 체인에 삽입**

---

### 5. 상태 관리

```python
# 중간 결과 보존
workflow = (
    {"original": RunnablePassthrough(), "processed": step1}
    | step2
)
```

**필요시 중간 결과 추적**

---

## Phase 5 학습 순서

1. **예제 1**: 순차 파이프라인
   - 기사 요약 → 번역 → 키워드
   - RunnableSequence 기본

2. **예제 2**: 병렬 파이프라인
   - 동시에 여러 분석
   - RunnableParallel 활용

3. **예제 3**: 순차 + 병렬 조합
   - 복잡한 워크플로우
   - 실전 패턴

4. **예제 4**: 실전 시나리오
   - 뉴스 기사 분석
   - 에러 처리
   - 로깅 및 모니터링

---

## 요약

**Phase 5 = 명시적인 단계 체인으로 복잡한 파이프라인 구성**

- ✅ LCEL 파이프 연산자로 간결한 체인
- ✅ RunnableSequence로 순차 실행
- ✅ RunnableParallel로 병렬 실행
- ✅ RunnableLambda로 커스텀 로직
- ✅ 자동 데이터 전달 및 변환

**Phase 6 (Agent)의 기초!**
