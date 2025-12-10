"""
Phase 5 - 예제 3: 순차 + 병렬 조합 워크플로우

목표:
- 순차 실행과 병렬 실행을 조합한 복잡한 워크플로우
- 전처리 → 병렬 분석 → 결과 통합 패턴
- 실전에서 자주 사용되는 파이프라인 구조
"""

from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableParallel, RunnableLambda, RunnablePassthrough

# 환경 변수 로드
load_dotenv()

# LLM 초기화
llm = ChatAnthropic(
    model="claude-3-haiku-20240307",
    temperature=0
)

print("=" * 70)
print("Phase 5 - 예제 3: 순차 + 병렬 조합 워크플로우")
print("=" * 70)

# ============================================================================
# 1단계: 전처리 체인 (순차)
# ============================================================================

print("\n[1단계] 전처리 체인 정의\n")

# 전처리 함수들
def clean_text(data: dict) -> dict:
    """텍스트 정제: 공백 제거, 소문자 변환"""
    article = data["article"]
    cleaned = article.strip().lower()
    print(f"   🧹 텍스트 정제 완료 (길이: {len(cleaned)} 문자)")
    return {"article": cleaned}

def extract_sentences(data: dict) -> dict:
    """문장 분리"""
    article = data["article"]
    sentences = [s.strip() for s in article.split('.') if s.strip()]
    sentence_count = len(sentences)
    print(f"   📄 문장 분리 완료 ({sentence_count}개 문장)")
    return {"article": data["article"], "sentence_count": sentence_count}

# 전처리 체인
preprocessing = (
    RunnableLambda(clean_text)
    | RunnableLambda(extract_sentences)
)

print("✅ 전처리 체인 생성:")
print("""
    [clean_text] → [extract_sentences]

    1. 공백 제거 및 소문자 변환
    2. 문장 분리 및 개수 카운트
""")

# ============================================================================
# 2단계: 병렬 분석 체인
# ============================================================================

print("\n" + "=" * 70)
print("[2단계] 병렬 분석 체인 정의")
print("=" * 70)

# 분석 1: 요약
summarizer = (
    PromptTemplate.from_template(
        "다음 영문 기사를 3문장 이내로 요약해주세요:\n\n{article}"
    )
    | llm
    | StrOutputParser()
)

# 분석 2: 감정 분석
sentiment_analyzer = (
    PromptTemplate.from_template(
        "다음 영문 기사의 전체적인 감정을 분석해주세요 (긍정적/중립적/부정적 중 하나):\n\n{article}"
    )
    | llm
    | StrOutputParser()
)

# 분석 3: 주제 분류
topic_classifier = (
    PromptTemplate.from_template(
        "다음 영문 기사의 주제를 하나의 단어로 분류해주세요 (예: Technology, Health, Politics):\n\n{article}"
    )
    | llm
    | StrOutputParser()
)

# 분석 4: 키워드 추출
keyword_extractor = (
    PromptTemplate.from_template(
        "다음 영문 기사에서 핵심 키워드 3개를 추출해주세요 (쉼표로 구분):\n\n{article}"
    )
    | llm
    | StrOutputParser()
)

# 병렬 분석
parallel_analysis = RunnableParallel(
    summary=summarizer,
    sentiment=sentiment_analyzer,
    topic=topic_classifier,
    keywords=keyword_extractor,
    metadata=RunnablePassthrough()  # 원본 데이터 보존
)

print("""
✅ 병렬 분석 체인 생성:

                 ┌→ [summarizer] → summary
                 │
                 ┼→ [sentiment_analyzer] → sentiment
    전처리 결과 → │
                 ┼→ [topic_classifier] → topic
                 │
                 ┼→ [keyword_extractor] → keywords
                 │
                 └→ [RunnablePassthrough] → metadata

    출력: {
        "summary": "...",
        "sentiment": "...",
        "topic": "...",
        "keywords": "...",
        "metadata": {원본 데이터}
    }
""")

# ============================================================================
# 3단계: 결과 통합 체인 (순차)
# ============================================================================

print("\n" + "=" * 70)
print("[3단계] 결과 통합 체인 정의")
print("=" * 70)

