"""
Phase 5 - 예제 1: 순차 파이프라인 (Sequential Pipeline)

목표:
- LCEL 파이프 연산자로 여러 단계 연결
- 각 단계의 출력이 자동으로 다음 단계의 입력
- 기사 요약 → 번역 → 키워드 추출 파이프라인 구현
"""

import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda

# API 키 설정
os.environ["OPENAI_API_KEY"] = "your-api-key-here"

# LLM 초기화
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0
)

print("=" * 70)
print("Phase 5 - 예제 1: 순차 파이프라인")
print("=" * 70)

# ============================================================================
# 1단계: 각 단계 정의
# ============================================================================

print("\n[1단계] 각 처리 단계 정의\n")

# 1단계: 요약 체인
summarizer = (
    PromptTemplate.from_template(
        "다음 영문 기사를 3문장 이내로 요약해주세요:\n\n{article}"
    )
    | llm
    | StrOutputParser()
)

print("✅ summarizer 체인 생성")
print("   입력: {article}")
print("   처리: 영문 기사를 3문장으로 요약")
print("   출력: str (요약 결과)")

# 2단계: 번역 체인
translator = (
    PromptTemplate.from_template(
        "다음 영문 텍스트를 한글로 번역해주세요:\n\n{text}"
    )
    | llm
    | StrOutputParser()
)

print("\n✅ translator 체인 생성")
print("   입력: {text}")
print("   처리: 영문을 한글로 번역")
print("   출력: str (번역 결과)")

# 3단계: 키워드 추출 체인
keyword_extractor = (
    PromptTemplate.from_template(
        "다음 텍스트에서 핵심 키워드 3개를 추출해주세요 (쉼표로 구분):\n\n{text}"
    )
    | llm
    | StrOutputParser()
)

print("\n✅ keyword_extractor 체인 생성")
print("   입력: {text}")
print("   처리: 핵심 키워드 3개 추출")
print("   출력: str (키워드 목록)")

# ============================================================================
# 2단계: 키 매핑 함수 정의
# ============================================================================

print("\n" + "=" * 70)
print("[2단계] 키 매핑 함수 정의")
print("=" * 70)

print("""
문제:
- summarizer는 {article}을 입력으로 받음
- translator와 keyword_extractor는 {text}를 입력으로 받음
- 하지만 summarizer의 출력은 단순 문자열 (str)

해결:
- RunnableLambda로 str → {"text": str} 변환
""")

def map_to_text(output: str) -> dict:
    """문자열 출력을 {text: ...} 딕셔너리로 변환"""
    return {"text": output}

print("✅ map_to_text 함수 정의")
print("   입력: str")
print("   출력: {'text': str}")

# ============================================================================
# 3단계: 전체 워크플로우 구성
# ============================================================================

print("\n" + "=" * 70)
print("[3단계] 전체 워크플로우 구성")
print("=" * 70)

workflow = (
    summarizer                      # 입력: {article} → 출력: str
    | RunnableLambda(map_to_text)   # 입력: str → 출력: {text: str}
    | translator                    # 입력: {text} → 출력: str
    | RunnableLambda(map_to_text)   # 입력: str → 출력: {text: str}
    | keyword_extractor             # 입력: {text} → 출력: str
)

print("""
✅ 전체 워크플로우:

    {article}
       ↓
  [summarizer] (요약)
       ↓
     str
       ↓
  [map_to_text] (키 매핑)
       ↓
   {text: str}
       ↓
  [translator] (번역)
       ↓
     str
       ↓
  [map_to_text] (키 매핑)
       ↓
   {text: str}
       ↓
  [keyword_extractor] (키워드)
       ↓
     str (최종 결과)
""")

# ============================================================================
# 4단계: 워크플로우 실행
# ============================================================================

print("=" * 70)
print("[4단계] 워크플로우 실행")
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

print("\n📄 입력 기사 (원문):")
print("-" * 70)
print(article.strip())
print("-" * 70)

print("\n⏳ 워크플로우 실행 중...")
print()

# 워크플로우 실행
result = workflow.invoke({"article": article})

print("\n" + "=" * 70)
print("✅ 최종 결과")
print("=" * 70)
print(f"\n🔑 핵심 키워드: {result}")

# ============================================================================
# 5단계: 중간 단계별 실행 (디버깅용)
# ============================================================================

print("\n" + "=" * 70)
print("[5단계] 중간 단계별 실행 (디버깅)")
print("=" * 70)

print("\n1️⃣ 1단계: 요약")
print("-" * 70)
summary = summarizer.invoke({"article": article})
print(f"요약 결과:\n{summary}")

