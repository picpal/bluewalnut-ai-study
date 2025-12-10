# Phase 5 - 예제 2: 병렬 파이프라인 실행 결과

## 실행 정보

- **실행 시각**: 2025-12-10
- **테스트 시나리오**: 요약 + 감정 분석 + 키워드 추출 병렬 처리
- **사용 모델**: claude-3-haiku-20240307
- **Temperature**: 0

---

## 실행 결과

### 전체 흐름

```
                 ┌→ [summarizer] → 요약
                 │
입력 (영문 기사) ┼→ [sentiment_analyzer] → 감정 분석
                 │
                 └→ [keyword_extractor] → 키워드

세 작업이 동시에 실행됨 (병렬)
```

### 성능 측정

| 실행 방식 | 소요 시간 | 비고 |
|----------|----------|------|
| **병렬 실행** | 3.13초 | RunnableParallel 사용 |
| **순차 실행** | 9.39초 | 순서대로 하나씩 실행 |
| **성능 향상** | **3.00배** | 병렬 실행이 약 3배 빠름 |

### 실행 결과 상세

#### 📝 요약 결과
```
인공지능(AI)은 우리의 삶과 업무 방식을 혁신하고 있습니다. AI 기술은 다양한 분야에
통합되어 효율성과 의사결정 프로세스를 향상시키고 있습니다. 하지만 프라이버시와 일자리
감소와 같은 윤리적 우려가 전 세계적으로 논의되고 있으며, 인류 전체에 이익이 되도록
AI를 책임감 있게 개발하는 것이 중요합니다.
```

#### 😊 감정 분석 결과
```
이 기사의 전체적인 감정은 중립적입니다.

기사는 AI 기술이 다양한 분야에서 효율성과 의사결정 프로세스를 향상시키고 있다는
긍정적인 측면을 언급하고 있습니다. 하지만 동시에 AI에 대한 윤리적 우려, 즉 프라이버시
침해와 일자리 감소 문제 등도 지적하고 있습니다.

전반적으로 AI 기술의 발전과 그에 따른 긍정적인 영향과 부정적인 우려를 균형 있게
다루고 있어 중립적인 톤을 유지하고 있습니다.
```

#### 🔑 키워드 추출 결과
```
Artificial Intelligence, Machine Learning, Ethical Concerns
```

---

## RunnableParallel 분석

### 1. RunnableParallel 구조

```python
parallel_workflow = RunnableParallel(
    summary=summarizer,
    sentiment=sentiment_analyzer,
    keywords=keyword_extractor
)

result = parallel_workflow.invoke({"article": article})
```

**출력 형식:**
```python
{
    "summary": "...",
    "sentiment": "...",
    "keywords": "..."
}
```

### 2. 병렬 실행의 장점

#### ⚡ 성능 향상
- **순차 실행**: 9.39초 (3개 작업을 순서대로)
- **병렬 실행**: 3.13초 (3개 작업을 동시에)
- **성능 향상**: 3.00배 빠름

#### 🎯 LLM API 호출 최적화
```
순차 실행:
  요약 (2.0초) → 감정 (2.5초) → 키워드 (1.5초) = 총 6초

병렬 실행:
  요약 (2.0초) ┐
  감정 (2.5초) ┼→ 가장 긴 작업(2.5초)만큼 소요
  키워드 (1.5초) ┘
```

### 3. 후처리 체인 추가

```python
# 후처리 함수
def format_analysis_result(result: dict) -> str:
    return f"""
    요약: {result['summary']}
    감정: {result['sentiment']}
    키워드: {result['keywords']}
    """

# 전체 워크플로우
complete_workflow = parallel_workflow | RunnableLambda(format_analysis_result)
```

**특징:**
- 병렬 결과(딕셔너리)를 다음 단계로 전달
- 파이프 연산자로 후처리 체인 연결
- 유연한 워크플로우 구성

---

## 핵심 학습 포인트

### 1. 독립적인 작업의 병렬화

**독립성 판단 기준:**
```
✅ 병렬 가능:
- 요약: 원문만 필요
- 감정 분석: 원문만 필요
- 키워드: 원문만 필요
→ 세 작업 모두 서로의 결과를 필요로 하지 않음

❌ 병렬 불가:
- 요약 → 번역 → 키워드
→ 각 단계가 이전 단계의 결과 필요
```

### 2. RunnableParallel의 동작 원리

```python
# 1. 모든 작업에 같은 입력 전달
input = {"article": article}

# 2. 각 작업이 독립적으로 실행
summary_task = summarizer.invoke(input)      # 병렬로
sentiment_task = sentiment_analyzer.invoke(input)  # 동시에
keywords_task = keyword_extractor.invoke(input)    # 실행

# 3. 모든 작업 완료 후 결과를 딕셔너리로 반환
result = {
    "summary": summary_task,
    "sentiment": sentiment_task,
    "keywords": keywords_task
}
```

### 3. 성능 향상 분석

#### 이론적 최대 성능 향상
```
N개의 독립적인 작업
각 작업 소요 시간: T1, T2, ..., TN

순차 실행 시간: T1 + T2 + ... + TN
병렬 실행 시간: max(T1, T2, ..., TN)

최대 성능 향상: (T1 + T2 + ... + TN) / max(T1, T2, ..., TN)
```

