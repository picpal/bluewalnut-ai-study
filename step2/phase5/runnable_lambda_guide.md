# RunnableLambda 완벽 가이드

## 목차

1. [RunnableLambda란?](#runnablelambda란)
2. [왜 필요한가?](#왜-필요한가)
3. [기본 사용법](#기본-사용법)
4. [주요 활용 사례](#주요-활용-사례)
5. [실전 예제](#실전-예제)
6. [고급 패턴](#고급-패턴)
7. [성능 고려사항](#성능-고려사항)
8. [베스트 프랙티스](#베스트-프랙티스)

---

## RunnableLambda란?

**일반 Python 함수를 LangChain의 `Runnable` 인터페이스로 변환하는 래퍼(Wrapper)**

```python
from langchain_core.runnables import RunnableLambda

# 일반 Python 함수
def my_function(x):
    return x.upper()

# Runnable로 변환
runnable_function = RunnableLambda(my_function)

# 이제 체인에서 사용 가능
chain = step1 | runnable_function | step2
```

### 핵심 개념

- **래퍼 패턴**: 일반 함수를 LangChain 체인에서 사용 가능하도록 감쌈
- **인터페이스 통일**: 모든 LangChain 컴포넌트와 동일한 방식으로 동작
- **체인의 접착제**: 서로 다른 컴포넌트를 연결하는 역할

---

## 왜 필요한가?

### 1. Runnable 인터페이스 통일

LangChain의 모든 주요 컴포넌트는 `Runnable` 인터페이스를 구현합니다:

```python
# 모두 Runnable 인터페이스 구현
prompt.invoke(input)      # PromptTemplate
llm.invoke(input)         # ChatModel
parser.invoke(input)      # OutputParser

# 일반 함수는 Runnable이 아님
my_function(input)        # ❌ invoke() 메서드 없음

# RunnableLambda로 변환
runnable = RunnableLambda(my_function)
runnable.invoke(input)    # ✅ invoke() 메서드 사용 가능
```

### 2. 파이프 연산자 호환성

```python
# ❌ 일반 함수는 파이프 연산자와 호환 불가
chain = prompt | llm | my_function | parser  # TypeError!

# ✅ RunnableLambda는 파이프 연산자와 완벽 호환
chain = prompt | llm | RunnableLambda(my_function) | parser
```

### 3. 추가 기능 제공

```python
runnable = RunnableLambda(my_function)

# 단일 실행
result = runnable.invoke(input)

# 배치 처리
results = runnable.batch([input1, input2, input3])

# 스트리밍 (가능한 경우)
for chunk in runnable.stream(input):
    print(chunk)

# 비동기 실행
result = await runnable.ainvoke(input)
```

---

## 기본 사용법

### 1. 함수 정의 방식

#### 방법 1: 일반 함수 정의 후 래핑

```python
def uppercase(text: str) -> str:
    """텍스트를 대문자로 변환"""
    return text.upper()

runnable = RunnableLambda(uppercase)
result = runnable.invoke("hello")  # "HELLO"
```

#### 방법 2: 람다 함수 직접 사용

```python
runnable = RunnableLambda(lambda x: x.upper())
result = runnable.invoke("hello")  # "HELLO"
```

#### 방법 3: 체인 안에서 직접 사용

```python
chain = (
    prompt
    | llm
    | RunnableLambda(lambda x: x.upper())
    | parser
)
```

### 2. 타입 힌트 활용

```python
def process_text(text: str) -> str:
    """명확한 타입 힌트로 가독성 향상"""
    return text.strip().lower()

runnable = RunnableLambda(process_text)
```

### 3. 복잡한 변환

```python
def transform_data(data: dict) -> dict:
    """딕셔너리 변환"""
    return {
        "text": data.get("content", ""),
        "metadata": {
            "length": len(data.get("content", "")),
            "timestamp": data.get("timestamp")
        }
    }

transformer = RunnableLambda(transform_data)
```

---

## 주요 활용 사례

### 1. 데이터 형식 변환 ⭐

**가장 일반적이고 중요한 사용 사례**

#### str → dict 변환

```python
# 문자열을 딕셔너리로 변환
def str_to_dict(text: str) -> dict:
    return {"text": text}

str_to_dict_runnable = RunnableLambda(str_to_dict)

chain = (
    summarizer                          # 출력: str
    | str_to_dict_runnable             # str → {"text": str}
    | translator                        # 입력: {"text"}
)
```

#### 키 이름 변경

```python
# article → text 키 변경
def rename_key(data: dict) -> dict:
    return {"text": data.get("article", "")}

key_mapper = RunnableLambda(rename_key)

chain = (
    fetcher                            # 출력: {"article": "..."}
    | key_mapper                       # {"article"} → {"text"}
    | processor                        # 입력: {"text"}
)
```

#### Phase 5 예제 1에서의 실제 사용

```python
def map_to_text(output: str) -> dict:
    return {"text": output}

workflow = (
    summarizer                          # {article} → str
    | RunnableLambda(map_to_text)      # str → {text}
    | translator                        # {text} → str
    | RunnableLambda(map_to_text)      # str → {text}
    | keyword_extractor                 # {text} → str
)
```

### 2. 데이터 전처리

#### 텍스트 정제

```python
def clean_text(data: dict) -> dict:
    """공백 제거 및 소문자 변환"""
    text = data["text"]
    cleaned = text.strip().lower()
    return {"text": cleaned}

cleaner = RunnableLambda(clean_text)

chain = (
    cleaner           # 전처리
    | summarizer      # 요약
    | translator      # 번역
)
```

#### 데이터 검증

```python
def validate_input(data: dict) -> dict:
    """입력 데이터 검증"""
    text = data.get("text", "")

    if not text or not text.strip():
        raise ValueError("텍스트가 비어있습니다")

    if len(text) < 10:
        raise ValueError("텍스트가 너무 짧습니다")

    return data

validator = RunnableLambda(validate_input)

chain = (
    validator         # 검증
    | processor       # 처리
)
```

#### 메타데이터 추가

```python
def add_metadata(data: dict) -> dict:
    """메타데이터 추가"""
    from datetime import datetime

    return {
        **data,
        "processed_at": datetime.now().isoformat(),
        "word_count": len(data["text"].split()),
        "char_count": len(data["text"])
    }

metadata_adder = RunnableLambda(add_metadata)

chain = (
    processor
    | metadata_adder   # 메타데이터 추가
    | saver
)
```

### 3. 데이터 후처리

#### 결과 포맷팅

```python
def format_result(text: str) -> str:
    """결과를 보기 좋게 포맷팅"""
    return f"""
╔═══════════════════════════════════════════╗
║           분석 결과                       ║
╠═══════════════════════════════════════════╣
{text}
╚═══════════════════════════════════════════╝
"""

formatter = RunnableLambda(format_result)

chain = (
    analyzer
    | formatter        # 포맷팅
)
```

#### 결과 통합

```python
def merge_results(results: dict) -> str:
    """병렬 실행 결과를 하나로 통합"""
    return f"""
요약: {results['summary']}
감정: {results['sentiment']}
키워드: {results['keywords']}
"""

merger = RunnableLambda(merge_results)

chain = (
    RunnableParallel(
        summary=summarizer,
        sentiment=sentiment_analyzer,
        keywords=keyword_extractor
    )
    | merger          # 결과 통합
)
```

### 4. 로깅 및 디버깅

#### 중간 결과 출력

```python
def log_output(data):
    """중간 결과를 로깅하고 그대로 전달"""
    print(f"📊 중간 결과: {data}")
    return data

logger = RunnableLambda(log_output)

chain = (
    step1
    | logger          # 로깅
    | step2
    | logger          # 로깅
    | step3
)
```

#### 타임스탬프 추가

```python
import time

def log_with_timestamp(data):
    """타임스탬프와 함께 로깅"""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] 데이터: {data}")
    return data

timestamped_logger = RunnableLambda(log_with_timestamp)
```

#### 조건부 로깅

```python
def conditional_log(data, condition=lambda x: True):
    """조건을 만족할 때만 로깅"""
    if condition(data):
        print(f"⚠️  조건 충족: {data}")
    return data

# 사용
chain = (
    step1
    | RunnableLambda(lambda x: conditional_log(x, lambda d: len(d["text"]) > 100))
    | step2
)
```

### 5. 조건부 로직

#### 길이에 따른 분기

```python
def process_by_length(data: dict) -> dict:
    """텍스트 길이에 따라 다른 처리"""
    text = data["text"]

    if len(text) < 100:
        # 짧은 텍스트는 그대로
        return data
    elif len(text) < 500:
        # 중간 길이는 약간 요약
        return {"text": text[:250] + "..."}
    else:
        # 긴 텍스트는 많이 요약
        return {"text": text[:100] + "..."}

processor = RunnableLambda(process_by_length)

chain = (
    processor         # 조건부 처리
    | translator
)
```

#### 언어 감지

```python
def detect_and_route(data: dict) -> dict:
    """언어를 감지하고 적절한 처리 경로 설정"""
    text = data["text"]

    # 간단한 언어 감지 (실제로는 langdetect 등 사용)
    if any(ord(char) > 127 for char in text[:100]):
        data["language"] = "non-english"
    else:
        data["language"] = "english"

    return data

language_router = RunnableLambda(detect_and_route)
```

### 6. 에러 처리

#### Try-Catch 래퍼

```python
def safe_process(data):
    """에러가 발생해도 계속 진행"""
    try:
        # 위험한 작업
        result = risky_operation(data)
        return result
    except Exception as e:
        print(f"❌ 에러 발생: {e}")
        return {"error": str(e), "original": data}

safe_processor = RunnableLambda(safe_process)

chain = (
    safe_processor    # 에러 처리
    | next_step
)
```

#### Fallback 패턴

```python
def with_fallback(primary_func, fallback_func):
    """실패 시 대체 함수 실행"""
    def wrapper(data):
        try:
            return primary_func(data)
        except Exception as e:
            print(f"⚠️  Primary 실패, fallback 사용: {e}")
            return fallback_func(data)
    return wrapper

# 사용
processor = RunnableLambda(
    with_fallback(
        primary_process,
        simple_process
    )
)
```

---

## 실전 예제

### 예제 1: 완전한 전처리 파이프라인

```python
from langchain_core.runnables import RunnableLambda
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

# LLM 초기화
llm = ChatAnthropic(model="claude-3-haiku-20240307")

# 1. 전처리 함수들
def clean_text(data: dict) -> dict:
    """텍스트 정제"""
    text = data["text"]
    cleaned = text.strip().lower()
    return {"text": cleaned}

def validate_length(data: dict) -> dict:
    """길이 검증"""
    if len(data["text"]) < 10:
        raise ValueError("텍스트가 너무 짧습니다")
    return data

def add_metadata(data: dict) -> dict:
    """메타데이터 추가"""
    from datetime import datetime
    return {
        **data,
        "timestamp": datetime.now().isoformat(),
        "length": len(data["text"])
    }

# 2. LLM 체인
summarizer = (
    PromptTemplate.from_template("요약: {text}")
    | llm
    | StrOutputParser()
)

# 3. 후처리 함수
def format_output(text: str) -> str:
    """결과 포맷팅"""
    return f"📝 요약 결과:\n{text}"

# 4. 전체 파이프라인
pipeline = (
    RunnableLambda(clean_text)         # 정제
    | RunnableLambda(validate_length)   # 검증
    | RunnableLambda(add_metadata)      # 메타데이터
    | summarizer                         # 요약
    | RunnableLambda(format_output)     # 포맷팅
)

# 실행
result = pipeline.invoke({"text": "Your article here..."})
print(result)
```

### 예제 2: 병렬 실행 후 통합

```python
from langchain_core.runnables import RunnableParallel, RunnableLambda

# 병렬 분석
parallel = RunnableParallel(
    summary=summarizer,
    keywords=keyword_extractor,
    sentiment=sentiment_analyzer
)

# 결과 통합 함수
def integrate_results(results: dict) -> dict:
    """병렬 분석 결과 통합"""
    return {
        "summary": results["summary"],
        "keywords": results["keywords"].split(", "),
        "sentiment": results["sentiment"],
        "analysis_complete": True
    }

# 최종 포맷팅
def format_final(data: dict) -> str:
    """최종 보고서 생성"""
    return f"""
╔═══════════════════════════════════════════╗
║           분석 완료                       ║
╠═══════════════════════════════════════════╣

📝 요약:
{data['summary']}

🔑 키워드:
{', '.join(data['keywords'])}

😊 감정:
{data['sentiment']}

╚═══════════════════════════════════════════╝
"""

# 전체 워크플로우
workflow = (
    parallel                             # 병렬 분석
    | RunnableLambda(integrate_results)  # 통합
    | RunnableLambda(format_final)       # 포맷팅
)

result = workflow.invoke({"text": "Your article..."})
print(result)
```

### 예제 3: 조건부 라우팅

```python
def route_by_length(data: dict) -> dict:
    """길이에 따라 처리 경로 설정"""
    length = len(data["text"])

    if length < 100:
        data["route"] = "short"
    elif length < 500:
        data["route"] = "medium"
    else:
        data["route"] = "long"

    return data

def process_by_route(data: dict) -> str:
    """경로에 따라 다른 처리"""
    route = data["route"]
    text = data["text"]

    if route == "short":
        return f"짧은 텍스트: {text}"
    elif route == "medium":
        return f"중간 텍스트: {text[:100]}..."
    else:
        return f"긴 텍스트: {text[:50]}..."

# 파이프라인
pipeline = (
    RunnableLambda(route_by_length)      # 라우팅
    | RunnableLambda(process_by_route)   # 경로별 처리
)

result = pipeline.invoke({"text": "Some text..."})
```

### 예제 4: 상태 추적

```python
def create_state_tracker():
    """상태를 추적하는 함수 생성"""
    state = {"count": 0, "total_length": 0}

    def track(data: dict) -> dict:
        state["count"] += 1
        state["total_length"] += len(data.get("text", ""))

        print(f"처리 횟수: {state['count']}")
        print(f"총 길이: {state['total_length']}")

        return data

    return track

# 사용
tracker = RunnableLambda(create_state_tracker())

pipeline = (
    tracker           # 상태 추적
    | processor
    | tracker         # 다시 추적
)
```

---

## 고급 패턴

### 1. 함수 합성 (Composition)

```python
def compose(*functions):
    """여러 함수를 하나로 합성"""
    def composed(data):
        result = data
        for func in functions:
            result = func(result)
        return result
    return composed

# 사용
cleaner = compose(
    lambda x: x.strip(),
    lambda x: x.lower(),
    lambda x: x.replace("\n", " ")
)

pipeline = (
    RunnableLambda(cleaner)
    | processor
)
```

### 2. 데코레이터 패턴

```python
def with_logging(func):
    """로깅을 추가하는 데코레이터"""
    def wrapper(data):
        print(f"[IN] {data}")
        result = func(data)
        print(f"[OUT] {result}")
        return result
    return wrapper

def with_timing(func):
    """실행 시간을 측정하는 데코레이터"""
    import time
    def wrapper(data):
        start = time.time()
        result = func(data)
        elapsed = time.time() - start
        print(f"⏱️  실행 시간: {elapsed:.4f}초")
        return result
    return wrapper

# 사용
@with_logging
@with_timing
def process(data):
    return data.upper()

pipeline = (
    RunnableLambda(process)
    | next_step
)
```

### 3. 캐싱 패턴

```python
def with_cache(func):
    """결과를 캐싱하는 래퍼"""
    cache = {}

    def wrapper(data):
        # 딕셔너리를 해시 가능한 형태로 변환
        key = str(data)

        if key in cache:
            print("💾 캐시에서 반환")
            return cache[key]

        print("🔄 새로 계산")
        result = func(data)
        cache[key] = result
        return result

    return wrapper

# 사용
cached_processor = RunnableLambda(with_cache(expensive_process))

pipeline = (
    cached_processor  # 캐시 적용
    | next_step
)
```

### 4. 재시도 패턴

```python
def with_retry(func, max_retries=3):
    """재시도 로직을 추가하는 래퍼"""
    import time

    def wrapper(data):
        for attempt in range(max_retries):
            try:
                return func(data)
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                print(f"⚠️  재시도 {attempt + 1}/{max_retries}")
                time.sleep(1 * (attempt + 1))  # 지수 백오프

    return wrapper

# 사용
reliable_processor = RunnableLambda(with_retry(unstable_process, 3))

pipeline = (
    reliable_processor  # 재시도 포함
    | next_step
)
```

### 5. 파이프라인 분기

```python
def create_branch(condition_func, true_branch, false_branch):
    """조건에 따라 다른 파이프라인 실행"""
    def brancher(data):
        if condition_func(data):
            return true_branch.invoke(data)
        else:
            return false_branch.invoke(data)
    return brancher

# 사용
is_long = lambda x: len(x.get("text", "")) > 1000

long_pipeline = summarizer | translator
short_pipeline = translator | keyword_extractor

brancher = RunnableLambda(
    create_branch(
        is_long,
        long_pipeline,
        short_pipeline
    )
)

pipeline = (
    preprocessor
    | brancher        # 조건부 분기
    | postprocessor
)
```

---

## 성능 고려사항

### 1. 오버헤드 측정

```python
import time

# 테스트 함수
def simple_process(x):
    return x.upper()

# 일반 함수 호출
start = time.time()
for i in range(100000):
    result = simple_process("hello")
time1 = time.time() - start

# RunnableLambda 호출
runnable = RunnableLambda(simple_process)
start = time.time()
for i in range(100000):
    result = runnable.invoke("hello")
time2 = time.time() - start

print(f"일반 함수: {time1:.4f}초")
print(f"RunnableLambda: {time2:.4f}초")
print(f"오버헤드: {((time2 - time1) / time1 * 100):.2f}%")

# 일반적으로 1-5% 정도의 오버헤드
# LLM 호출 시간에 비하면 무시할 수 있는 수준
```

### 2. 최적화 팁

#### ✅ 좋은 예

```python
# 간단한 변환은 람다 사용
RunnableLambda(lambda x: x.upper())
RunnableLambda(lambda x: {"text": x})

# 반복되는 패턴은 함수로 정의
def to_dict(x):
    return {"text": x}

key_mapper = RunnableLambda(to_dict)
```

#### ⚠️ 주의할 점

```python
# 복잡한 로직은 별도 함수로
def complex_processing(data):
    # 많은 처리...
    # 100줄 이상의 코드
    return result

# 람다로 작성하지 말 것
# RunnableLambda(lambda x: ... 100 lines ...)  # ❌

# 명확한 함수로 작성
RunnableLambda(complex_processing)  # ✅
```

### 3. 메모리 관리

```python
# ❌ 나쁜 예: 클로저로 큰 데이터 캡처
large_data = load_large_dataset()  # 1GB

def process_with_data(x):
    # large_data가 메모리에 계속 유지됨
    return lookup(large_data, x)

processor = RunnableLambda(process_with_data)

# ✅ 좋은 예: 필요할 때만 로드
def process_efficiently(x):
    data = load_specific_data(x)  # 필요한 부분만
    return lookup(data, x)

processor = RunnableLambda(process_efficiently)
```

---

## 베스트 프랙티스

### ✅ 권장 사항

#### 1. 명확한 함수 이름

```python
# ❌ 나쁜 예
f = RunnableLambda(lambda x: x.upper())

# ✅ 좋은 예
def uppercase_text(text: str) -> str:
    return text.upper()

uppercaser = RunnableLambda(uppercase_text)
```

#### 2. 타입 힌트 사용

```python
# ✅ 타입 힌트로 명확성 향상
def transform_data(data: dict) -> dict:
    """데이터 변환 함수

    Args:
        data: 입력 딕셔너리

    Returns:
        변환된 딕셔너리
    """
    return {"text": data.get("content", "")}

transformer = RunnableLambda(transform_data)
```

#### 3. 단일 책임 원칙

```python
# ❌ 나쁜 예: 여러 작업을 한 함수에
def do_everything(data):
    cleaned = data.strip().lower()
    validated = validate(cleaned)
    enriched = add_metadata(validated)
    return enriched

# ✅ 좋은 예: 각 작업을 분리
cleaner = RunnableLambda(lambda x: x.strip().lower())
validator = RunnableLambda(validate)
enricher = RunnableLambda(add_metadata)

pipeline = cleaner | validator | enricher
```

#### 4. 재사용 가능한 함수

```python
# ✅ 재사용 가능한 유틸리티 함수
def create_key_mapper(from_key: str, to_key: str):
    """키 이름을 변경하는 함수 생성"""
    def mapper(data: dict) -> dict:
        return {to_key: data.get(from_key, "")}
    return mapper

# 여러 곳에서 재사용
article_to_text = RunnableLambda(create_key_mapper("article", "text"))
content_to_text = RunnableLambda(create_key_mapper("content", "text"))
```

#### 5. 에러 메시지 명확하게

```python
def validate_input(data: dict) -> dict:
    """입력 검증"""
    if "text" not in data:
        raise ValueError("'text' 키가 필요합니다")

    if not isinstance(data["text"], str):
        raise TypeError("'text'는 문자열이어야 합니다")

    if len(data["text"]) < 10:
        raise ValueError(
            f"텍스트가 너무 짧습니다 (최소 10자, 현재 {len(data['text'])}자)"
        )

    return data

validator = RunnableLambda(validate_input)
```

### ⚠️ 피해야 할 패턴

#### 1. 복잡한 람다 함수

```python
# ❌ 나쁜 예: 읽기 어려운 람다
RunnableLambda(lambda x: {"text": x.get("content", "").strip().lower().replace("\n", " ") if x.get("content") else ""})

# ✅ 좋은 예: 명확한 함수
def prepare_text(data: dict) -> dict:
    content = data.get("content", "")
    if not content:
        return {"text": ""}

    cleaned = content.strip().lower().replace("\n", " ")
    return {"text": cleaned}

preparer = RunnableLambda(prepare_text)
```

#### 2. 부작용(Side Effects)이 있는 함수

```python
# ⚠️  주의: 부작용이 있는 함수
def process_with_side_effect(data):
    # 전역 변수 수정
    global counter
    counter += 1

    # 파일 쓰기
    with open("log.txt", "a") as f:
        f.write(str(data))

    return data

# ✅ 더 나은 방법: 부작용을 명시적으로 처리
def process_safely(data):
    # 로깅은 별도 시스템 사용
    logger.info(f"Processing: {data}")
    return data
```

#### 3. 상태 의존적인 함수

```python
# ⚠️  주의: 외부 상태에 의존
external_config = {"mode": "production"}

def process_with_state(data):
    # 외부 상태에 의존 - 예측 불가능
    if external_config["mode"] == "production":
        return process_prod(data)
    else:
        return process_dev(data)

# ✅ 더 나은 방법: 상태를 명시적으로 전달
def create_processor(mode: str):
    def processor(data):
        if mode == "production":
            return process_prod(data)
        else:
            return process_dev(data)
    return processor

prod_processor = RunnableLambda(create_processor("production"))
```

---

## 일반 함수 vs RunnableLambda 비교

| 항목 | 일반 함수 | RunnableLambda |
|------|----------|----------------|
| **호출 방식** | `func(x)` | `runnable.invoke(x)` |
| **파이프 연산자** | ❌ 불가 | ✅ 가능 |
| **배치 처리** | 수동 구현 | ✅ `.batch()` 제공 |
| **스트리밍** | 수동 구현 | ✅ `.stream()` 제공 |
| **비동기** | `async def` 필요 | ✅ `.ainvoke()` 제공 |
| **체인 통합** | ❌ 어려움 | ✅ 완전 통합 |
| **에러 처리** | 수동 구현 | 체인 레벨 처리 가능 |
| **디버깅** | 쉬움 | 약간 복잡 |
| **성능** | 빠름 | 약간 느림 (1-5%) |

### 언제 무엇을 사용할까?

```python
# ✅ RunnableLambda 사용
- LangChain 체인에서 사용
- 파이프 연산자 필요
- 배치 처리 필요
- 일관된 인터페이스 필요

# ✅ 일반 함수 사용
- 체인 외부에서 사용
- 단순 유틸리티 함수
- 성능이 매우 중요
- 테스트 용이성 중요
```

---

## 실전 사용 시나리오

### 시나리오 1: API 응답 변환

```python
def transform_api_response(response: dict) -> dict:
    """외부 API 응답을 내부 형식으로 변환"""
    return {
        "text": response.get("data", {}).get("content", ""),
        "metadata": {
            "source": "external_api",
            "timestamp": response.get("timestamp"),
            "version": response.get("version", "1.0")
        }
    }

api_transformer = RunnableLambda(transform_api_response)

pipeline = (
    api_fetcher
    | api_transformer      # API 응답 변환
    | processor
)
```

### 시나리오 2: 다국어 처리

```python
def detect_language(data: dict) -> dict:
    """언어 감지 및 태깅"""
    text = data["text"]

    # 간단한 언어 감지
    if any('\u4e00' <= char <= '\u9fff' for char in text):
        lang = "zh"
    elif any('\u3040' <= char <= '\u309f' for char in text):
        lang = "ja"
    elif any('\uac00' <= char <= '\ud7a3' for char in text):
        lang = "ko"
    else:
        lang = "en"

    return {**data, "language": lang}

language_detector = RunnableLambda(detect_language)

pipeline = (
    language_detector      # 언어 감지
    | language_router      # 언어별 처리
)
```

### 시나리오 3: 품질 필터링

```python
def filter_low_quality(data: dict) -> dict:
    """저품질 데이터 필터링"""
    text = data.get("text", "")

    # 품질 체크
    quality_score = 0

    if len(text) >= 50:
        quality_score += 1

    if any(char.isalpha() for char in text):
        quality_score += 1

    if text.count(" ") >= 5:
        quality_score += 1

    data["quality_score"] = quality_score

    if quality_score < 2:
        raise ValueError(f"품질이 낮습니다 (점수: {quality_score}/3)")

    return data

quality_filter = RunnableLambda(filter_low_quality)

pipeline = (
    fetcher
    | quality_filter       # 품질 필터링
    | processor
)
```

---

## 디버깅 팁

### 1. 중간 결과 확인

```python
def debug_print(label: str):
    """디버깅용 프린트 함수 생성"""
    def printer(data):
        print(f"\n{'='*50}")
        print(f"[{label}]")
        print(f"{'='*50}")
        print(data)
        print(f"{'='*50}\n")
        return data
    return printer

pipeline = (
    step1
    | RunnableLambda(debug_print("Step 1 결과"))
    | step2
    | RunnableLambda(debug_print("Step 2 결과"))
    | step3
)
```

### 2. 타입 검증

```python
def type_checker(expected_type):
    """타입을 검증하는 함수 생성"""
    def checker(data):
        if not isinstance(data, expected_type):
            raise TypeError(
                f"예상 타입: {expected_type}, "
                f"실제 타입: {type(data)}"
            )
        return data
    return checker

pipeline = (
    step1
    | RunnableLambda(type_checker(dict))   # dict 확인
    | step2
    | RunnableLambda(type_checker(str))    # str 확인
    | step3
)
```

### 3. 단계별 시간 측정

```python
import time

def time_logger(label: str):
    """실행 시간을 측정하는 함수 생성"""
    def logger(data):
        start = time.time()
        # 데이터를 그대로 전달하되 시간 측정
        elapsed = time.time() - start
        print(f"⏱️  [{label}] 실행 시간: {elapsed:.4f}초")
        return data
    return logger

pipeline = (
    RunnableLambda(time_logger("시작"))
    | step1
    | RunnableLambda(time_logger("Step 1 완료"))
    | step2
    | RunnableLambda(time_logger("Step 2 완료"))
)
```

---

## 요약

### RunnableLambda의 핵심

**목적**
- 일반 Python 함수를 LangChain의 Runnable 인터페이스로 변환
- 체인에서 커스텀 로직을 사용할 수 있게 해주는 "접착제" 역할

**주요 장점**
- ✅ 파이프 연산자 (`|`) 호환
- ✅ 배치 처리 (`.batch()`) 지원
- ✅ 스트리밍 (`.stream()`) 지원
- ✅ 비동기 (`.ainvoke()`) 지원
- ✅ 일관된 인터페이스

**주요 사용 사례**
1. 데이터 형식 변환 (str ↔ dict)
2. 전처리 (정제, 검증, 메타데이터 추가)
3. 후처리 (포맷팅, 통합)
4. 로깅 및 디버깅
5. 조건부 로직
6. 에러 처리

**베스트 프랙티스**
- ✅ 명확한 함수 이름 사용
- ✅ 타입 힌트 추가
- ✅ 단일 책임 원칙 준수
- ✅ 재사용 가능하게 설계
- ⚠️  복잡한 람다 함수 지양
- ⚠️  부작용 최소화

### 기본 패턴 정리

```python
# 1. 키 매핑
RunnableLambda(lambda x: {"text": x})

# 2. 전처리
RunnableLambda(lambda x: preprocess(x))

# 3. 후처리
RunnableLambda(lambda x: format_output(x))

# 4. 로깅
RunnableLambda(lambda x: print(x) or x)

# 5. 검증
RunnableLambda(lambda x: validate(x))
```

---

## 참고 자료

- [LangChain 공식 문서 - Runnable](https://python.langchain.com/docs/expression_language/interface/)
- [LangChain 공식 문서 - RunnableLambda](https://python.langchain.com/docs/expression_language/primitives/lambda/)
- Phase 5 예제 코드 참고

---

**RunnableLambda는 LangChain 체인의 강력한 도구입니다. 적절히 사용하면 유연하고 강력한 파이프라인을 구축할 수 있습니다!** 🚀
