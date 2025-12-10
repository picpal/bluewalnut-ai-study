"""
Phase 5 - 예제 4: 실전 시나리오 (뉴스 기사 분석 시스템)

목표:
- 프로덕션 수준의 워크플로우 구현
- 에러 처리 및 재시도 로직
- 로깅 및 모니터링
- 실전에서 사용 가능한 완전한 파이프라인
"""

import os
import time
import logging
from datetime import datetime
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableParallel, RunnableLambda, RunnablePassthrough

# ============================================================================
# 로깅 설정
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# API 키 설정
os.environ["OPENAI_API_KEY"] = "your-api-key-here"

# LLM 초기화
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0
)

print("=" * 70)
print("Phase 5 - 예제 4: 실전 뉴스 기사 분석 시스템")
print("=" * 70)

# ============================================================================
# 1. 유틸리티 함수
# ============================================================================

class WorkflowMonitor:
    """워크플로우 실행 모니터링"""

    def __init__(self):
        self.stats = {
            "start_time": None,
            "end_time": None,
            "steps_completed": [],
            "errors": [],
            "total_steps": 0
        }

    def start(self):
        self.stats["start_time"] = time.time()
        logger.info("🚀 워크플로우 시작")

    def step_complete(self, step_name: str):
        self.stats["steps_completed"].append({
            "name": step_name,
            "timestamp": time.time()
        })
        logger.info(f"✅ {step_name} 완료")

    def record_error(self, step_name: str, error: Exception):
        self.stats["errors"].append({
            "step": step_name,
            "error": str(error),
            "timestamp": time.time()
        })
        logger.error(f"❌ {step_name} 실패: {error}")

    def end(self):
        self.stats["end_time"] = time.time()
        duration = self.stats["end_time"] - self.stats["start_time"]
        logger.info(f"🏁 워크플로우 완료 (소요 시간: {duration:.2f}초)")

    def get_report(self) -> str:
        duration = self.stats["end_time"] - self.stats["start_time"]
        return f"""
📊 워크플로우 실행 보고서
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⏱️  총 소요 시간: {duration:.2f}초
✅ 완료된 단계: {len(self.stats['steps_completed'])}개
❌ 발생한 에러: {len(self.stats['errors'])}개

단계별 세부 정보:
{self._format_steps()}

에러 세부 정보:
{self._format_errors()}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

    def _format_steps(self) -> str:
        if not self.stats["steps_completed"]:
            return "  없음"
        lines = []
        for i, step in enumerate(self.stats["steps_completed"], 1):
            elapsed = step["timestamp"] - self.stats["start_time"]
            lines.append(f"  {i}. {step['name']} (+{elapsed:.2f}s)")
        return "\n".join(lines)

    def _format_errors(self) -> str:
        if not self.stats["errors"]:
            return "  없음"
        lines = []
        for i, error in enumerate(self.stats["errors"], 1):
            lines.append(f"  {i}. {error['step']}: {error['error']}")
        return "\n".join(lines)

# 전역 모니터
monitor = WorkflowMonitor()

# ============================================================================
# 2. 에러 처리 및 재시도 래퍼
# ============================================================================

def with_retry(func, max_retries=3, step_name="Unknown"):
    """재시도 로직이 포함된 함수 래퍼"""

    def wrapper(*args, **kwargs):
        for attempt in range(max_retries):
            try:
                result = func(*args, **kwargs)
                if attempt > 0:
                    logger.info(f"✅ {step_name} 재시도 성공 (시도 {attempt + 1})")
                return result
            except Exception as e:
                logger.warning(f"⚠️  {step_name} 실패 (시도 {attempt + 1}/{max_retries}): {e}")
                if attempt == max_retries - 1:
                    monitor.record_error(step_name, e)
                    raise
                time.sleep(1 * (attempt + 1))  # 지수 백오프

        return None

    return wrapper

# ============================================================================
# 3. 전처리 단계
# ============================================================================

print("\n[1단계] 전처리 파이프라인 구성\n")

def validate_input(data: Dict[str, Any]) -> Dict[str, Any]:
    """입력 데이터 검증"""
    step_name = "입력 검증"
    logger.info(f"🔍 {step_name} 시작")

    article = data.get("article", "")

    # 검증 규칙
    if not article or not article.strip():
        raise ValueError("기사 내용이 비어있습니다")

    if len(article) < 50:
        raise ValueError(f"기사가 너무 짧습니다 (최소 50자 필요, 현재 {len(article)}자)")

    if len(article) > 10000:
        raise ValueError(f"기사가 너무 깁니다 (최대 10000자, 현재 {len(article)}자)")

    monitor.step_complete(step_name)
    return data

def clean_and_normalize(data: Dict[str, Any]) -> Dict[str, Any]:
    """텍스트 정제 및 정규화"""
    step_name = "텍스트 정제"
    logger.info(f"🧹 {step_name} 시작")

    article = data["article"]

    # 정제 작업
    cleaned = article.strip()
    cleaned = " ".join(cleaned.split())  # 중복 공백 제거

    # 메타데이터 추가
    data_with_meta = {
        "article": cleaned,
        "original_length": len(article),
        "cleaned_length": len(cleaned),
        "word_count": len(cleaned.split()),
        "processing_timestamp": datetime.now().isoformat()
    }

    monitor.step_complete(step_name)
    return data_with_meta

# 전처리 체인
preprocessing = (
    RunnableLambda(lambda x: with_retry(validate_input, step_name="입력 검증")(x))
    | RunnableLambda(lambda x: with_retry(clean_and_normalize, step_name="텍스트 정제")(x))
)

print("✅ 전처리 파이프라인 생성 완료")

# ============================================================================
# 4. 병렬 분석 단계
# ============================================================================

print("\n[2단계] 병렬 분석 파이프라인 구성\n")

# 분석 체인들
summarizer = (
    PromptTemplate.from_template(
        "다음 영문 기사를 3문장 이내로 요약해주세요:\n\n{article}"
    )
    | llm
    | StrOutputParser()
)

sentiment_analyzer = (
    PromptTemplate.from_template(
        "다음 영문 기사의 감정을 분석해주세요 (긍정적/중립적/부정적 중 하나):\n\n{article}"
    )
    | llm
    | StrOutputParser()
)

topic_classifier = (
    PromptTemplate.from_template(
        "다음 영문 기사의 주제를 분류해주세요 (Technology/Health/Politics/Business/Other 중 하나):\n\n{article}"
    )
    | llm
    | StrOutputParser()
)

keyword_extractor = (
    PromptTemplate.from_template(
        "다음 영문 기사에서 핵심 키워드 5개를 추출해주세요 (쉼표로 구분):\n\n{article}"
    )
    | llm
    | StrOutputParser()
)

entity_extractor = (
    PromptTemplate.from_template(
        "다음 영문 기사에서 주요 인물, 조직, 장소를 추출해주세요 (각각 쉼표로 구분하여 나열):\n\n{article}"
    )
    | llm
    | StrOutputParser()
)

# 에러 처리가 포함된 분석 래퍼
def safe_analyze(analyzer, name: str):
    """에러 처리가 포함된 분석 래퍼"""

    def analyze_with_fallback(data: Dict[str, Any]) -> str:
        try:
            logger.info(f"📊 {name} 시작")
            result = analyzer.invoke(data)
            monitor.step_complete(name)
            return result
        except Exception as e:
            logger.error(f"❌ {name} 실패: {e}")
            monitor.record_error(name, e)
            return f"[분석 실패: {str(e)}]"

    return RunnableLambda(analyze_with_fallback)

# 병렬 분석 (에러 처리 포함)
parallel_analysis = RunnableParallel(
    summary=safe_analyze(summarizer, "요약 분석"),
    sentiment=safe_analyze(sentiment_analyzer, "감정 분석"),
    topic=safe_analyze(topic_classifier, "주제 분류"),
    keywords=safe_analyze(keyword_extractor, "키워드 추출"),
    entities=safe_analyze(entity_extractor, "개체명 추출"),
    metadata=RunnablePassthrough()
)

print("✅ 병렬 분석 파이프라인 생성 완료 (에러 처리 포함)")

# ============================================================================
# 5. 결과 통합 및 포맷팅
# ============================================================================

print("\n[3단계] 결과 통합 파이프라인 구성\n")

def integrate_and_validate(analysis_results: Dict[str, Any]) -> Dict[str, Any]:
    """분석 결과 통합 및 검증"""
    step_name = "결과 통합"
    logger.info(f"📦 {step_name} 시작")

    # 실패한 분석 확인
    failed_analyses = []
    for key, value in analysis_results.items():
        if key != "metadata" and "[분석 실패" in str(value):
            failed_analyses.append(key)

    # 통합 보고서
    report = {
        "analysis": {
            "summary": analysis_results["summary"],
            "sentiment": analysis_results["sentiment"],
            "topic": analysis_results["topic"],
            "keywords": analysis_results["keywords"],
            "entities": analysis_results["entities"]
        },
        "metadata": {
            "original_length": analysis_results["metadata"]["original_length"],
            "cleaned_length": analysis_results["metadata"]["cleaned_length"],
            "word_count": analysis_results["metadata"]["word_count"],
            "processing_timestamp": analysis_results["metadata"]["processing_timestamp"],
            "analysis_timestamp": datetime.now().isoformat()
        },
        "quality": {
            "total_analyses": 5,
            "successful_analyses": 5 - len(failed_analyses),
            "failed_analyses": failed_analyses,
            "success_rate": (5 - len(failed_analyses)) / 5 * 100
        }
    }

    monitor.step_complete(step_name)
    return report

def format_final_output(report: Dict[str, Any]) -> str:
    """최종 출력 포맷팅"""
    step_name = "결과 포맷팅"
    logger.info(f"🎨 {step_name} 시작")

    analysis = report["analysis"]
    metadata = report["metadata"]
    quality = report["quality"]

    output = f"""
