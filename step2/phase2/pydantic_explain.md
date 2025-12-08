# PydanticOutputParser 개념 정리

## PydanticOutputParser란?

**LLM의 자유로운 텍스트 응답을 구조화된 데이터로 변환**하는 LangChain 컴포넌트입니다.

---

## 왜 필요한가? (문제점)

### Step 1의 한계
```python
# Step 1에서 배운 방식
response = chain.invoke({"country": "프랑스"})
print(response.content)
# 출력: "프랑스의 수도는 파리입니다."
```

**문제점:**
- 응답이 **자유로운 텍스트** 형태
- 데이터를 추출하려면 **문자열 파싱** 필요
- 프로그래밍적으로 활용하기 어려움

```python
# 이런 식으로 직접 파싱해야 함 (불안정!)
capital = response.content.split("수도는 ")[1].split("입니다")[0]  # "파리"
```

### 원하는 형태
```python
# 구조화된 데이터로 받고 싶음
{
    "country": "프랑스",
    "capital": "파리",
    "continent": "유럽"
}

# 이렇게 사용 가능
print(result.capital)  # "파리"
print(result.continent)  # "유럽"
```

---

## Pydantic이란?

Python의 **데이터 검증 라이브러리**입니다.

```python
from pydantic import BaseModel

class CountryInfo(BaseModel):
    country: str
    capital: str
    continent: str

# 타입 안전성 보장
info = CountryInfo(
    country="프랑스",
    capital="파리",
    continent="유럽"
)

print(info.capital)  # "파리"
print(info.dict())    # {"country": "프랑스", "capital": "파리", "continent": "유럽"}
```

**장점:**
- 타입 체크 자동화
- 유효성 검증 (예: 필수 필드 누락 시 에러)
- IDE 자동완성 지원

---

## PydanticOutputParser의 동작 원리

### 1단계: Pydantic 모델 정의
```python
from pydantic import BaseModel, Field

class CountryInfo(BaseModel):
    country: str = Field(description="국가명")
    capital: str = Field(description="수도명")
    continent: str = Field(description="대륙명")
```

### 2단계: Parser 생성
```python
from langchain.output_parsers import PydanticOutputParser

parser = PydanticOutputParser(pydantic_object=CountryInfo)
```

### 3단계: 프롬프트에 **포맷 지시문 자동 추가**
```python
# parser가 자동으로 생성하는 지시문
format_instructions = parser.get_format_instructions()
print(format_instructions)
```

**출력 예시:**
```
The output should be formatted as a JSON instance that conforms to the JSON schema below.

{"country": "국가명", "capital": "수도명", "continent": "대륙명"}
```

이 지시문을 프롬프트에 추가하면 LLM이 **자동으로 JSON 형태로 응답**합니다!

### 4단계: 체인 구성
```python
template = """
{country}의 수도와 대륙 정보를 알려주세요.

{format_instructions}
"""

prompt = PromptTemplate(
    input_variables=["country"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
    template=template
)

# Step 1과 비교: parser 추가!
chain = prompt | llm | parser
```

**핵심 차이:**
- Step 1: `prompt | llm` → 텍스트 응답
- Step 2: `prompt | llm | parser` → 구조화된 객체

### 5단계: 실행 및 파싱
```python
result = chain.invoke({"country": "프랑스"})

# result는 CountryInfo 객체!
print(type(result))          # <class 'CountryInfo'>
print(result.capital)        # "파리" (속성 접근)
print(result.dict())         # {"country": "프랑스", "capital": "파리", "continent": "유럽"}
```

---

## 전체 흐름 요약

```
1. 사용자 입력: {"country": "프랑스"}
        ↓
2. PromptTemplate: "프랑스의 수도와 대륙 정보를... (JSON 포맷 지시문 포함)"
        ↓
3. LLM: {"country": "프랑스", "capital": "파리", "continent": "유럽"}  ← JSON 문자열
        ↓
4. PydanticOutputParser: JSON 문자열 → CountryInfo 객체로 변환
        ↓
5. 최종 결과: result.capital = "파리"
```

---

## Before vs After

### Before (Step 1)
```python
chain = prompt | llm
response = chain.invoke({"country": "프랑스"})

# 텍스트 응답
print(response.content)  # "프랑스의 수도는 파리입니다."

# 데이터 추출이 어려움
capital = response.content.split("수도는 ")[1].split("입니다")[0]
```

### After (Step 2)
```python
chain = prompt | llm | parser
result = chain.invoke({"country": "프랑스"})

# 구조화된 객체
print(result.capital)     # "파리"
print(result.continent)   # "유럽"

# 타입 안전성 보장
if result.continent == "유럽":
    print("유럽 국가입니다")
```

---

## 핵심 정리

1. **Pydantic**: Python 데이터 검증 라이브러리 (타입 체크 + 유효성 검증)
2. **PydanticOutputParser**: LLM 텍스트 응답 → Pydantic 객체로 변환
3. **동작 원리**:
   - 프롬프트에 JSON 포맷 지시문 자동 추가
   - LLM이 JSON 형태로 응답
   - Parser가 JSON 문자열을 Pydantic 객체로 변환
4. **장점**:
   - 구조화된 데이터 활용 가능
   - 타입 안전성 보장
   - 코드 가독성 향상

---

## Step 2에서 학습할 내용

- Pydantic 모델 정의 방법
- PydanticOutputParser 사용법
- `partial_variables`를 통한 포맷 지시문 주입
- 파싱 실패 시 에러 핸들링
- 리스트를 포함한 복잡한 구조 파싱
