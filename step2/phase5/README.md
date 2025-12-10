# Phase 5: Workflow — LCEL 기반 다단계 파이프라인

## 개요

Phase 5에서는 **LangChain Expression Language (LCEL)**을 사용하여 복잡한 다단계 파이프라인을 구성하는 방법을 학습합니다.

---

## 학습 목표

- ✅ LCEL 파이프 연산자 (`|`)로 여러 단계 연결
- ✅ `RunnableSequence`를 통한 순차 실행
- ✅ `RunnableParallel`을 통한 병렬 실행
- ✅ 순차와 병렬을 조합한 복잡한 워크플로우 구성
- ✅ 에러 처리 및 모니터링을 포함한 프로덕션 수준 구현

---

## 파일 구조

```
phase5/
├── concept.md                    # Phase 5 핵심 개념 설명
├── example1_sequential.py        # 순차 파이프라인
├── example2_parallel.py          # 병렬 파이프라인
├── example3_combined.py          # 순차 + 병렬 조합
├── example4_real_world.py        # 실전 시나리오 (에러 처리 + 로깅)
└── README.md                     # 본 문서
```

---

## 예제 설명

### 예제 1: 순차 파이프라인 (`example1_sequential.py`)

**목표:** 기사 요약 → 번역 → 키워드 추출을 순차적으로 처리

```python
workflow = (
    summarizer                      # 1단계: 요약
    | RunnableLambda(map_to_text)   # 키 매핑
    | translator                    # 2단계: 번역
    | RunnableLambda(map_to_text)   # 키 매핑
    | keyword_extractor             # 3단계: 키워드 추출
)

result = workflow.invoke({"article": article})
```

**핵심 포인트:**
- LCEL 파이프 연산자 (`|`)로 단계 연결
- 각 단계의 출력이 자동으로 다음 단계의 입력
- `RunnableLambda`로 키 매핑 처리

---

### 예제 2: 병렬 파이프라인 (`example2_parallel.py`)

**목표:** 요약 + 감정 분석 + 키워드 추출을 동시에 처리

```python
parallel_workflow = RunnableParallel(
    summary=summarizer,
    sentiment=sentiment_analyzer,
    keywords=keyword_extractor
)

result = parallel_workflow.invoke({"article": article})
# {
#   "summary": "...",
#   "sentiment": "...",
#   "keywords": "..."
# }
```

**핵심 포인트:**
- `RunnableParallel`로 독립적인 작업 동시 실행
- 순차 실행 대비 약 3배 빠른 성능
- 각 작업이 같은 입력을 받고 독립적으로 실행

---

### 예제 3: 순차 + 병렬 조합 (`example3_combined.py`)

**목표:** 전처리 → 병렬 분석 → 결과 통합 패턴

```python
complete_workflow = (
    preprocessing       # 순차: 전처리
    | parallel_analysis # 병렬: 다중 분석
    | integration       # 순차: 결과 통합
)

result = complete_workflow.invoke({"article": article})
```

**흐름:**
```
    입력
     ↓
    [전처리] (순차)
     ↓
              ┌→ [요약]
              ├→ [감정]
    [병렬 분석] ├→ [주제]
              ├→ [키워드]
              └→ [메타데이터 보존]
     ↓
    [결과 통합] (순차)
     ↓
    출력
```

**핵심 포인트:**
- 실전에서 가장 많이 사용되는 패턴
- `RunnablePassthrough`로 원본 데이터 보존
- 순차와 병렬의 장점을 모두 활용

---

### 예제 4: 실전 시나리오 (`example4_real_world.py`)

**목표:** 프로덕션 수준의 뉴스 기사 분석 시스템

```python
production_workflow = (
    preprocessing       # 검증 + 정제 (재시도 3회)
    | parallel_analysis # 5개 분석 동시 실행 (에러 처리)
    | integration       # 결과 통합 + 품질 검증
)
```

**추가 기능:**
- ✅ **재시도 로직:** 최대 3회 재시도 (exponential backoff)
- ✅ **에러 처리:** 부분 실패 허용 (일부 분석 실패해도 계속 진행)
- ✅ **로깅:** 단계별 상세 로깅
- ✅ **모니터링:** 실행 시간, 성공률, 에러 추적
- ✅ **데이터 검증:** 입력 검증 및 결과 품질 체크

**핵심 포인트:**
- 실제 서비스에서 사용 가능한 안정성
- 관찰 가능성 (Observability) 확보
- 에러 상황에 대한 대응 전략

---

## 실행 방법

### 1. API 키 설정

각 예제 파일에서 API 키를 설정하세요:

```python
os.environ["OPENAI_API_KEY"] = "your-api-key-here"
```

### 2. 예제 실행

```bash
# 예제 1 실행
python phase5/example1_sequential.py

# 예제 2 실행
python phase5/example2_parallel.py

# 예제 3 실행
python phase5/example3_combined.py

# 예제 4 실행
python phase5/example4_real_world.py
```

---

## 핵심 개념 정리

### 1. LCEL (LangChain Expression Language)

```python
# 파이프 연산자로 체인 연결
chain = step1 | step2 | step3

# 왼쪽 출력이 오른쪽 입력으로 자동 전달
result = chain.invoke(input)
```

### 2. Runnable 인터페이스

모든 LangChain 컴포넌트는 `Runnable` 인터페이스를 구현:
- `PromptTemplate`
- `ChatModel`
- `OutputParser`
- `RunnableSequence`
- `RunnableParallel`
- `RunnableLambda`

**주요 메서드:**
- `invoke(input)`: 단일 입력 처리
- `batch(inputs)`: 여러 입력 배치 처리
- `stream(input)`: 스트리밍 출력

### 3. RunnableSequence (순차 실행)