╔═══════════════════════════════════════════════════════════════════╗
║                     📰 뉴스 기사 분석 보고서                      ║
╠═══════════════════════════════════════════════════════════════════╣

📝 요약:
{analysis['summary']}

😊 감정 분석:
{analysis['sentiment']}

🏷️  주제 분류:
{analysis['topic']}

🔑 핵심 키워드:
{analysis['keywords']}

👥 개체명 (인물/조직/장소):
{analysis['entities']}

╠═══════════════════════════════════════════════════════════════════╣
║                          메타데이터                               ║
╠═══════════════════════════════════════════════════════════════════╣

📊 기사 정보:
- 원본 길이: {metadata['original_length']}자
- 정제 후 길이: {metadata['cleaned_length']}자
- 단어 수: {metadata['word_count']}개

⏱️  처리 시간:
- 전처리: {metadata['processing_timestamp']}
- 분석 완료: {metadata['analysis_timestamp']}

✅ 분석 품질:
- 성공한 분석: {quality['successful_analyses']}/{quality['total_analyses']}개
- 성공률: {quality['success_rate']:.1f}%
{f"- 실패한 분석: {', '.join(quality['failed_analyses'])}" if quality['failed_analyses'] else ""}

╚═══════════════════════════════════════════════════════════════════╝
"""

    monitor.step_complete(step_name)
    return output

# 통합 체인
integration = (
    RunnableLambda(integrate_and_validate)
    | RunnableLambda(format_final_output)
)

print("✅ 결과 통합 파이프라인 생성 완료")

# ============================================================================
# 6. 전체 워크플로우
# ============================================================================

print("\n" + "=" * 70)
print("[4단계] 전체 워크플로우 구성")
print("=" * 70)

# 전체 워크플로우
production_workflow = (
    preprocessing       # 전처리 (검증 + 정제)
    | parallel_analysis # 병렬 분석 (5개 분석 동시 실행)
    | integration       # 결과 통합 (검증 + 포맷팅)
)

print("""
✅ 프로덕션 워크플로우:

    입력
     ↓
    [전처리]
     ├→ 입력 검증 (재시도 3회)
     └→ 텍스트 정제
     ↓
    [병렬 분석] (에러 처리 포함)
     ├→ 요약 분석
     ├→ 감정 분석
     ├→ 주제 분류
     ├→ 키워드 추출
     └→ 개체명 추출
     ↓
    [결과 통합]
     ├→ 결과 통합 및 검증
     └→ 최종 포맷팅
     ↓
    출력

