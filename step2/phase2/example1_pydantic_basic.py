"""
Step 2 - 예제 1: Pydantic 모델 기본 사용법

목표:
- Pydantic BaseModel의 기본 개념 이해
- 타입 검증 및 유효성 검사 체험
- LLM 호출 없이 Pydantic 자체 기능 학습
"""

from pydantic import BaseModel, Field, ValidationError

print("=" * 50)
print("예제 1: Pydantic 모델 기본 사용법")
print("=" * 50)
print()

# 1. Pydantic 모델 정의
class MovieInfo(BaseModel):
    """영화 정보를 담는 Pydantic 모델"""
    title: str = Field(description="영화 제목")
    director: str = Field(description="감독 이름")
    year: int = Field(description="개봉 연도")
    rating: float = Field(description="평점 (0.0 ~ 10.0)", ge=0.0, le=10.0)

print("📌 1. Pydantic 모델 정의 완료")
print()

# 2. 정상적인 객체 생성
print("📌 2. 정상적인 객체 생성")
movie1 = MovieInfo(
    title="인셉션",
    director="크리스토퍼 놀란",
    year=2010,
    rating=8.8
)

print(f"영화 제목: {movie1.title}")
print(f"감독: {movie1.director}")
print(f"개봉 연도: {movie1.year}")
print(f"평점: {movie1.rating}")
print()

# 3. dict() 변환 (Pydantic 객체는 JSON 직렬화 불가, dict()로 변환 후 JSON 직렬화)
# dict() 변환은 JSON, DB, API 등 외부 시스템과 연동할 때 필요
print("📌 3. dict() 변환")
movie_dict = movie1.dict()
print(f"타입: {type(movie_dict)}")
print(f"내용: {movie_dict}")
print()

#
#BaseModel을 상속받으면:
#  1. 객체 생성 시 자동으로 검증(validation) 실행
#  2. 검증 실패 시 ValidationError 발생
#  3. 검증 성공 시 정상 객체 생성
#  4. try-except로 잡아서 처리


# 4. 타입 검증 (에러 발생)
print("📌 4. 타입 검증 테스트")
try:
    # year에 문자열을 넣으면?
    movie2 = MovieInfo(
        title="타이타닉",
        director="제임스 카메론",
        year="1997",  # 문자열 → 자동 변환 시도
        rating=7.9
    )
    print(f"✅ 자동 변환 성공: year = {movie2.year} (타입: {type(movie2.year)})")
except ValidationError as e:
    print(f"❌ 검증 실패: {e}")
print()

# 5. 유효성 검증 (에러 발생)
print("📌 5. 유효성 검증 테스트 (rating 범위 초과)")
try:
    # rating이 0~10 범위를 벗어나면?
    movie3 = MovieInfo(
        title="아바타",
        director="제임스 카메론",
        year=2009,
        rating=15.0  # 10.0 초과!
    )
    print(f"✅ 생성 성공: {movie3.rating}")
except ValidationError as e:
    print(f"❌ 검증 실패:")
    for error in e.errors():
        print(f"  - 필드: {error['loc'][0]}")
        print(f"  - 에러 타입: {error['type']}")
        print(f"  - 메시지: {error['msg']}")
print()

# 6. 필수 필드 누락 (에러 발생)
print("📌 6. 필수 필드 누락 테스트")
try:
    # title 필드를 빠뜨리면?
    movie4 = MovieInfo(
        director="봉준호",
        year=2019,
        rating=8.6
    )
    print(f"✅ 생성 성공: {movie4.title}")
except ValidationError as e:
    print(f"❌ 검증 실패:")
    for error in e.errors():
        print(f"  - 누락된 필드: {error['loc'][0]}")
        print(f"  - 메시지: {error['msg']}")
print()

print("=" * 50)
print("✅ 예제 1 완료!")
print()
print("핵심 학습 포인트:")
print("1. Pydantic BaseModel로 데이터 구조 정의")
print("2. 자동 타입 변환 (예: 문자열 '1997' → 정수 1997)")
print("3. 유효성 검증 (예: ge=0.0, le=10.0)")
print("4. 필수 필드 검증")
print("5. dict()로 딕셔너리 변환")
print("=" * 50)
