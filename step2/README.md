# LangChain 학습 프로젝트

## 현재 단계: Step 1 - PromptTemplate + LLM 체인

### 학습 목표

1. LangChain의 기본 구조 이해
2. PromptTemplate으로 동적 프롬프트 생성
3. LCEL(LangChain Expression Language)의 파이프 연산자 `|` 사용

---

## 환경 설정

### 1. Python 가상환경 활성화

```bash
source venv/bin/activate  # Mac/Linux
# 또는
venv\Scripts\activate     # Windows
```

### 2. 환경 변수 설정

`.env` 파일을 생성하고 OpenAI API 키를 설정합니다:

```bash
cp .env.example .env
# .env 파일을 열어 OPENAI_API_KEY를 입력하세요
```

`.env` 파일 내용:
```
OPENAI_API_KEY=sk-your-api-key-here
```

---

## Step 1 실행

각 예제는 독립적으로 실행할 수 있습니다:

### 예제 1: 간단한 PromptTemplate (LLM 호출 없음)
```bash
python step1_example1_simple_prompt.py
```

### 예제 2: PromptTemplate + LLM 체인 (LLM 호출 있음)
```bash
python step1_example2_prompt_llm_chain.py
```

### 예제 3: 여러 입력으로 체인 반복 실행 (LLM 호출 있음)
```bash
python step1_example3_multiple_chains.py
```

### 실행 결과 예시

**예제 1 결과:**
```
==================================================
예제 1: 간단한 PromptTemplate
==================================================

생성된 프롬프트:
안녕하세요, 철수님! 오늘 날씨가 좋네요.

생성된 프롬프트 2:
안녕하세요, 영희님! 반갑습니다!
```

**예제 2 결과:**
```
==================================================
예제 2: PromptTemplate + LLM 체인
==================================================

[실행 중...]

LLM 응답:
민수님, 파이썬 프로그래밍에 관심이 있으시군요! 다음 추천사항을 참고해보세요:

1. 온라인 코딩 플랫폼 활용
2. 실전 프로젝트 만들기
3. 오픈소스 기여
...
```

**예제 3 결과:**
```
==================================================
예제 3: 여러 입력으로 체인 반복 실행
==================================================

[실행 중...]

대한민국: 대한민국의 수도는 서울입니다.
일본: 일본의 수도는 도쿄입니다.
프랑스: 프랑스의 수도는 파리입니다.
브라질: 브라질의 수도는 브라질리아입니다.
```

---

## 코드 설명

### 예제 1: 간단한 PromptTemplate

```python
from langchain.prompts import PromptTemplate

template = "안녕하세요, {name}님! {greeting}"
prompt = PromptTemplate(
    input_variables=["name", "greeting"],
    template=template
)

result = prompt.format(name="철수", greeting="오늘 날씨가 좋네요.")
```

**핵심 개념:**
- `PromptTemplate`: 변수를 포함한 프롬프트 템플릿
- `input_variables`: 템플릿에서 사용할 변수 목록
- `format()`: 변수에 값을 삽입하여 최종 프롬프트 생성

---

### 예제 2: PromptTemplate + LLM 체인

```python
from langchain_openai import ChatOpenAI

prompt = PromptTemplate(...)
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)

# LCEL 체인 구성
chain = prompt | llm

# 체인 실행
response = chain.invoke({"name": "민수", "interest": "파이썬"})
```

**핵심 개념:**
- `|` (파이프 연산자): LCEL의 핵심, Runnable 객체들을 연결
- `chain.invoke()`: 체인 실행 및 결과 반환
- LLM의 응답은 `AIMessage` 객체로 반환되며, `.content`로 텍스트 접근

---

### 예제 3: 체인 재사용

```python
chain = prompt | llm

for country in ["대한민국", "일본", "프랑스"]:
    response = chain.invoke({"country": country})
    print(response.content)
```

**핵심 개념:**
- 한 번 정의한 체인을 다양한 입력값으로 재사용 가능
- 효율적인 프롬프트 관리 및 코드 재사용성 향상

---

## 주요 학습 포인트

### 1. Runnable 인터페이스
- LangChain의 모든 주요 컴포넌트는 `Runnable` 인터페이스를 구현
- `invoke()`, `stream()`, `batch()` 등의 메서드 제공
- 일관된 방식으로 체인 실행 가능

### 2. LCEL (LangChain Expression Language)
- 파이프 연산자 `|`로 컴포넌트 연결
- 간결하고 읽기 쉬운 코드
- 예: `prompt | llm | parser`

### 3. PromptTemplate의 장점
- 프롬프트 재사용성
- 변수를 통한 동적 생성
- 코드와 프롬프트 분리로 유지보수 용이

---

## 다음 단계

Step 2에서는 **Output Parsing**을 학습합니다:
- LLM 출력을 구조화된 데이터(JSON, Dict)로 변환
- Pydantic 모델을 활용한 타입 안전성 확보

---

## 참고 자료

- [LangChain 공식 문서](https://python.langchain.com/)
- [PromptTemplate 가이드](https://python.langchain.com/docs/modules/model_io/prompts/)
- [LCEL 소개](https://python.langchain.com/docs/expression_language/)
