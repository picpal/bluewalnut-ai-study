# Phase 5 - 예제 1: 순차 파이프라인 실행 결과

## 실행 정보

- **실행 시각**: 2025-12-10
- **테스트 시나리오**: 영문 기사 → 요약 → 번역 → 키워드 추출
- **사용 모델**: claude-3-haiku-20240307
- **Temperature**: 0

---

## 실행 결과

### 전체 흐름

```
입력: 영문 기사 (AI에 관한 기사)
  ↓
[summarizer] → 3문장 요약 (영문)
  ↓
[map_to_text] → 키 매핑 (str → {text: str})
  ↓
[translator] → 한글 번역
  ↓
[map_to_text] → 키 매핑 (str → {text: str})
  ↓
[keyword_extractor] → 핵심 키워드 3개 추출
  ↓
최종 결과: "인공지능, 윤리적 우려, 책임감 있는 개발"
```

### 입력 기사 (원문)

```
Artificial Intelligence (AI) is revolutionizing the way we live and work.
From healthcare to finance, AI technologies are being integrated into various
sectors, enhancing efficiency and decision-making processes. Machine learning
algorithms can now analyze vast amounts of data in seconds, identifying patterns
that would take humans years to discover. However, ethical concerns about AI,
such as privacy and job displacement, continue to be debated by experts worldwide.
As we move forward, it is crucial to develop AI responsibly, ensuring it benefits
humanity as a whole.
```

### 1단계: 요약 (Summarizer)

**출력:**
```
인공지능(AI)은 우리의 삶과 업무 방식을 혁신하고 있습니다. AI 기술은 다양한 분야에
통합되어 효율성과 의사결정 프로세스를 향상시키고 있습니다. 하지만 프라이버시와 일자리
감소와 같은 윤리적 우려가 전 세계적으로 논의되고 있으며, 인류 전체에 이익이 되도록
AI를 책임감 있게 개발하는 것이 중요합니다.
```

**특이사항:**
- LLM이 영문 입력을 받고 한글로 요약을 출력함
- 프롬프트는 영문 요약을 요청했지만, Claude가 한글로 응답
- 3문장으로 잘 요약됨

### 2단계: 번역 (Translator)

**입력:**
```
인공지능(AI)은 우리의 삶과 업무 방식을 혁신하고 있습니다. AI 기술은 다양한 분야에
통합되어 효율성과 의사결정 프로세스를 향상시키고 있습니다. 하지만 프라이버시와 일자리
감소와 같은 윤리적 우려가 전 세계적으로 논의되고 있으며, 인류 전체에 이익이 되도록
AI를 책임감 있게 개발하는 것이 중요합니다.
```

**출력:**
```
인공지능(AI)은 우리의 삶과 업무 방식을 혁신하고 있습니다. AI 기술은 다양한 분야에
통합되어 효율성과 의사결정 프로세스를 향상시키고 있습니다. 하지만 프라이버시와 일자리
감소와 같은 윤리적 우려가 전 세계적으로 논의되고 있으며, 인류 전체에 이익이 되도록
AI를 책임감 있게 개발하는 것이 중요합니다.
```

**특이사항:**
- 입력이 이미 한글이므로 출력이 동일함
- LLM이 이미 한글임을 인식하고 그대로 반환

### 3단계: 키워드 추출 (Keyword Extractor)

**출력:**
```
인공지능, 윤리적 우려, 책임감 있는 개발
```

**분석:**
- 3개의 키워드를 정확히 추출
- 쉼표로 구분됨
- 기사의 핵심 내용을 잘 반영

### 최종 결과

```
인공지능, 윤리적 우려, 책임감 있는 개발
```

---

## 워크플로우 분석

### 1. LCEL 파이프 연산자의 위력

**코드:**
```python
workflow = (
    summarizer
    | RunnableLambda(map_to_text)
    | translator
    | RunnableLambda(map_to_text)
    | keyword_extractor
)

result = workflow.invoke({"article": article})
```

**특징:**
- 5개의 단계를 파이프 연산자 `|`로 간결하게 연결
- 각 단계의 출력이 자동으로 다음 단계의 입력으로 전달
- 명시적이고 읽기 쉬운 구조

### 2. 키 매핑의 필요성

**문제:**
```python
# summarizer는 {article}을 입력으로 받음
PromptTemplate.from_template("...{article}...")

# translator는 {text}를 입력으로 받음
PromptTemplate.from_template("...{text}...")

# 하지만 summarizer의 출력은 단순 문자열 (str)
```

**해결:**
```python
def map_to_text(output: str) -> dict:
    return {"text": output}

# str → {"text": str} 변환
workflow = summarizer | RunnableLambda(map_to_text) | translator
```

**핵심:**
- `RunnableLambda`로 커스텀 함수를 체인에 삽입
- 데이터 형식 변환으로 단계 간 호환성 확보

### 💡 왜 입력 키를 통일하지 않았는가?

#### 질문: "처음부터 모든 프롬프트가 `{text}`를 사용하면 안 되나요?"

**답변: 맞습니다! 입력 키를 통일하는 것이 훨씬 더 좋은 설계입니다.**