```python
# 파이프 연산자로 생성 (권장)
sequence = step1 | step2 | step3

# 명시적 생성
from langchain_core.runnables import RunnableSequence
sequence = RunnableSequence(first=step1, middle=[step2], last=step3)
```

### 4. RunnableParallel (병렬 실행)

```python
from langchain_core.runnables import RunnableParallel

parallel = RunnableParallel(
    task1=step1,
    task2=step2,
    task3=step3
)

result = parallel.invoke(input)
# {"task1": result1, "task2": result2, "task3": result3}
```

### 5. RunnableLambda (커스텀 함수)

```python
from langchain_core.runnables import RunnableLambda

def my_function(x):
    return x.upper()

custom = RunnableLambda(my_function)
chain = llm | custom | parser
```

### 6. RunnablePassthrough (데이터 보존)

```python
from langchain_core.runnables import RunnablePassthrough

workflow = RunnableParallel(
    original=RunnablePassthrough(),  # 원본 보존
    processed=processor              # 처리
)
```

---

## 순차 vs 병렬 선택 기준

### ✅ 순차 사용 (RunnableSequence / 파이프 `|`)

**사용 시기:**
- 각 단계가 이전 단계의 결과를 필요로 할 때
- 순서가 중요할 때

**예시:**
- 요약 → 번역 → 키워드 (번역 전 요약 필요)
- 데이터 수집 → 분석 → 보고서 (순서 필수)

### ✅ 병렬 사용 (RunnableParallel)

**사용 시기:**
- 각 작업이 독립적일 때
- 모두 같은 입력을 받을 때
- 성능 향상이 필요할 때

**예시:**
- 요약 + 감정 + 키워드 (모두 독립적)
- 여러 데이터 소스 조회 (동시 호출)

---

## Phase 4 vs Phase 5 비교

### Phase 4: 수동 루프

```python
# 수동으로 while 루프 작성
while True:
    response = llm_with_tools.invoke(messages)

    if not response.tool_calls:
        break

    for tool_call in response.tool_calls:
        result = execute_tool(tool_call)
        messages.append(ToolMessage(...))
```

**특징:**
- ✅ 완전한 제어
- ❌ 코드가 길고 복잡
- ❌ 명시적인 파이프라인 구조 없음

---

### Phase 5: LCEL 파이프라인

```python
# 명시적인 체인 구성
workflow = step1 | step2 | step3
result = workflow.invoke(input)
```

**특징:**
- ✅ 간결한 코드
- ✅ 명시적인 단계 구조
- ✅ 자동 데이터 전달
- ✅ 병렬 실행 지원

---

## 실전 활용 패턴

### 패턴 1: 데이터 수집 → 분석 → 보고서

```python
workflow = (
    data_collector
    | RunnableParallel(
        stats=statistics,
        viz=visualization,
        insights=insight_generator
    )
    | report_generator
)
```

### 패턴 2: 검증 → 처리 → 저장

```python
workflow = (
    validator
    | RunnableParallel(
        process_a=processor_a,
        process_b=processor_b
    )
    | saver
)
```

### 패턴 3: 전처리 → 다중 모델 → 앙상블

```python
workflow = (
    preprocessor
    | RunnableParallel(
        gpt4=gpt4_chain,
        claude=claude_chain,
        gemini=gemini_chain
    )
    | ensemble
)
```

---

## 프로덕션 체크리스트

Phase 5를 프로덕션에 적용할 때 확인 사항:

- [ ] **에러 처리:** 재시도 로직 및 Fallback 구현
- [ ] **로깅:** 단계별 상세 로깅
- [ ] **모니터링:** 실행 시간 및 성공률 추적
- [ ] **데이터 검증:** 입력/출력 검증
- [ ] **테스트:** 정상 케이스 + 에러 케이스 테스트
- [ ] **문서화:** 워크플로우 구조 및 각 단계 설명
- [ ] **성능 최적화:** 병렬 실행 최대화
- [ ] **비용 관리:** LLM API 호출 최적화

---

## 다음 단계

### Phase 6: Agent

Phase 5에서 배운 명시적 워크플로우를 기반으로, Phase 6에서는 **Agent**를 학습합니다.

**Phase 5 vs Phase 6:**

| Phase 5 (Workflow) | Phase 6 (Agent) |
|-------------------|-----------------|
| 개발자가 단계 정의 | Agent가 자율 판단 |
| 명시적 파이프라인 | 동적 도구 선택 |
| 정해진 순서 | 상황에 따라 변경 |
| 예측 가능 | 자율적 |

**Phase 6 주요 내용:**
- `AgentExecutor`로 자율 실행
- ReAct (Reasoning + Acting) 패턴
- 도구 자동 선택 및 반복 실행
- Agent가 스스로 작업 완료 판단

---

## 요약

**Phase 5의 핵심:**

1. **LCEL 파이프 연산자 (`|`)**
   - 간결한 체인 구성
   - 자동 데이터 전달

2. **순차 vs 병렬**
   - 의존성 있으면 순차
   - 독립적이면 병렬

3. **실전 패턴**
   - 전처리 → 병렬 분석 → 통합
   - 에러 처리 + 로깅 + 모니터링

4. **프로덕션 레디**
   - 안정성 확보
   - 관찰 가능성 확보

**Phase 6에서 만나요! 🚀**

---

## 참고 자료

- [LangChain LCEL 공식 문서](https://python.langchain.com/docs/expression_language/)
- [Runnable 인터페이스](https://python.langchain.com/docs/expression_language/interface/)
- [RunnableParallel](https://python.langchain.com/docs/expression_language/primitives/parallel/)
- [RunnableLambda](https://python.langchain.com/docs/expression_language/primitives/lambda/)
