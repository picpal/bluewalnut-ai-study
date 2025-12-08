# Step 2 - 예제 3 실행 결과

## 실행 일시
2025-12-07

## 사용 모델
- **LLM**: Anthropic Claude 3 Haiku (claude-3-haiku-20240307)
- **Temperature**: 0.3 (약간의 창의성)

---

## 예제 목표

**복잡한 구조 (리스트 포함) + 체인 재사용**
- `List[Movie]` 타입으로 여러 영화를 한 번에 파싱
- 중첩된 Pydantic 모델 구조
- 여러 입력으로 체인 재사용

---

## 코드 구조

### 1. 중첩된 Pydantic 모델 정의

```python
from pydantic import BaseModel, Field
from typing import List

# 개별 영화 정보 모델
class Movie(BaseModel):
    """개별 영화 정보"""
    title: str = Field(description="영화 제목")
    director: str = Field(description="감독 이름")
    year: int = Field(description="개봉 연도")

# 영화 추천 리스트 모델 (중첩 구조!)
class MovieRecommendations(BaseModel):
    """영화 추천 리스트"""
    category: str = Field(description="추천 카테고리")
    movies: List[Movie] = Field(description="추천 영화 리스트 (3개)")
```

**핵심:**
- `Movie`: 개별 영화 정보를 담는 기본 모델
- `MovieRecommendations`: 카테고리 + **영화 리스트**를 포함하는 상위 모델
- `List[Movie]`: Python의 타입 힌트로 리스트 구조 정의

---

### 2. PromptTemplate 정의

```python
template = """당신은 영화 추천 전문가입니다.

다음 카테고리에 맞는 영화를 정확히 3개 추천해주세요:
카테고리: {category}

각 영화에 대해 제목, 감독, 개봉 연도를 포함해주세요.

{format_instructions}
"""

prompt = PromptTemplate(
    input_variables=["category"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
    template=template
)
```

**핵심:**
- "정확히 3개 추천"이라고 명시
- Parser가 생성한 JSON 스키마에 `List[Movie]` 구조 포함

---

### 3. 체인 구성 및 반복 실행

```python
# 체인 구성 (한 번만!)
chain = prompt | llm | parser

# 여러 카테고리로 재사용
categories = ["한국 영화", "SF 영화"]

results = []
for category in categories:
    result = chain.invoke({"category": category})
    results.append(result)
```

**Step 1 예제 3과 동일한 패턴:**
- 체인을 한 번 정의
- 여러 입력값으로 반복 실행

---

## 실행 결과

### 첫 번째 실행: 한국 영화

**입력:**
```python
result = chain.invoke({"category": "한국 영화"})
```

**LLM 응답 (내부 JSON):**
```json
{
  "category": "한국 영화",
  "movies": [
    {
      "title": "기생충",
      "director": "봉준호",
      "year": 2019
    },
    {
      "title": "올드보이",
      "director": "박찬욱",
      "year": 2003
    },
    {
      "title": "밀양",
      "director": "이창동",
      "year": 2007
    }
  ]
}
```

**파싱된 결과:**
```
✅ 카테고리: 한국 영화
✅ 추천 영화 개수: 3

  1. 기생충
     - 감독: 봉준호
     - 개봉 연도: 2019

  2. 올드보이
     - 감독: 박찬욱
     - 개봉 연도: 2003

  3. 밀양
     - 감독: 이창동
     - 개봉 연도: 2007
```

**구조화된 데이터 접근:**
```python
print(result.category)           # "한국 영화"
print(len(result.movies))        # 3
print(result.movies[0].title)    # "기생충"
print(result.movies[0].director) # "봉준호"
print(result.movies[0].year)     # 2019

# 리스트 반복
for movie in result.movies:
    print(f"{movie.title} ({movie.year}) - {movie.director}")
```

---

### 두 번째 실행: SF 영화

**입력:**
```python
result = chain.invoke({"category": "SF 영화"})
```