#### 실제 측정 결과
```
3개 작업 (요약, 감정, 키워드)

순차: 9.39초
병렬: 3.13초

성능 향상: 9.39 / 3.13 = 3.00배

→ 거의 이론적 최대값 (3배)에 근접!
```

### 4. 언제 병렬을 사용할까?

#### ✅ 병렬 사용 (RunnableParallel)

**상황 1: 독립적인 분석 작업**
```python
RunnableParallel(
    summary=summarizer,
    sentiment=sentiment_analyzer,
    keywords=keyword_extractor
)
```

**상황 2: 여러 데이터 소스 조회**
```python
RunnableParallel(
    weather=weather_api,
    news=news_api,
    stocks=stock_api
)
```

**상황 3: 다양한 번역 스타일**
```python
RunnableParallel(
    formal=formal_translator,
    casual=casual_translator,
    technical=technical_translator
)
```

#### ❌ 순차 사용 (파이프 `|`)

**상황 1: 단계별 의존성**
```python
summarizer | translator | keyword_extractor
```

**상황 2: 데이터 변환 파이프라인**
```python
cleaner | validator | processor | saver
```

---

## 실전 활용 패턴

### 패턴 1: 다중 LLM 앙상블

```python
parallel = RunnableParallel(
    gpt4=gpt4_chain,
    claude=claude_chain,
    gemini=gemini_chain
)

# 여러 LLM의 응답을 비교하여 최선의 답변 선택
```

### 패턴 2: 입력 보존 + 처리

```python
from langchain_core.runnables import RunnablePassthrough

parallel = RunnableParallel(
    original=RunnablePassthrough(),  # 원본 보존
    processed=processor               # 처리
)

# 원본과 처리 결과를 모두 유지
```

### 패턴 3: 다양한 분석 동시 수행

```python
parallel = RunnableParallel(
    summary=summarizer,
    entities=entity_extractor,
    sentiment=sentiment_analyzer,
    topics=topic_classifier,
    keywords=keyword_extractor
)

# 하나의 문서에 대한 모든 분석을 한 번에
```

---

## 병렬 vs 순차 의사결정 트리

```
작업이 독립적인가?
    │
    ├─ YES → 병렬 가능
    │         │
    │         ├─ 성능이 중요한가?
    │         │   │
    │         │   ├─ YES → RunnableParallel 사용
    │         │   └─ NO → 순차도 가능
    │         │
    │         └─ 작업 수가 많은가?
    │             │
    │             ├─ YES (3개 이상) → 병렬 효과 큼
    │             └─ NO (1-2개) → 순차도 괜찮음
    │
    └─ NO → 순차 필수 (파이프 | 사용)
```

---

## 성능 최적화 팁

### 1. 병렬 작업 수 최적화

```python
# 좋은 예: 독립적인 작업만 병렬로
parallel = RunnableParallel(
    task1=independent_task1,
    task2=independent_task2,
    task3=independent_task3
)

# 나쁜 예: 의존적인 작업을 억지로 병렬로
# (실제로는 순차 실행됨)
parallel = RunnableParallel(
    step1=step1,
    step2=step2  # step1 결과 필요 → 에러 발생
)
```

### 2. 병렬 + 순차 조합

```python
# 전처리 (순차) → 병렬 분석 → 후처리 (순차)
workflow = (
    preprocessor
    | RunnableParallel(
        analysis1=analyzer1,
        analysis2=analyzer2,
        analysis3=analyzer3
    )
    | postprocessor
)
```

### 3. 타임아웃 설정

```python
# LLM 호출에 타임아웃 설정
llm = ChatAnthropic(
    model="claude-3-haiku-20240307",
    timeout=30  # 30초 타임아웃
)

# 병렬 작업 중 하나가 실패해도 나머지는 계속 진행
```

---

## 비용 분석

### LLM API 호출 비용

**병렬 실행:**
```
3개 작업 × 1회 LLM 호출 = 3회 API 호출
소요 시간: 3.13초
```

**순차 실행:**
```
3개 작업 × 1회 LLM 호출 = 3회 API 호출
소요 시간: 9.39초
```

**결론:**
- API 호출 횟수는 동일 (비용 동일)
- 하지만 실행 시간은 3배 차이
- **시간은 돈이다**: 사용자 경험 향상, 처리량 증가

---

## 다음 단계

**예제 3: 순차 + 병렬 조합**에서는:
- 전처리 (순차) → 병렬 분석 → 통합 (순차)
- 실전에서 가장 많이 사용되는 패턴
- `RunnablePassthrough`로 원본 데이터 보존
- 복잡한 워크플로우 구성

---

## 요약

### Phase 5 예제 2의 핵심

1. **RunnableParallel**
   - 독립적인 작업을 동시에 실행
   - 각 작업에 키(key) 할당
   - 결과를 딕셔너리로 반환

2. **성능 향상**
   - 순차 대비 약 3배 빠름 (이론적 최대값)
   - LLM API 호출이 동시에 이루어짐
   - 독립적인 작업이 많을수록 효과 큼

3. **언제 사용할까?**
   - 작업이 독립적인가? → YES
   - 성능이 중요한가? → YES
   - 작업 수가 많은가? → YES
   → **병렬 실행!**

4. **실전 활용**
   - 다중 분석 동시 수행
   - 여러 데이터 소스 조회
   - 다중 LLM 앙상블

**병렬 실행은 독립적인 작업의 성능을 극대화합니다!**
