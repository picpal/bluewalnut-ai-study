"""
Phase 5 - 예제 2: 병렬 파이프라인 (Parallel Pipeline)

목표:
- RunnableParallel로 여러 작업 동시 실행
- 독립적인 작업들을 병렬로 처리하여 성능 향상
- 기사를 입력받아 요약 + 감정 분석 + 키워드 추출을 동시에 수행
"""

import os
import time
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableParallel, RunnableLambda

# API 키 설정
os.environ["OPENAI_API_KEY"] = "your-api-key-here"

# LLM 초기화
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0
)

print("=" * 70)
print("Phase 5 - 예제 2: 병렬 파이프라인")
print("=" * 70)

# ============================================================================
# 1단계: 각 독립 작업 정의
# ============================================================================

print("\n[1단계] 각 독립 작업 정의\n")

# 작업 1: 요약
summarizer = (
    PromptTemplate.from_template(
        "다음 영문 기사를 3문장 이내로 요약해주세요:\n\n{article}"
    )
    | llm
    | StrOutputParser()
)

print("✅ summarizer 체인 생성")
print("   독립적 작업: 기사 요약")
print("   다른 작업과 무관하게 실행 가능")

# 작업 2: 감정 분석
sentiment_analyzer = (
    PromptTemplate.from_template(
        "다음 영문 기사의 전체적인 감정을 분석해주세요 (긍정적/중립적/부정적 중 하나로만 답변):\n\n{article}"
    )
    | llm
    | StrOutputParser()
)

print("\n✅ sentiment_analyzer 체인 생성")
print("   독립적 작업: 감정 분석")
print("   요약 결과가 필요 없음")

# 작업 3: 키워드 추출
keyword_extractor = (
    PromptTemplate.from_template(
        "다음 영문 기사에서 핵심 키워드 3개를 추출해주세요 (쉼표로 구분):\n\n{article}"
    )
    | llm
    | StrOutputParser()
)

print("\n✅ keyword_extractor 체인 생성")
print("   독립적 작업: 키워드 추출")
print("   다른 작업 결과 불필요")

# ============================================================================
# 2단계: 병렬 파이프라인 구성
# ============================================================================

print("\n" + "=" * 70)
print("[2단계] 병렬 파이프라인 구성")
print("=" * 70)

parallel_workflow = RunnableParallel(
    summary=summarizer,
    sentiment=sentiment_analyzer,
    keywords=keyword_extractor
)

print("""
✅ RunnableParallel 생성:

              ┌→ [summarizer] → summary
              │
    {article} ┼→ [sentiment_analyzer] → sentiment
              │
              └→ [keyword_extractor] → keywords

    최종 출력: {
        "summary": "...",
        "sentiment": "...",
        "keywords": "..."
    }

특징:
- 세 작업이 동시에 시작
- 각 작업은 모두 같은 입력 ({article}) 받음
- 서로 독립적이라 병렬 실행 가능
- 모든 작업이 완료되면 결과를 딕셔너리로 반환
""")

# ============================================================================
# 3단계: 워크플로우 실행 (병렬)
# ============================================================================

print("=" * 70)
print("[3단계] 병렬 워크플로우 실행")
print("=" * 70)

# 테스트 데이터: 영문 기사
article = """
Artificial Intelligence (AI) is revolutionizing the way we live and work.
From healthcare to finance, AI technologies are being integrated into various
sectors, enhancing efficiency and decision-making processes. Machine learning
algorithms can now analyze vast amounts of data in seconds, identifying patterns
that would take humans years to discover. However, ethical concerns about AI,
such as privacy and job displacement, continue to be debated by experts worldwide.
As we move forward, it is crucial to develop AI responsibly, ensuring it benefits
humanity as a whole.
"""

print("\n📄 입력 기사:")
print("-" * 70)
print(article.strip())
print("-" * 70)

print("\n⏳ 병렬 워크플로우 실행 중...")
print("   (세 작업이 동시에 실행됩니다)")