def integrate_results(analysis_results: dict) -> dict:
    """병렬 분석 결과를 하나의 보고서로 통합"""
    print("\n   📊 분석 결과 통합 중...")

    report = {
        "summary": analysis_results["summary"],
        "sentiment": analysis_results["sentiment"],
        "topic": analysis_results["topic"],
        "keywords": analysis_results["keywords"],
        "sentence_count": analysis_results["metadata"].get("sentence_count", 0),
        "article_length": len(analysis_results["metadata"]["article"])
    }

    print("   ✅ 통합 완료!")
    return report

def format_final_report(report: dict) -> str:
    """최종 보고서 포맷팅"""
    return f"""
╔═══════════════════════════════════════════════════════════════════╗
║                     📊 기사 분석 최종 보고서                      ║
╠═══════════════════════════════════════════════════════════════════╣

📝 요약:
{report['summary']}

😊 감정 분석:
{report['sentiment']}

🏷️  주제 분류:
{report['topic']}

🔑 핵심 키워드:
{report['keywords']}

📈 메타데이터:
- 총 문장 수: {report['sentence_count']}개
- 기사 길이: {report['article_length']}자

╚═══════════════════════════════════════════════════════════════════╝
"""

# 통합 체인
integration = (
    RunnableLambda(integrate_results)
    | RunnableLambda(format_final_report)
)

print("""
✅ 결과 통합 체인 생성:

    [integrate_results] → [format_final_report]

    1. 병렬 분석 결과를 단일 딕셔너리로 통합
    2. 최종 보고서 포맷팅
""")

# ============================================================================
# 4단계: 전체 워크플로우 구성
# ============================================================================

print("\n" + "=" * 70)
print("[4단계] 전체 워크플로우 구성")
print("=" * 70)

# 전체 워크플로우: 전처리 → 병렬 분석 → 결과 통합
complete_workflow = (
    preprocessing       # 순차 1: 전처리
    | parallel_analysis # 병렬: 다중 분석
    | integration       # 순차 2: 결과 통합
)

print("""
✅ 전체 워크플로우:

    입력 ({article})
       ↓
    [전처리] (순차)
       ├→ clean_text
       └→ extract_sentences
       ↓
    {article, sentence_count}
       ↓
              ┌→ [summarizer]
              ┼→ [sentiment_analyzer]
    [병렬 분석] ┼→ [topic_classifier]
              ┼→ [keyword_extractor]
              └→ [metadata 보존]
       ↓
    {summary, sentiment, topic, keywords, metadata}
       ↓
    [결과 통합] (순차)
       ├→ integrate_results
       └→ format_final_report
       ↓
    최종 보고서 (포맷된 문자열)

순차 → 병렬 → 순차 패턴!
""")

# ============================================================================
# 5단계: 워크플로우 실행
# ============================================================================

print("\n" + "=" * 70)
print("[5단계] 전체 워크플로우 실행")
print("=" * 70)

# 테스트 데이터
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

print("\n⏳ 전체 워크플로우 실행 중...\n")
print("🔄 1단계: 전처리 실행...")

# 전체 워크플로우 실행
final_report = complete_workflow.invoke({"article": article})

print("\n" + "=" * 70)
print("✅ 최종 보고서")
print("=" * 70)

print(final_report)

# ============================================================================
# 6단계: 각 단계별 실행 (디버깅)
# ============================================================================

print("\n" + "=" * 70)
print("[6단계] 각 단계별 실행 (디버깅)")
print("=" * 70)

print("\n1️⃣ 전처리 단계:")
print("-" * 70)
preprocessed = preprocessing.invoke({"article": article})
print(f"결과: {preprocessed}")

print("\n2️⃣ 병렬 분석 단계:")
print("-" * 70)
analysis_results = parallel_analysis.invoke(preprocessed)
print("결과:")
for key, value in analysis_results.items():
    if key != "metadata":
        print(f"  {key}: {value}")

print("\n3️⃣ 결과 통합 단계:")
print("-" * 70)
integrated = integration.invoke(analysis_results)
print("최종 보고서 생성 완료")

# ============================================================================
# 핵심 학습 포인트
# ============================================================================

