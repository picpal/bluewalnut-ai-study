# 왜 Python 기본 문법 대신 LangChain PromptTemplate을 사용할까?


## Python 기본 방식 vs LangChain PromptTemplate

### Python 기본 문자열 포맷팅

Python에는 이미 강력한 문자열 포맷팅 기능이 있습니다:

```python
# 방법 1: f-string (Python 3.6+)
name = "철수"
greeting = "안녕하세요"
result = f"안녕하세요, {name}님! {greeting}"

# 방법 2: str.format()
template = "안녕하세요, {name}님! {greeting}"
result = template.format(name="철수", greeting="안녕하세요")

# 방법 3: % 포맷팅 (구식)
result = "안녕하세요, %s님! %s" % (name, greeting)
```

### LangChain PromptTemplate

```python
from langchain.prompts import PromptTemplate

template = "안녕하세요, {name}님! {greeting}"
prompt = PromptTemplate(
    input_variables=["name", "greeting"],
    template=template
)

result = prompt.format(name="철수", greeting="안녕하세요")
```

**의문:** 위 두 방식이 결과는 같은데, 왜 굳이 LangChain을 사용할까?

---

## LangChain PromptTemplate의 4가지 핵심 장점

### 1. LangChain 생태계와 통합 (가장 중요!)

**Python 기본 방식의 한계:**
```python
template = "안녕하세요, {name}님!"
llm = ChatOpenAI(...)

# ❌ 에러! str 타입은 파이프 연산자를 지원하지 않음
chain = template | llm
```

**LangChain PromptTemplate:**
```python
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

prompt = PromptTemplate(
    input_variables=["name"],
    template="안녕하세요, {name}님!"
)
llm = ChatOpenAI(...)

# ✅ 성공! LCEL(LangChain Expression Language) 파이프 연결
chain = prompt | llm
response = chain.invoke({"name": "철수"})
```

**핵심:** PromptTemplate은 단순 문자열이 아니라 **LangChain의 Runnable 객체**이기 때문에 다른 컴포넌트와 자유롭게 연결할 수 있습니다.

---

### 2. Runnable 인터페이스 구현

LangChain의 모든 주요 컴포넌트는 `Runnable` 인터페이스를 구현합니다.

```python
prompt = PromptTemplate(...)

# 다양한 실행 방식 제공
prompt.invoke({"name": "철수"})           # 단일 실행
prompt.batch([                             # 배치 실행 (여러 입력 동시 처리)
    {"name": "철수"},
    {"name": "영희"},
    {"name": "민수"}
])
prompt.stream({"name": "철수"})           # 스트림 실행 (점진적 출력)
```

**Python 기본 문자열:**
```python
template = "안녕하세요, {name}님!"

# ❌ invoke, batch, stream 같은 메서드 없음
template.invoke({"name": "철수"})  # AttributeError
```

**장점:**
- 일관된 인터페이스로 모든 LangChain 컴포넌트 사용
- 코드 학습 곡선 감소
- 유지보수 용이

---

### 3. 입력 검증 기능

**LangChain PromptTemplate:**
```python
prompt = PromptTemplate(
    input_variables=["name", "greeting"],
    template="안녕하세요, {name}님! {greeting}"
)

# ✅ 올바른 사용
prompt.format(name="철수", greeting="안녕")

# ❌ 변수 누락 시 명확한 에러
prompt.format(name="철수")
# KeyError: 'greeting' - 어떤 변수가 빠졌는지 즉시 알 수 있음

# ⚠️ 정의되지 않은 변수 사용 시 경고 가능
prompt.format(name="철수", greeting="안녕", age=20)
# age는 input_variables에 없음
```

**Python str.format():**
```python
template = "안녕하세요, {name}님! {greeting}"

# ❌ 변수 누락 시 에러
template.format(name="철수")
# KeyError: 'greeting' - 하지만 input_variables 선언이 없어서
# 사전에 어떤 변수가 필요한지 알기 어려움

# ⚠️ 잘못된 변수는 무시됨 (버그 발견 어려움)
template.format(name="철수", greeting="안녕", age=20)
# age는 사용되지 않지만 경고 없음
```

**장점:**
- 프롬프트 구조를 명시적으로 선언
- 런타임 에러를 사전에 방지
- 코드 가독성 향상

---

### 4. 복잡한 프롬프트 관리

실제 LLM 애플리케이션에서는 단순 문자열보다 훨씬 복잡한 프롬프트가 필요합니다.