**LLM 응답 (내부 JSON):**
```json
{
  "category": "SF 영화",
  "movies": [
    {
      "title": "Blade Runner 2049",
      "director": "Denis Villeneuve",
      "year": 2017
    },
    {
      "title": "Interstellar",
      "director": "Christopher Nolan",
      "year": 2014
    },
    {
      "title": "Arrival",
      "director": "Denis Villeneuve",
      "year": 2016
    }
  ]
}
```

**파싱된 결과:**
```
✅ 카테고리: SF 영화
✅ 추천 영화 개수: 3

  1. Blade Runner 2049
     - 감독: Denis Villeneuve
     - 개봉 연도: 2017

  2. Interstellar
     - 감독: Christopher Nolan
     - 개봉 연도: 2014

  3. Arrival
     - 감독: Denis Villeneuve
     - 개봉 연도: 2016
```

---

### 전체 결과 요약

```
[한국 영화]
  - 기생충 (2019) - 봉준호
  - 올드보이 (2003) - 박찬욱
  - 밀양 (2007) - 이창동

[SF 영화]
  - Blade Runner 2049 (2017) - Denis Villeneuve
  - Interstellar (2014) - Christopher Nolan
  - Arrival (2016) - Denis Villeneuve
```

---

## 전체 흐름 분석

```
1. 입력 (첫 번째)
   {"category": "한국 영화"}
        ↓
2. PromptTemplate
   "카테고리: 한국 영화 ... {format_instructions}"
        ↓
3. LLM (Claude Haiku)
   JSON 리스트 구조로 응답:
   {"category": "한국 영화", "movies": [{...}, {...}, {...}]}
        ↓
4. PydanticOutputParser
   JSON → MovieRecommendations 객체로 파싱
   - result.category = "한국 영화"
   - result.movies = [Movie(...), Movie(...), Movie(...)]
        ↓
5. 결과 활용
   for movie in result.movies:
       print(movie.title)
        ↓
   (두 번째 입력으로 반복)
```

---

## 핵심 학습 포인트

### 1. List[T] 타입 사용

```python
class MovieRecommendations(BaseModel):
    movies: List[Movie]  # ← 리스트 타입!
```

**의미:**
- Python의 타입 힌트 `List[Movie]`
- `movies` 필드는 `Movie` 객체들의 리스트
- Pydantic이 자동으로 각 요소를 `Movie` 객체로 변환

**결과:**
```python
result.movies          # [Movie(...), Movie(...), Movie(...)]
result.movies[0]       # Movie(title='기생충', director='봉준호', year=2019)
result.movies[0].title # "기생충"
```

---

### 2. 중첩된 Pydantic 모델

```python
# 내부 모델
class Movie(BaseModel):
    title: str
    director: str
    year: int

# 외부 모델 (Movie를 포함)
class MovieRecommendations(BaseModel):
    category: str
    movies: List[Movie]  # ← Movie 모델을 포함!
```

**장점:**
- 복잡한 데이터 구조를 계층적으로 표현
- 각 레벨에서 독립적인 검증
- 코드 재사용성 향상

---

### 3. Parser가 생성한 JSON 스키마

Parser는 중첩 구조를 포함한 JSON 스키마를 자동 생성:

```json
{
  "properties": {
    "category": {"type": "string"},
    "movies": {
      "type": "array",
      "items": {
        "properties": {
          "title": {"type": "string"},
          "director": {"type": "string"},
          "year": {"type": "integer"}
        },
        "required": ["title", "director", "year"]
      }
    }
  },
  "required": ["category", "movies"]
}
```

**LLM은 이 스키마를 보고 정확한 구조로 응답!**

---

### 4. 리스트 데이터 활용

```python
# 길이 확인
print(len(result.movies))  # 3

# 인덱스 접근
first_movie = result.movies[0]
print(first_movie.title)   # "기생충"

# 반복문
for movie in result.movies:
    print(f"{movie.title} ({movie.year})")

# 리스트 컴프리헨션
titles = [movie.title for movie in result.movies]
print(titles)  # ['기생충', '올드보이', '밀양']

# 필터링
recent_movies = [m for m in result.movies if m.year >= 2010]
```

---

### 5. 체인 재사용 (Step 1과 동일한 패턴)