print("\n2️⃣ 2단계: 번역")
print("-" * 70)
translation = translator.invoke({"text": summary})
print(f"번역 결과:\n{translation}")

print("\n3️⃣ 3단계: 키워드 추출")
print("-" * 70)
keywords = keyword_extractor.invoke({"text": translation})
print(f"키워드:\n{keywords}")

# ============================================================================
# 핵심 학습 포인트
# ============================================================================

print("\n" + "=" * 70)
print("📚 핵심 학습 포인트")
print("=" * 70)

print("""
1️⃣ LCEL 파이프 연산자 (|)
   - 왼쪽 출력이 오른쪽 입력으로 자동 전달
   - 예: step1 | step2 | step3

2️⃣ 각 단계는 Runnable
   - PromptTemplate | LLM | OutputParser
   - 모두 .invoke() 메서드 제공

3️⃣ 키 매핑 처리
   - RunnableLambda로 출력 형식 변환
   - str → {"text": str} 변환으로 다음 단계 연결

4️⃣ 순차 실행
   - 각 단계가 이전 단계 완료 후 실행
   - 단계별 의존성이 명확

5️⃣ 자동 데이터 흐름
   - 수동으로 결과 전달 불필요
   - 체인이 자동으로 처리
""")

# ============================================================================
# Phase 4와 비교
# ============================================================================

print("\n" + "=" * 70)
print("🆚 Phase 4 vs Phase 5")
print("=" * 70)

print("""
Phase 4 방식 (수동 루프):
```python
messages = [HumanMessage(content=article)]

# 1단계: 요약
response1 = llm.invoke(messages)
summary = response1.content

# 2단계: 번역
messages.append(AIMessage(content=summary))
messages.append(HumanMessage(content="번역해줘"))
response2 = llm.invoke(messages)
translation = response2.content

# 3단계: 키워드
messages.append(AIMessage(content=translation))
messages.append(HumanMessage(content="키워드 추출해줘"))
response3 = llm.invoke(messages)
keywords = response3.content
```

문제점:
❌ 각 단계를 수동으로 호출
❌ 메시지 히스토리 수동 관리
❌ 코드가 길고 반복적
❌ 단계 추가 시 코드 수정 많음

Phase 5 방식 (LCEL 파이프라인):
```python
workflow = summarizer | map_to_text | translator | map_to_text | keyword_extractor
result = workflow.invoke({"article": article})
```

장점:
✅ 한 줄로 전체 파이프라인 정의
✅ 자동 데이터 전달
✅ 읽기 쉽고 유지보수 용이
✅ 단계 추가/제거 간단 (파이프만 수정)
""")

# ============================================================================
# 워크플로우 확장
# ============================================================================

print("\n" + "=" * 70)
print("🔧 워크플로우 확장 예시")
print("=" * 70)

print("""
기존 워크플로우에 단계 추가가 쉽습니다:

1️⃣ 감정 분석 단계 추가:
sentiment_analyzer = PromptTemplate(...) | llm | StrOutputParser()

extended_workflow = (
    summarizer
    | map_to_text
    | translator
    | map_to_text
    | sentiment_analyzer  # 새 단계 추가
    | map_to_text
    | keyword_extractor
)

2️⃣ 전처리 단계 추가:
cleaner = RunnableLambda(lambda x: x.strip())

workflow_with_preprocessing = (
    cleaner  # 맨 앞에 추가
    | summarizer
    | map_to_text
    | translator
    | map_to_text
    | keyword_extractor
)

3️⃣ 후처리 단계 추가:
formatter = RunnableLambda(lambda x: f"핵심 키워드: {x}")

workflow_with_formatting = (
    summarizer
    | map_to_text
    | translator
    | map_to_text
    | keyword_extractor
    | formatter  # 맨 뒤에 추가
)

파이프 연산자 덕분에 단계 추가가 매우 간단합니다!
""")

# ============================================================================
# 다음 단계
# ============================================================================

print("\n" + "=" * 70)
print("➡️  다음 단계")
print("=" * 70)

print("""
예제 2에서는:
- 병렬 파이프라인 (RunnableParallel)
- 동시에 여러 작업 실행
- 요약 + 감정 분석 + 키워드를 동시에 처리

예제 1 (순차):
    입력 → [단계1] → [단계2] → [단계3] → 출력

예제 2 (병렬):
             ┌→ [작업1] → 결과1
    입력 ----┼→ [작업2] → 결과2
             └→ [작업3] → 결과3
""")

print("\n" + "=" * 70)
print("✅ 예제 1 완료!")
print("=" * 70)