**채팅 프롬프트 예시:**
```python
from langchain.prompts import ChatPromptTemplate

# 시스템 메시지 + 사용자 메시지 구조화
prompt = ChatPromptTemplate.from_messages([
    ("system", "당신은 {role} 전문가입니다. {tone} 톤으로 답변하세요."),
    ("human", "{question}"),
])

result = prompt.invoke({
    "role": "파이썬 프로그래밍",
    "tone": "친절하고 상세한",
    "question": "리스트 컴프리헨션이 뭔가요?"
})
```

**Few-shot 프롬프트 예시:**
```python
from langchain.prompts import FewShotPromptTemplate

# 예제 기반 프롬프트
examples = [
    {"input": "사과", "output": "빨간색"},
    {"input": "바나나", "output": "노란색"},
]

few_shot_prompt = FewShotPromptTemplate(
    examples=examples,
    example_prompt=PromptTemplate(
        input_variables=["input", "output"],
        template="입력: {input}\n출력: {output}"
    ),
    prefix="다음은 과일과 색상의 관계입니다:",
    suffix="입력: {fruit}\n출력:",
    input_variables=["fruit"]
)
```

**Python 기본 방식:**
```python
# 매우 복잡하고 관리하기 어려운 문자열 조합
system = f"당신은 {role} 전문가입니다. {tone} 톤으로 답변하세요."
user = f"{question}"
# 메시지 구조 관리가 어렵고 에러 발생 가능성 높음
```

**장점:**
- 복잡한 프롬프트 구조를 명확하게 관리
- 시스템 메시지, few-shot 예제, 대화 히스토리 등 체계적 관리
- 프롬프트 템플릿 재사용성 극대화

---

## 비교 표

| 특성 | Python str.format() | LangChain PromptTemplate |
|------|---------------------|--------------------------|
| **문자열 포맷팅** | ✅ 가능 | ✅ 가능 |
| **간단한 사용** | ✅ 더 간단 | ⚠️ 약간 복잡 |
| **LangChain 체인 연결** | ❌ 불가 | ✅ 가능 (`\|` 연산자) |
| **Runnable 인터페이스** | ❌ 없음 | ✅ 있음 (invoke, batch, stream) |
| **입력 검증** | ❌ 없음 | ✅ 있음 (input_variables) |
| **복잡한 프롬프트 구조** | ❌ 어려움 | ✅ 쉬움 (ChatPromptTemplate 등) |
| **타입 안전성** | ❌ 없음 | ✅ 있음 |
| **디버깅** | ⚠️ 어려움 | ✅ 쉬움 (명시적 변수 선언) |
| **학습 곡선** | ✅ 낮음 (Python 기본) | ⚠️ 중간 (LangChain 개념 필요) |

---

## 언제 무엇을 사용해야 할까?

### Python 기본 방식이 적합한 경우:
- LLM을 전혀 사용하지 않는 일반 문자열 처리
- 매우 간단한 일회성 스크립트
- LangChain을 사용하지 않는 프로젝트

```python
# 단순 로그 메시지 생성
log = f"User {username} logged in at {timestamp}"
```

### LangChain PromptTemplate이 적합한 경우:
- LLM과 통합하는 모든 경우 (거의 대부분!)
- 프롬프트를 재사용해야 하는 경우
- 복잡한 프롬프트 구조가 필요한 경우
- 팀 프로젝트에서 프롬프트를 체계적으로 관리해야 하는 경우

```python
# LLM 애플리케이션
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

prompt = PromptTemplate(...)
llm = ChatOpenAI(...)
chain = prompt | llm  # 이 시점에서 PromptTemplate이 필수!
```

---

## 핵심 정리

> **PromptTemplate의 본질:**
>
> 단순히 "문자열 포맷팅을 하는 도구"가 아니라,
> **LangChain 생태계 내에서 다른 컴포넌트(LLM, Parser, Agent 등)와
> 연결되는 표준화된 인터페이스를 제공하는 것**이 목적입니다.

```python
# 이것이 가능하게 만드는 것이 핵심!
chain = prompt | llm | output_parser | ...
```

---

## 다음 단계

예제 2에서 `prompt | llm` 체인을 실습하면서 이 장점을 직접 체험해보세요!

```bash
python step1_example2_prompt_llm_chain.py
```

**예제 2에서 배울 내용:**
- PromptTemplate과 LLM을 파이프(`|`)로 연결하는 방법
- LCEL(LangChain Expression Language)의 강력함
- `chain.invoke()`로 전체 파이프라인 실행하기