특징:
✅ 재시도 로직 (최대 3회)
✅ 에러 처리 및 Fallback
✅ 로깅 및 모니터링
✅ 품질 검증
""")

# ============================================================================
# 7. 워크플로우 실행
# ============================================================================

print("\n" + "=" * 70)
print("[5단계] 워크플로우 실행")
print("=" * 70)

# 테스트 데이터
article = """
Apple Inc. announced today that its latest iPhone model has broken all previous
sales records in the first quarter of 2024. CEO Tim Cook stated that the
integration of advanced AI features has been a major driver of consumer interest.
The new device includes enhanced camera capabilities, longer battery life, and
improved privacy features. Analysts predict that Apple's market value could
surpass $4 trillion by the end of the year. However, some critics have raised
concerns about the environmental impact of increased electronic waste. Meanwhile,
competitors like Samsung and Google are preparing their own AI-powered smartphone
releases for later this year.
"""

print("\n📄 입력 기사:")
print("-" * 70)
print(article.strip())
print("-" * 70)

# 모니터 시작
monitor.start()

print("\n⏳ 프로덕션 워크플로우 실행 중...\n")

try:
    # 워크플로우 실행
    final_report = production_workflow.invoke({"article": article})

    # 모니터 종료
    monitor.end()

    # 최종 보고서 출력
    print("\n" + "=" * 70)
    print("✅ 최종 보고서")
    print("=" * 70)
    print(final_report)

    # 모니터링 보고서
    print("\n" + "=" * 70)
    print("📈 모니터링 보고서")
    print("=" * 70)
    print(monitor.get_report())

except Exception as e:
    monitor.end()
    logger.error(f"🚨 워크플로우 실행 중 치명적 에러 발생: {e}")
    print(f"\n❌ 워크플로우 실패: {e}")
    print(monitor.get_report())

# ============================================================================
# 8. 에러 시나리오 테스트
# ============================================================================

print("\n" + "=" * 70)
print("[6단계] 에러 처리 테스트")
print("=" * 70)

print("\n테스트 1: 빈 입력")
print("-" * 70)

try:
    production_workflow.invoke({"article": ""})
except ValueError as e:
    print(f"✅ 예상대로 에러 발생: {e}")

print("\n테스트 2: 너무 짧은 입력")
print("-" * 70)

try:
    production_workflow.invoke({"article": "Short"})
except ValueError as e:
    print(f"✅ 예상대로 에러 발생: {e}")

# ============================================================================
# 핵심 학습 포인트
# ============================================================================

print("\n" + "=" * 70)
print("📚 핵심 학습 포인트")
print("=" * 70)

print("""
1️⃣ 에러 처리
   - 재시도 로직 (exponential backoff)
   - Fallback 메커니즘
   - 부분 실패 허용 (일부 분석 실패해도 계속 진행)