# 실행 시간 측정
start_time = time.time()

# 병렬 실행
result = parallel_workflow.invoke({"article": article})

parallel_time = time.time() - start_time

print(f"\n✅ 병렬 실행 완료! (소요 시간: {parallel_time:.2f}초)")

print("\n" + "=" * 70)
print("📊 병렬 실행 결과")
print("=" * 70)

print(f"\n📝 요약:")
print(f"   {result['summary']}")

print(f"\n😊 감정:")
print(f"   {result['sentiment']}")

print(f"\n🔑 키워드:")
print(f"   {result['keywords']}")

# ============================================================================
# 4단계: 순차 실행과 비교
# ============================================================================

print("\n" + "=" * 70)
print("[4단계] 순차 실행과 성능 비교")
print("=" * 70)

print("\n⏳ 순차 실행 중...")
print("   (한 작업씩 순서대로 실행됩니다)")

start_time = time.time()

# 순차 실행
summary_seq = summarizer.invoke({"article": article})
sentiment_seq = sentiment_analyzer.invoke({"article": article})
keywords_seq = keyword_extractor.invoke({"article": article})

sequential_time = time.time() - start_time

print(f"\n✅ 순차 실행 완료! (소요 시간: {sequential_time:.2f}초)")

# 성능 비교
print("\n" + "=" * 70)
print("⚡ 성능 비교")
print("=" * 70)

print(f"""
병렬 실행 시간: {parallel_time:.2f}초
순차 실행 시간: {sequential_time:.2f}초
성능 향상: {sequential_time / parallel_time:.2f}배 빠름

결론:
- 병렬 실행이 약 {sequential_time / parallel_time:.1f}배 빠릅니다
- 독립적인 작업일수록 병렬 실행의 이점이 큽니다
- LLM API 호출이 동시에 이루어집니다
""")

# ============================================================================
# 5단계: 결과 후처리
# ============================================================================

print("\n" + "=" * 70)
print("[5단계] 병렬 결과 후처리")
print("=" * 70)

print("""
병렬 실행 결과는 딕셔너리이므로, 후처리 단계를 추가할 수 있습니다.
""")

# 결과 포맷팅 함수
def format_analysis_result(result: dict) -> str:
    """병렬 분석 결과를 보기 좋게 포맷팅"""
    return f"""
╔═══════════════════════════════════════════════════════════════════╗
║                       기사 분석 결과                              ║
╠═══════════════════════════════════════════════════════════════════╣

📝 요약:
{result['summary']}

😊 감정 분석:
{result['sentiment']}

🔑 핵심 키워드:
{result['keywords']}

╚═══════════════════════════════════════════════════════════════════╝
"""

# 후처리 단계 추가
formatter = RunnableLambda(format_analysis_result)

# 전체 워크플로우 (병렬 + 후처리)
complete_workflow = parallel_workflow | formatter

print("✅ 후처리 단계 추가:")
print("""
    parallel_workflow | formatter

              ┌→ [summarizer] → summary
              │
    {article} ┼→ [sentiment_analyzer] → sentiment
              │
              └→ [keyword_extractor] → keywords
                        ↓
                  {결과 딕셔너리}
                        ↓
                   [formatter] (후처리)
                        ↓
                  포맷된 문자열
""")

print("\n⏳ 전체 워크플로우 실행 중...\n")

# 실행
formatted_result = complete_workflow.invoke({"article": article})

print(formatted_result)

# ============================================================================
# 핵심 학습 포인트
# ============================================================================

print("=" * 70)
print("📚 핵심 학습 포인트")
print("=" * 70)

