# Step 2 - 예제 2 실행 결과

## 실행 일시
2025-12-07

## 사용 모델
- **LLM**: Anthropic Claude 3 Haiku (claude-3-haiku-20240307)
- **Temperature**: 0 (일관된 답변)

---

## 예제 목표

**PydanticOutputParser + LLM 체인 통합**
- LLM 응답을 구조화된 Pydantic 객체로 변환
- `partial_variables`로 포맷 지시문 자동 주입
- `prompt | llm | parser` 체인 구성

---

## 코드 구조

### 1. Pydantic 모델 정의

```python
from pydantic import BaseModel, Field

class MovieInfo(BaseModel):
    """영화 정보를 담는 Pydantic 모델"""
    title: str = Field(description="영화 제목")
    director: str = Field(description="감독 이름")
    year: int = Field(description="개봉 연도")
    genre: str = Field(description="장르")
```

---

### 2. PydanticOutputParser 생성

```python
from langchain.output_parsers import PydanticOutputParser

parser = PydanticOutputParser(pydantic_object=MovieInfo)
```

---

### 3. Parser가 생성한 포맷 지시문

Parser는 자동으로 LLM에게 전달할 **JSON 포맷 지시문**을 생성합니다:

```
The output should be formatted as a JSON instance that conforms to the JSON schema below.

As an example, for the schema {"properties": {"foo": {"title": "Foo", "description": "a list of strings", "type": "array", "items": {"type": "string"}}}, "required": ["foo"]}
the object {"foo": ["bar", "baz"]} is a well-formatted instance of the schema. The object {"properties": {"foo": ["bar", "baz"]}} is not well-formatted.

Here is the output schema:
```
```json
{
  "description": "영화 정보를 담는 Pydantic 모델",
  "properties": {
    "title": {"description": "영화 제목", "title": "Title", "type": "string"},
    "director": {"description": "감독 이름", "title": "Director", "type": "string"},
    "year": {"description": "개봉 연도", "title": "Year", "type": "integer"},
    "genre": {"description": "장르", "title": "Genre", "type": "string"}
  },
  "required": ["title", "director", "year", "genre"]
}
```

**핵심:**
- Parser가 Pydantic 모델 구조를 분석해서 **JSON 스키마 자동 생성**
- LLM에게 "이 스키마에 맞춰서 응답하라"고 지시
- 개발자는 직접 작성할 필요 없음!

---

### 4. PromptTemplate 정의 (포맷 지시문 포함)

```python
from langchain.prompts import PromptTemplate

template = """당신은 영화 정보 제공 어시스턴트입니다.

사용자가 요청한 영화에 대해 다음 정보를 제공해주세요:
- 제목
- 감독
- 개봉 연도
- 장르

영화: {movie_query}

{format_instructions}
"""

prompt = PromptTemplate(
    input_variables=["movie_query"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
    template=template
)
```

**핵심:**
- `partial_variables`: 미리 정해진 변수 값을 템플릿에 주입
- `parser.get_format_instructions()`로 포맷 지시문을 자동으로 프롬프트에 포함

---

### 5. 체인 구성

```python
from langchain_anthropic import ChatAnthropic

llm = ChatAnthropic(
    model="claude-3-haiku-20240307",
    temperature=0
)

# Step 1: prompt | llm
# Step 2: prompt | llm | parser ← 핵심 차이!
chain = prompt | llm | parser
```

**Step 1 vs Step 2:**

| 단계 | 체인 구성 | 결과 타입 |
|------|-----------|-----------|
| Step 1 | `prompt \| llm` | `AIMessage` (텍스트) |
| Step 2 | `prompt \| llm \| parser` | `MovieInfo` (Pydantic 객체) |

---

## 실행 결과

### 입력
```python
result = chain.invoke({"movie_query": "인셉션"})
```

### LLM이 받은 최종 프롬프트

```
당신은 영화 정보 제공 어시스턴트입니다.

사용자가 요청한 영화에 대해 다음 정보를 제공해주세요:
- 제목
- 감독
- 개봉 연도
- 장르

영화: 인셉션

The output should be formatted as a JSON instance that conforms to the JSON schema below.
...
{"description": "영화 정보를 담는 Pydantic 모델", "properties": {...}, "required": [...]}
```

### LLM 응답 (내부 JSON)

LLM은 포맷 지시문에 따라 JSON 형태로 응답:

```json
{
  "title": "Inception",
  "director": "Christopher Nolan",
  "year": 2010,
  "genre": "Science Fiction, Action, Adventure"
}
```

### Parser가 변환한 최종 결과

```python
✅ 타입: <class '__main__.MovieInfo'>
✅ 객체: title='Inception' director='Christopher Nolan' year=2010 genre='Science Fiction, Action, Adventure'
```

