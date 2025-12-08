"""
Step 2 - 예제 3: 복잡한 구조 (리스트 포함) + 반복 실행

목표:
- 리스트를 포함한 복잡한 Pydantic 모델 정의
- 여러 입력으로 체인 재사용
- 실전적인 데이터 구조 활용
"""

import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import List
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from langchain_anthropic import ChatAnthropic

# 환경 변수 로드
load_dotenv()

print("=" * 50)
print("예제 3: 복잡한 구조 (리스트 포함)")
print("=" * 50)
print()

# 1. 개별 영화 정보 모델
class Movie(BaseModel):
    """개별 영화 정보"""
    title: str = Field(description="영화 제목")
    director: str = Field(description="감독 이름")
    year: int = Field(description="개봉 연도")

# 2. 영화 추천 리스트 모델
class MovieRecommendations(BaseModel):
    """영화 추천 리스트"""
    category: str = Field(description="추천 카테고리")
    movies: List[Movie] = Field(description="추천 영화 리스트 (3개)")

print("📌 1. 복잡한 Pydantic 모델 정의 완료")
print("   - Movie: 개별 영화 정보")
print("   - MovieRecommendations: 영화 리스트 포함")
print()

# 3. PydanticOutputParser 생성
parser = PydanticOutputParser(pydantic_object=MovieRecommendations)

print("📌 2. PydanticOutputParser 생성 완료")
print()

# 4. PromptTemplate 정의
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

print("📌 3. PromptTemplate 생성 완료")
print()

# 5. LLM 설정
llm = ChatAnthropic(
    model="claude-3-haiku-20240307",
    temperature=0.3  # 약간의 창의성
)

print("📌 4. LLM 설정 완료 (temperature=0.3)")
print()

# 6. 체인 구성
chain = prompt | llm | parser

print("📌 5. 체인 구성 완료")
print("   chain = prompt | llm | parser")
print()

# 7. 여러 카테고리로 반복 실행
categories = ["한국 영화", "SF 영화"]

print(f"📌 6. {len(categories)}개 카테고리로 체인 반복 실행 준비")
for i, cat in enumerate(categories, 1):
    print(f"   {i}. {cat}")
print()

print("⚠️  이제 LLM API를 호출합니다.")
print()

input("Enter를 눌러 계속 진행하세요...")
print()

# 8. 반복 실행
results = []

for category in categories:
    print("=" * 50)
    print(f"📌 카테고리: {category}")
    print("=" * 50)
    print()
    print("[실행 중...]")
    print()

    result = chain.invoke({"category": category})
    results.append(result)

    print(f"✅ 카테고리: {result.category}")
    print(f"✅ 추천 영화 개수: {len(result.movies)}")
    print()

    for i, movie in enumerate(result.movies, 1):
        print(f"  {i}. {movie.title}")
        print(f"     - 감독: {movie.director}")
        print(f"     - 개봉 연도: {movie.year}")
        print()

    print()

# 9. 전체 결과 요약
print("=" * 50)
print("📌 전체 결과 요약")
print("=" * 50)
print()

for result in results:
    print(f"[{result.category}]")
    for movie in result.movies:
        print(f"  - {movie.title} ({movie.year}) - {movie.director}")
    print()

print("=" * 50)
print("✅ 예제 3 완료!")
print()
print("핵심 학습 포인트:")
print("1. List[Movie] 타입으로 리스트 구조 정의")
print("2. 중첩된 Pydantic 모델 (MovieRecommendations > Movie)")
print("3. 체인 재사용으로 여러 카테고리 처리")
print("4. result.movies로 리스트 접근 및 반복")
print("=" * 50)
