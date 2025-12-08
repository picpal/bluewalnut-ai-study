"""
Step 2 - 예제 2: PydanticOutputParser + LLM 체인

목표:
- PydanticOutputParser를 LLM 체인에 통합
- LLM 응답을 구조화된 Pydantic 객체로 변환
- partial_variables로 포맷 지시문 주입
"""

import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from langchain_anthropic import ChatAnthropic

# 환경 변수 로드
load_dotenv()

print("=" * 50)
print("예제 2: PydanticOutputParser + LLM 체인")
print("=" * 50)
print()

# 1. Pydantic 모델 정의
class MovieInfo(BaseModel):
    """영화 정보를 담는 Pydantic 모델"""
    title: str = Field(description="영화 제목")
    director: str = Field(description="감독 이름")
    year: int = Field(description="개봉 연도")
    genre: str = Field(description="장르")

print("📌 1. Pydantic 모델 정의 완료")
print()

# 2. PydanticOutputParser 생성
parser = PydanticOutputParser(pydantic_object=MovieInfo)

print("📌 2. PydanticOutputParser 생성 완료")
print()

# 3. 포맷 지시문 확인
format_instructions = parser.get_format_instructions()
print("📌 3. Parser가 생성한 포맷 지시문:")
print("-" * 50)
print(format_instructions)
print("-" * 50)
print()

# 4. PromptTemplate 정의 (포맷 지시문 포함)
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

print("📌 4. PromptTemplate 생성 완료")
print("   - input_variables: ['movie_query']")
print("   - partial_variables: format_instructions (자동 주입)")
print()

# 5. LLM 설정
llm = ChatAnthropic(
    model="claude-3-haiku-20240307",
    temperature=0  # 일관된 답변
)

print("📌 5. LLM 설정 완료 (claude-3-haiku-20240307)")
print()

# 6. 체인 구성: prompt | llm | parser
chain = prompt | llm | parser

print("📌 6. 체인 구성 완료")
print("   chain = prompt | llm | parser")
print()

# 7. 체인 실행 (사용자 확인 필요)
print("📌 7. 체인 실행 준비")
print()
print("⚠️  이제 LLM API를 호출합니다.")
print()

input("Enter를 눌러 계속 진행하세요...")
print()

print("[실행 중...]")
print()

# 실행
result = chain.invoke({"movie_query": "인셉션"})

# 8. 결과 확인
print("=" * 50)
print("📌 8. 실행 결과")
print("=" * 50)
print()

print(f"✅ 타입: {type(result)}")
print(f"✅ 객체: {result}")
print()

print("📌 구조화된 데이터 접근:")
print(f"  - 제목: {result.title}")
print(f"  - 감독: {result.director}")
print(f"  - 개봉 연도: {result.year}")
print(f"  - 장르: {result.genre}")
print()

print("📌 딕셔너리 변환:")
print(f"  {result.dict()}")
print()

print("=" * 50)
print("✅ 예제 2 완료!")
print()
print("핵심 학습 포인트:")
print("1. PydanticOutputParser로 LLM 응답 파싱")
print("2. partial_variables로 포맷 지시문 자동 주입")
print("3. chain = prompt | llm | parser 구성")
print("4. 결과는 Pydantic 객체 (속성 접근 가능)")
print("=" * 50)