2️⃣ 로깅 및 모니터링
   - 단계별 로깅
   - 실행 시간 추적
   - 에러 추적 및 보고

3️⃣ 데이터 검증
   - 입력 검증 (길이, 형식)
   - 결과 검증 (품질 체크)
   - 메타데이터 추가

4️⃣ 프로덕션 레디
   - 안정성 (에러 처리)
   - 관찰 가능성 (로깅)
   - 확장 가능성 (모듈화)

5️⃣ 실전 패턴
   - 전처리 → 병렬 분석 → 통합
   - 각 단계마다 에러 처리
   - 전체 실행 모니터링
""")

# ============================================================================
# Phase 5 요약
# ============================================================================

print("\n" + "=" * 70)
print("📖 Phase 5 전체 요약")
print("=" * 70)

print("""
Phase 5에서 배운 것:

예제 1: 순차 파이프라인
- LCEL 파이프 연산자 (|)
- 단계별 자동 데이터 전달
- 키 매핑 처리

예제 2: 병렬 파이프라인
- RunnableParallel
- 독립적인 작업 동시 실행
- 성능 향상 (약 3배)

예제 3: 순차 + 병렬 조합
- 복잡한 워크플로우 구성
- RunnablePassthrough로 데이터 보존
- 실전 패턴 (전처리 → 병렬 → 통합)

예제 4: 실전 시나리오 (현재)
- 에러 처리 및 재시도
- 로깅 및 모니터링
- 데이터 검증
- 프로덕션 수준 구현

핵심 개념:
✅ LCEL로 명시적인 파이프라인 구성
✅ Runnable 인터페이스의 조합 가능성
✅ 순차 vs 병렬 선택 기준
✅ 실전에서의 에러 처리 및 모니터링

다음 단계 (Phase 6):
- Agent: 자율적 도구 선택 및 실행
- ReAct 패턴
- AgentExecutor
- Phase 5의 수동 워크플로우 → Agent의 자율 워크플로우
""")

print("\n" + "=" * 70)
print("✅ Phase 5 예제 4 완료!")
print("=" * 70)
print("\n🎉 Phase 5 전체 완료! 🎉\n")