### 구조화된 데이터 접근

```python
print(result.title)     # "Inception"
print(result.director)  # "Christopher Nolan"
print(result.year)      # 2010
print(result.genre)     # "Science Fiction, Action, Adventure"
```

### 딕셔너리 변환

```python
result.dict()
# {'title': 'Inception', 'director': 'Christopher Nolan', 'year': 2010, 'genre': 'Science Fiction, Action, Adventure'}
```

---

## 전체 흐름 분석

```
1. 사용자 입력
   {"movie_query": "인셉션"}
        ↓
2. PromptTemplate
   "영화: 인셉션 ... {format_instructions}"
   → format_instructions에 JSON 스키마 포함
        ↓
3. LLM (Claude Haiku)
   프롬프트 분석 → JSON 형태로 응답
   {"title": "Inception", "director": "Christopher Nolan", ...}
        ↓
4. PydanticOutputParser
   JSON 문자열 → MovieInfo 객체로 파싱
        ↓
5. 최종 결과
   result.title = "Inception"
   result.director = "Christopher Nolan"
   result.year = 2010
   result.genre = "Science Fiction, Action, Adventure"
```

---

## Step 1 vs Step 2 비교

### Step 1: 텍스트 응답

```python
# Step 1 체인
chain = prompt | llm

response = chain.invoke({"country": "프랑스"})
print(response.content)
# 출력: "프랑스의 수도는 파리입니다."

# 데이터 추출이 어려움
capital = response.content.split("수도는 ")[1].split("입니다")[0]
```

### Step 2: 구조화된 응답

```python
# Step 2 체인
chain = prompt | llm | parser

result = chain.invoke({"movie_query": "인셉션"})
print(result.title)     # "Inception"
print(result.director)  # "Christopher Nolan"

# 속성 직접 접근 가능!
if result.year >= 2010:
    print("최근 영화입니다")
```

---

## 핵심 학습 포인트

### 1. PydanticOutputParser의 역할

- LLM의 **텍스트 응답 → Pydantic 객체**로 변환
- JSON 스키마를 자동으로 생성하여 LLM에게 전달
- 파싱 실패 시 자동으로 ValidationError 발생

### 2. partial_variables

```python
prompt = PromptTemplate(
    input_variables=["movie_query"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
    template=template
)
```

- 런타임에 변하지 않는 변수를 미리 주입
- `format_instructions`는 항상 동일하므로 partial_variables로 처리
- 사용자는 `movie_query`만 제공하면 됨

### 3. 체인 확장

```python
# Step 1
chain = prompt | llm

# Step 2
chain = prompt | llm | parser

# 향후 확장 가능
chain = prompt | llm | parser | custom_processor
```

- LCEL의 파이프 연산자로 쉽게 확장 가능
- 각 단계가 독립적으로 동작

### 4. 타입 안전성

```python
# ✅ IDE 자동완성 지원
result.title      # IDE가 자동으로 제안
result.director   # IDE가 자동으로 제안

# ✅ 타입 체크
if result.year > 2000:  # year가 int임을 보장
    print("21세기 영화")
```

---

## parser.get_format_instructions()의 역할

### Before (수동)

```python
template = """영화: {movie_query}

다음 JSON 형식으로 응답해주세요:
{
  "title": "영화 제목",
  "director": "감독 이름",
  "year": 개봉연도,
  "genre": "장르"
}
"""
```

**문제점:**
- 개발자가 직접 JSON 스키마 작성
- Pydantic 모델과 중복
- 수동 파싱 필요

### After (자동)

```python
template = """영화: {movie_query}

{format_instructions}
"""

prompt = PromptTemplate(
    input_variables=["movie_query"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
    template=template
)
```

**장점:**
- Parser가 자동으로 JSON 스키마 생성
- Pydantic 모델만 정의하면 됨
- 자동 파싱 + 검증

---

## 다음 단계

예제 3에서는:
- **리스트를 포함한 복잡한 구조** 파싱
- `List[Movie]` 타입 활용
- 여러 입력으로 체인 재사용

```python
# 예제 3 미리보기
class MovieRecommendations(BaseModel):
    category: str
    movies: List[Movie]  # ← 리스트!

result = chain.invoke({"category": "한국 영화"})
for movie in result.movies:
    print(movie.title)
```

---

## 요약

예제 2를 통해 배운 것:
1. ✅ PydanticOutputParser로 LLM 응답을 구조화된 객체로 변환
2. ✅ `parser.get_format_instructions()`로 JSON 스키마 자동 생성
3. ✅ `partial_variables`로 포맷 지시문 자동 주입
4. ✅ `prompt | llm | parser` 체인 구성
5. ✅ 결과는 Pydantic 객체 (타입 안전성, 속성 접근 가능)