print("\n" + "=" * 70)
print("📚 핵심 학습 포인트")
print("=" * 70)

print("""
1️⃣ 순차 + 병렬 조합
   - 전처리: 순차 실행 (단계별 의존성)
   - 분석: 병렬 실행 (독립적 작업)
   - 통합: 순차 실행 (결과 결합)

2️⃣ RunnablePassthrough
   - 병렬 실행 시 원본 데이터 보존
   - metadata로 원본 정보 유지
   - 나중에 참조 가능

3️⃣ 딕셔너리 흐름
   - 각 단계가 딕셔너리를 주고받음
   - 키 이름으로 데이터 추적
   - 유연한 데이터 관리

4️⃣ 실전 패턴
   - 전처리 → 병렬 분석 → 통합
   - 가장 많이 사용되는 구조
   - 성능과 가독성 모두 확보

5️⃣ 디버깅 용이
   - 각 단계를 독립적으로 테스트 가능
   - 중간 결과 확인 가능
   - 문제 발생 시 원인 파악 쉬움
""")

# ============================================================================
# 실전 활용 패턴
# ============================================================================

print("\n" + "=" * 70)
print("🔧 실전 활용 패턴")
print("=" * 70)

print("""
패턴 1: 데이터 수집 → 분석 → 보고서
workflow = (
    data_collector          # 순차: 데이터 수집
    | RunnableParallel(     # 병렬: 다양한 분석
        stats=statistics,
        viz=visualization,
        insights=insight_generator
    )
    | report_generator      # 순차: 보고서 생성
)

패턴 2: 검증 → 처리 → 저장
workflow = (
    validator               # 순차: 데이터 검증
    | RunnableParallel(     # 병렬: 여러 처리
        process_a=processor_a,
        process_b=processor_b
    )
    | saver                 # 순차: 결과 저장
)

패턴 3: 전처리 → 다중 모델 → 앙상블
workflow = (
    preprocessor            # 순차: 전처리
    | RunnableParallel(     # 병렬: 여러 모델
        gpt4=gpt4_chain,
        claude=claude_chain,
        gemini=gemini_chain
    )
    | ensemble              # 순차: 결과 앙상블
)

패턴 4: 원본 보존 + 변환
workflow = (
    RunnableParallel(
        original=RunnablePassthrough(),
        transformed=transformer
    )
    | comparator            # 원본과 변환 결과 비교
)
""")

# ============================================================================
# 성능 최적화 팁
# ============================================================================

print("\n" + "=" * 70)
print("⚡ 성능 최적화 팁")
print("=" * 70)

print("""
1️⃣ 병렬 실행 최대화
   - 독립적인 작업은 최대한 병렬로
   - LLM 호출이 많을수록 효과 큼
   - 예: 4개 작업 병렬 → 약 4배 빠름

2️⃣ 불필요한 순차 제거
   - 의존성 없는 작업은 병렬로 전환
   - 예: "요약 후 키워드" → "요약 | 키워드" (병렬 가능)

3️⃣ 데이터 전달 최소화
   - 필요한 데이터만 다음 단계로 전달
   - 큰 데이터는 RunnablePassthrough 활용

4️⃣ 캐싱 활용
   - 같은 입력에 대한 결과 캐싱
   - LangChain 캐싱 기능 활용
   - 반복 호출 비용 절감

5️⃣ 배치 처리
   - 여러 입력을 한 번에 처리
   - workflow.batch([input1, input2, ...])
   - 대량 데이터 처리 시 유용
""")

# ============================================================================
# 다음 단계
# ============================================================================

print("\n" + "=" * 70)
print("➡️  다음 단계")
print("=" * 70)

print("""
예제 4에서는:
- 실전 시나리오: 뉴스 기사 분석 시스템
- 에러 처리 및 재시도 로직
- 로깅 및 모니터링
- 프로덕션 수준의 워크플로우

예제 1: 순차 (A → B → C)
예제 2: 병렬 (A → [B1, B2, B3])
예제 3: 조합 (A → [B1, B2] → C)
예제 4: 실전 (모든 패턴 + 에러 처리 + 로깅)
""")

print("\n" + "=" * 70)
print("✅ 예제 3 완료!")
print("=" * 70)
