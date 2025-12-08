# Step 2 - 예제 1 실행 결과

## 실행 일시
2025-12-07

## 예제 목표
**Pydantic 모델 기본 사용법 학습**
- BaseModel을 상속받은 클래스 정의
- 자동 타입 검증 및 변환
- 유효성 검증 (Field 제약)
- 필수 필드 검증
- dict() 변환

---

## 실행 결과

### 1. Pydantic 모델 정의

```python
from pydantic import BaseModel, Field

class MovieInfo(BaseModel):
    """영화 정보를 담는 Pydantic 모델"""
    title: str = Field(description="영화 제목")
    director: str = Field(description="감독 이름")
    year: int = Field(description="개봉 연도")
    rating: float = Field(description="평점 (0.0 ~ 10.0)", ge=0.0, le=10.0)
```

**핵심:**
- `BaseModel` 상속 → 자동 검증 기능 활성화
- 타입 어노테이션 (`:` 뒤): `title: str`, `year: int`
- `Field()`: 추가 메타데이터 및 제약 조건 (ge=0.0, le=10.0)

---

### 2. 정상적인 객체 생성

**입력:**
```python
movie1 = MovieInfo(
    title="인셉션",
    director="크리스토퍼 놀란",
    year=2010,
    rating=8.8
)
```

**출력:**
```
✅ 객체 생성 성공!

영화 제목: 인셉션
감독: 크리스토퍼 놀란
개봉 연도: 2010
평점: 8.8
```

---

### 3. dict() 변환

**코드:**
```python
movie_dict = movie1.dict()
print(f"타입: {type(movie_dict)}")
print(f"내용: {movie_dict}")
```

**출력:**
```
타입: <class 'dict'>
내용: {'title': '인셉션', 'director': '크리스토퍼 놀란', 'year': 2010, 'rating': 8.8}
```

**의미:**
- Pydantic 객체 → Python 딕셔너리로 변환
- JSON, DB, API 등 외부 시스템과 연동할 때 필요

---

### 4. 타입 자동 변환 테스트

**테스트 코드:**
```python
movie2 = MovieInfo(
    title="타이타닉",
    director="제임스 카메론",
    year="1997",  # ← 문자열!
    rating=7.9
)
```

**결과:**
```
✅ 자동 변환 성공: year = 1997 (타입: <class 'int'>)
```

**의미:**
- 문자열 `"1997"` → 정수 `1997`로 자동 변환
- Pydantic이 타입 변환 가능한 경우 자동 처리

---

### 5. 유효성 검증 실패 (범위 초과)

**테스트 코드:**
```python
try:
    movie3 = MovieInfo(
        title="아바타",
        director="제임스 카메론",
        year=2009,
        rating=15.0  # ← 10.0 초과!
    )
except ValidationError as e:
    print("❌ 검증 실패")
```

**결과:**
```
❌ 검증 실패:
  - 필드: rating
  - 에러 타입: less_than_equal
  - 메시지: Input should be less than or equal to 10
```

**의미:**
- `rating=15.0`이 `le=10.0` 제약 위반
- `ValidationError` 발생으로 객체 생성 실패

---

### 6. 필수 필드 누락 테스트

**테스트 코드:**
```python
try:
    movie4 = MovieInfo(
        director="봉준호",
        year=2019,
        rating=8.6
        # title 필드 누락!
    )
except ValidationError as e:
    print("❌ 검증 실패")
```

**결과:**
```
❌ 검증 실패:
  - 누락된 필드: title
  - 메시지: Field required
```

**의미:**
- `title` 필드는 필수인데 제공되지 않음
- `ValidationError` 발생으로 객체 생성 실패

---

## 검증 흐름 정리

```
객체 생성 시도
    ↓
BaseModel이 자동 검증 실행
    ↓
    ├─ 타입 검증 (str, int, float)
    ├─ 타입 변환 시도 (가능한 경우)
    ├─ 유효성 검증 (ge, le 등)
    └─ 필수 필드 검증
        ↓
        ├─ 모든 검증 통과 → 객체 생성 ✅
        └─ 검증 실패 → ValidationError 발생 ❌
```

---

## 핵심 학습 포인트

### 1. BaseModel 상속
```python
class MovieInfo(BaseModel):
```
- Pydantic 기능 활성화
- 자동 검증, 타입 변환, 직렬화 기능 제공

### 2. 타입 어노테이션
```python
title: str
year: int
rating: float
```
- 콜론(`:`) 뒤에 타입 지정
- Python 타입 힌트 문법

### 3. Field()로 제약 조건
```python
rating: float = Field(ge=0.0, le=10.0)
```
- `ge`: greater than or equal (이상)
- `le`: less than or equal (이하)
- `description`: 필드 설명

### 4. 자동 타입 변환
- 문자열 `"1997"` → 정수 `1997`
- 변환 가능한 경우 자동 처리
- 변환 불가능한 경우 ValidationError

### 5. ValidationError
```python
try:
    movie = MovieInfo(...)
except ValidationError as e:
    for error in e.errors():
        print(error)
```
- 검증 실패 시 발생하는 예외
- `e.errors()`로 상세 에러 정보 확인

### 6. dict() 변환
```python
movie_dict = movie1.dict()
```
- Pydantic 객체 → Python 딕셔너리
- JSON, DB, API 연동 시 필요

---

## Pydantic vs 일반 딕셔너리

| 항목 | Pydantic 객체 | Python 딕셔너리 |
|------|---------------|-----------------|
| 타입 검증 | ✅ 자동 | ❌ 없음 |
| 유효성 검증 | ✅ Field 제약 | ❌ 없음 |
| 접근 방식 | `movie.title` | `movie_dict['title']` |
| JSON 변환 | `.dict()` 필요 | `json.dumps()` 직접 가능 |
| IDE 지원 | ✅ 자동완성 | ❌ 제한적 |

---

## 다음 단계

예제 2에서는:
- **PydanticOutputParser**를 LLM 체인에 통합
- LLM의 텍스트 응답을 Pydantic 객체로 자동 변환
- `prompt | llm | parser` 체인 구성

```python
# 예제 2 미리보기
chain = prompt | llm | parser

result = chain.invoke({"movie_query": "인셉션"})
# result는 MovieInfo 객체!
print(result.title)     # "인셉션"
print(result.director)  # "크리스토퍼 놀란"
```

---

## 참고 사항

**Pydantic V2 변경사항:**
- `.dict()` → `.model_dump()` (권장)
- `.json()` → `.model_dump_json()` (권장)

현재 예제는 학습 목적으로 기존 `.dict()` 메서드를 사용했지만, 실전에서는 `.model_dump()`를 권장합니다.