#### 예제에서 일부러 다르게 만든 3가지 이유

##### 1️⃣ 실전 상황 시뮬레이션

실무에서는 종종 이런 상황이 발생합니다:

```python
# 다른 팀이 만든 레거시 체인
legacy_summarizer = PromptTemplate.from_template("...{article}...")

# 우리가 만든 새로운 체인
our_translator = PromptTemplate.from_template("...{text}...")

# 통합해야 하는데 키가 달라서 문제!
# → RunnableLambda로 해결하는 방법을 배워야 함
```

##### 2️⃣ RunnableLambda 학습

키 매핑은 `RunnableLambda`의 중요한 사용 사례:

```python
def map_to_text(output: str) -> dict:
    return {"text": output}

# 데이터 형식 변환 패턴 학습
chain = step1 | RunnableLambda(map_to_text) | step2
```

**활용 사례:**
- 외부 라이브러리 통합
- 레거시 코드 재사용
- 서로 다른 API 형식 변환

##### 3️⃣ 데이터 흐름 이해

```
{article} → [summarizer] → str → [map_to_text] → {text: str} → [translator] → str
```

이런 변환 과정을 명시적으로 보여줌으로써 데이터가 어떻게 흐르는지 이해할 수 있습니다.

#### ✅ 실전 권장 방법

**베스트 프랙티스: 입력 키 통일**

```python
# 모든 프롬프트에 동일한 키 사용
summarizer = PromptTemplate.from_template("...{text}...")
translator = PromptTemplate.from_template("...{text}...")
keyword_extractor = PromptTemplate.from_template("...{text}...")

# 하지만 여전히 출력(str)을 다음 입력(dict)으로 변환 필요
workflow = (
    summarizer
    | RunnableLambda(lambda x: {"text": x})
    | translator
    | RunnableLambda(lambda x: {"text": x})
    | keyword_extractor
)

# 실행
result = workflow.invoke({"text": article})
```

**완전히 단순화된 버전:**

```python
# 만약 각 단계가 딕셔너리를 입력/출력한다면
workflow = summarizer | translator | keyword_extractor

# 매우 간단!
```

#### 실전 가이드라인

| 상황 | 추천 방법 |
|------|----------|
| **새 프로젝트** | 처음부터 입력 키 통일 (`{text}`) |
| **레거시 통합** | RunnableLambda로 키 매핑 |
| **외부 라이브러리** | RunnableLambda로 형식 변환 |
| **팀 컨벤션** | 팀 전체가 동일한 키 이름 사용 |

#### 교훈

> **"예제는 학습 목적으로 복잡하게 만들었지만, 실전에서는 가능한 한 단순하게 설계하세요."**

- ✅ 동일한 입력 키 사용
- ✅ 일관된 데이터 구조
- ✅ 불필요한 변환 최소화
- ⚠️  불가피한 경우에만 RunnableLambda 사용

### 3. Phase 4 vs Phase 5 비교

#### Phase 4 방식 (수동 루프)

```python
messages = [HumanMessage(content=article)]

# 1단계: 요약
response1 = llm.invoke(messages)
summary = response1.content

# 2단계: 번역 (수동으로 메시지 추가)
messages.append(AIMessage(content=summary))
messages.append(HumanMessage(content="번역해줘"))
response2 = llm.invoke(messages)
translation = response2.content

# 3단계: 키워드 (수동으로 메시지 추가)
messages.append(AIMessage(content=translation))
messages.append(HumanMessage(content="키워드 추출해줘"))
response3 = llm.invoke(messages)
keywords = response3.content
```

**문제점:**
- ❌ 각 단계를 수동으로 호출
- ❌ 메시지 히스토리 수동 관리
- ❌ 코드가 길고 반복적
- ❌ 에러 처리가 분산됨

#### Phase 5 방식 (LCEL 파이프라인)

```python
workflow = (
    summarizer
    | RunnableLambda(map_to_text)
    | translator
    | RunnableLambda(map_to_text)
    | keyword_extractor
)

result = workflow.invoke({"article": article})
```

**장점:**
- ✅ 한 곳에 전체 파이프라인 정의
- ✅ 자동 데이터 전달
- ✅ 읽기 쉽고 유지보수 용이
- ✅ 단계 추가/제거가 간단

---

## 핵심 학습 포인트

### 1. Runnable 인터페이스

```python
# 모든 컴포넌트가 Runnable
- PromptTemplate: Runnable
- ChatModel (LLM): Runnable
- OutputParser: Runnable
- RunnableLambda: Runnable

# 일관된 인터페이스
result = runnable.invoke(input)
```

**의미:**
- 모든 컴포넌트가 동일한 인터페이스 제공
- 파이프 연산자로 자유롭게 조합 가능
- Composability (조합 가능성) 확보

### 2. 데이터 흐름의 자동화

```
{article} → [summarizer] → str → [map_to_text] → {text: str} → [translator] → str → ...
```

**Phase 4:**
```python
# 수동 데이터 전달
result1 = step1()
result2 = step2(result1)  # 명시적 전달
result3 = step3(result2)  # 명시적 전달
```