```python
# ✅ 좋은 방법: 체인을 한 번만 정의
chain = prompt | llm | parser

categories = ["한국 영화", "SF 영화"]
for category in categories:
    result = chain.invoke({"category": category})
    # 각 카테고리별로 3개 영화 받음
```

**장점:**
- 코드 효율성
- 메모리 절약
- 일관된 처리

---

## 예제 2 vs 예제 3 비교

### 예제 2: 단일 객체

```python
class MovieInfo(BaseModel):
    title: str
    director: str
    year: int
    genre: str

result = chain.invoke({"movie_query": "인셉션"})
# result는 MovieInfo 객체 (단일)
print(result.title)  # "Inception"
```

### 예제 3: 리스트 구조

```python
class MovieRecommendations(BaseModel):
    category: str
    movies: List[Movie]  # ← 리스트!

result = chain.invoke({"category": "한국 영화"})
# result.movies는 Movie 객체의 리스트
for movie in result.movies:
    print(movie.title)
```

---

## 실전 활용 예시

### 1. 여러 항목 추출

```python
class Products(BaseModel):
    category: str
    items: List[Product]

# "스마트폰 추천 5개" 요청
result = chain.invoke({"category": "스마트폰"})
for product in result.items:
    print(f"{product.name}: {product.price}원")
```

### 2. 데이터 분석 결과

```python
class AnalysisResult(BaseModel):
    summary: str
    insights: List[Insight]

result = chain.invoke({"data": sales_data})
for insight in result.insights:
    print(f"- {insight.description}")
```

### 3. 다단계 추천

```python
class Recommendations(BaseModel):
    user: str
    items: List[Item]

users = ["철수", "영희", "민수"]
for user in users:
    result = chain.invoke({"user": user})
    print(f"{user}님 추천:")
    for item in result.items:
        print(f"  - {item.name}")
```

---

## temperature=0.3의 의미

```python
llm = ChatAnthropic(
    model="claude-3-haiku-20240307",
    temperature=0.3  # 약간의 창의성
)
```

**예제 2 vs 예제 3:**

| 예제 | temperature | 이유 |
|------|-------------|------|
| 예제 2 | 0 | 영화 정보는 정확한 사실 (인셉션 = 크리스토퍼 놀란) |
| 예제 3 | 0.3 | 영화 추천은 약간의 다양성 필요 |

**temperature=0.3 효과:**
- 매번 약간 다른 영화 추천 가능
- 하지만 너무 창의적이지는 않음 (적절한 균형)

---

## Step 2 전체 요약

### 예제 1: Pydantic 기본
```python
movie = MovieInfo(title="인셉션", director="놀란", year=2010)
# BaseModel의 검증 기능 학습
```

### 예제 2: 단일 객체 파싱
```python
chain = prompt | llm | parser
result = chain.invoke({"movie_query": "인셉션"})
# result.title = "Inception"
```

### 예제 3: 리스트 구조 파싱
```python
chain = prompt | llm | parser
result = chain.invoke({"category": "한국 영화"})
# result.movies = [Movie(...), Movie(...), Movie(...)]
for movie in result.movies:
    print(movie.title)
```

---

## 다음 단계

**Step 3: Function Calling — 단일 함수**
- LLM의 Function Calling 기능
- Python 함수를 LLM에 바인딩
- LLM이 언제 함수를 호출할지 판단

예시:
```python
# 날씨 조회 함수
def get_weather(city: str) -> str:
    return f"{city}의 날씨는 맑음"

# LLM이 자동으로 함수 호출 판단
"서울 날씨 알려줘" → get_weather("서울") 호출
```

---

## 요약

예제 3을 통해 배운 것:
1. ✅ `List[Movie]` 타입으로 리스트 구조 정의
2. ✅ 중첩된 Pydantic 모델 (MovieRecommendations > Movie)
3. ✅ Parser가 복잡한 JSON 스키마 자동 생성
4. ✅ LLM이 리스트 구조로 응답
5. ✅ 파싱된 리스트를 for 문으로 반복 처리
6. ✅ 체인 재사용으로 여러 카테고리 처리