print("""
1️⃣ RunnableParallel
   - 여러 작업을 동시에 실행
   - 각 작업에 키(key) 할당
   - 결과를 딕셔너리로 반환

2️⃣ 독립적인 작업
   - 각 작업이 서로의 결과를 필요로 하지 않음
   - 모두 같은 입력 받음
   - 병렬 실행 가능

3️⃣ 성능 향상
   - 순차 실행 대비 약 3배 빠름
   - LLM API 호출이 동시에 이루어짐
   - 독립적인 작업이 많을수록 효과 큼

4️⃣ 결과 후처리
   - 병렬 결과(딕셔너리)를 다음 단계로 전달
   - 파이프 연산자로 후처리 체인 연결
   - 유연한 워크플로우 구성

5️⃣ 사용 사례
   - 여러 LLM 프롬프트 동시 실행
   - 다양한 분석 작업 병렬 처리
   - 독립적인 데이터 수집
""")

# ============================================================================
# 언제 병렬을 사용할까?
# ============================================================================

print("\n" + "=" * 70)
print("🤔 순차 vs 병렬 - 언제 뭘 사용할까?")
print("=" * 70)

print("""
✅ 병렬 사용 (RunnableParallel):

상황 1: 독립적인 분석 작업
예: 기사 → 요약 + 감정 + 키워드 (서로 독립적)

상황 2: 여러 데이터 소스 조회
예: 날씨 API + 뉴스 API + 주식 API (동시 호출 가능)

상황 3: 다양한 각도의 분석
예: 텍스트 → 문법 검사 + 번역 + 요약 (각각 독립적)

✅ 순차 사용 (RunnableSequence / 파이프 |):

상황 1: 단계별 의존성
예: 기사 → 요약 → 번역 → 키워드 (이전 결과 필요)

상황 2: 점진적 변환
예: 데이터 정제 → 분석 → 보고서 생성 (순서 중요)

상황 3: 조건부 처리
예: 데이터 검증 → 통과 시 처리 → 실패 시 에러 (순서 필수)

💡 판단 기준:
"이 작업이 다른 작업의 결과를 필요로 하나?"
- YES → 순차 (|)
- NO → 병렬 (RunnableParallel)
""")

# ============================================================================
# RunnableParallel 활용 패턴
# ============================================================================

print("\n" + "=" * 70)
print("🔧 RunnableParallel 활용 패턴")
print("=" * 70)

print("""
패턴 1: 여러 프롬프트 동시 실행
parallel = RunnableParallel(
    formal=formal_translator,
    casual=casual_translator,
    technical=technical_translator
)
# 한 번에 세 가지 번역 스타일 얻기

패턴 2: 데이터 수집 + 분석
parallel = RunnableParallel(
    raw_data=data_fetcher,
    analysis=analyzer,
    summary=summarizer
)
# 원본 데이터 보존하면서 분석

패턴 3: 다중 LLM 앙상블
parallel = RunnableParallel(
    gpt4=gpt4_chain,
    claude=claude_chain,
    gemini=gemini_chain
)
# 여러 LLM의 응답을 비교

패턴 4: 입력 보존 + 처리
from langchain_core.runnables import RunnablePassthrough

parallel = RunnableParallel(
    original=RunnablePassthrough(),
    processed=processor
)
# 원본 입력과 처리 결과를 모두 유지
""")

# ============================================================================
# 다음 단계
# ============================================================================

print("\n" + "=" * 70)
print("➡️  다음 단계")
print("=" * 70)

print("""
예제 3에서는:
- 순차 + 병렬 조합
- 복잡한 워크플로우 구성
- 전처리 → 병렬 분석 → 결과 통합

예제 1 (순차):
    입력 → [단계1] → [단계2] → [단계3] → 출력

예제 2 (병렬):
             ┌→ [작업1] → 결과1
    입력 ----┼→ [작업2] → 결과2
             └→ [작업3] → 결과3

예제 3 (조합):
                ┌→ [분석1] → 결과1
    입력 → [전처리] ┼→ [분석2] → 결과2 → [통합] → 출력
                └→ [분석3] → 결과3
""")

print("\n" + "=" * 70)
print("✅ 예제 2 완료!")
print("=" * 70)