**Phase 5:**
```python
# 자동 데이터 전달
workflow = step1 | step2 | step3
result = workflow.invoke(input)  # 자동 처리
```

### 3. RunnableLambda의 활용

```python
# 일반 Python 함수를 Runnable로 변환
def my_function(x):
    return transform(x)

runnable_func = RunnableLambda(my_function)

# 체인에 삽입
chain = step1 | runnable_func | step2
```

**용도:**
- 데이터 형식 변환
- 전처리/후처리 로직
- 커스텀 비즈니스 로직

### 4. 순차 실행의 명시성

```python
workflow = (
    summarizer          # 1단계
    | map_to_text       # 2단계
    | translator        # 3단계
    | map_to_text       # 4단계
    | keyword_extractor # 5단계
)
```

**특징:**
- 실행 순서가 코드에 명시적으로 표현됨
- 가독성이 높음
- 유지보수가 쉬움

---

## 워크플로우 확장 예시

### 1. 감정 분석 단계 추가

```python
sentiment_analyzer = (
    PromptTemplate.from_template("감정 분석: {text}")
    | llm
    | StrOutputParser()
)

extended_workflow = (
    summarizer
    | RunnableLambda(map_to_text)
    | translator
    | RunnableLambda(map_to_text)
    | sentiment_analyzer  # 새 단계 추가
    | RunnableLambda(map_to_text)
    | keyword_extractor
)
```

### 2. 전처리 단계 추가

```python
def clean_text(data: dict) -> dict:
    article = data["article"].strip().lower()
    return {"article": article}

workflow_with_preprocessing = (
    RunnableLambda(clean_text)  # 맨 앞에 추가
    | summarizer
    | RunnableLambda(map_to_text)
    | translator
    | RunnableLambda(map_to_text)
    | keyword_extractor
)
```

### 3. 후처리 단계 추가

```python
def format_keywords(keywords: str) -> str:
    return f"🔑 핵심 키워드: {keywords}"

workflow_with_formatting = (
    summarizer
    | RunnableLambda(map_to_text)
    | translator
    | RunnableLambda(map_to_text)
    | keyword_extractor
    | RunnableLambda(format_keywords)  # 맨 뒤에 추가
)
```

**장점:**
- 파이프 연산자 앞뒤에 단계 추가만 하면 됨
- 기존 코드 수정 불필요
- 확장이 매우 간단

---

## 실전 적용 시나리오

### 1. 뉴스 기사 처리 파이프라인

```python
news_pipeline = (
    article_fetcher       # 기사 수집
    | summarizer          # 요약
    | translator          # 번역
    | keyword_extractor   # 키워드
    | category_classifier # 카테고리 분류
    | database_saver      # DB 저장
)
```

### 2. 콘텐츠 번역 파이프라인

```python
translation_pipeline = (
    input_validator       # 입력 검증
    | text_cleaner        # 텍스트 정제
    | translator          # 번역
    | quality_checker     # 품질 검사
    | formatter           # 포맷팅
)
```

### 3. 문서 분석 파이프라인

```python
document_pipeline = (
    pdf_extractor         # PDF 텍스트 추출
    | summarizer          # 요약
    | entity_extractor    # 개체명 추출
    | keyword_extractor   # 키워드
    | report_generator    # 보고서 생성
)
```

---

## 성능 특성

### 실행 시간

```
전체 워크플로우 실행 시간: 약 5-10초

단계별 추정 시간:
- summarizer: 2-4초 (LLM 호출)
- translator: 2-4초 (LLM 호출)
- keyword_extractor: 1-2초 (LLM 호출)
- map_to_text: <0.01초 (즉시)

총 LLM 호출: 3회
```

### 비용 추정

```
모델: claude-3-haiku-20240307
입력 토큰: 약 150 tokens/호출
출력 토큰: 약 50 tokens/호출

총 비용: 매우 낮음 (Haiku는 저비용 모델)
```

---

## 다음 단계

**예제 2: 병렬 파이프라인**에서는:
- `RunnableParallel`로 여러 작업 동시 실행
- 요약 + 감정 분석 + 키워드를 병렬 처리
- 순차 vs 병렬 성능 비교
- 독립적인 작업의 효율적 처리

**예제 1 (순차):**
```
입력 → [A] → [B] → [C] → 출력
```

**예제 2 (병렬):**
```
         ┌→ [A] → 결과A
입력 ----┼→ [B] → 결과B
         └→ [C] → 결과C
```

---

## 요약

### Phase 5 예제 1의 핵심

1. **LCEL 파이프 연산자 (`|`)**
   - 명시적인 파이프라인 구조
   - 자동 데이터 전달

2. **RunnableLambda**
   - 커스텀 함수를 체인에 삽입
   - 데이터 형식 변환

3. **순차 실행의 명확성**
   - 코드에 실행 순서가 명시됨
   - 가독성과 유지보수성 향상

4. **Phase 4 대비 개선**
   - 코드 간결성
   - 자동화된 데이터 흐름
   - 확장 용이성

**순차 파이프라인은 단계 간 의존성이 있는 작업에 적합합니다!**
