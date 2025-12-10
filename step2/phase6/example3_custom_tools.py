"""
Phase 6 - 예제 3: 커스텀 도구와 Agent

목표:
- 복잡한 커스텀 도구 정의
- 도구 간의 의존성 처리
- 동적 도구 선택 능력 검증
- 실전 시나리오 구현 준비
"""

import os
import json
import re
from datetime import datetime
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain.agents import create_react_agent, AgentExecutor
from langchain_core.tools import tool
from langchain_core.prompts import PromptTemplate

# 환경 변수 로드
load_dotenv()

print("=" * 70)
print("Phase 6 - 예제 3: 커스텀 도구와 Agent")
print("=" * 70)
print()

# ============================================================================
# 1. 복잡한 커스텀 도구 정의
# ============================================================================


@tool
def search_news(query: str) -> str:
    """
    최신 뉴스를 검색합니다.

    Args:
        query: 검색할 뉴스 키워드

    Returns:
        검색된 뉴스 정보 (JSON 형식)
    """
    # 모의 뉴스 데이터
    news_data = {
        "AI 기술": {
            "title": "AI 기술 혁신, GPT-5보다 10배 뛰어넘",
            "content": "OpenAI가 최신 AI 모델 GPT-5를 공개하며, 이전 모델보다 10배 더 뛰어난 성능을 보여줬다. 연구원들은 이 모델의 안전성에 대해 우려를 표명하고 있다.",
            "date": "2024-12-10",
            "source": "테크뉴스",
        },
        "애플 주식": {
            "title": "애플의 최신 분기 실적 발표",
            "content": "애플이 최신 분기 실적을 발표했다. 매출 119조 달러를 기록하며, 시장의 예상을 뛰어넘었다. 주요 애플들의 주가가 상승했으며, 투자들은 긍정적인 반응을 보이고 있다.",
            "date": "2024-12-09",
            "source": "경제신문",
        },
        "환경 정책": {
            "title": "정부, 탄소중립 목표 2030년 달성",
            "content": "정부가 2050년까지 탄소중립을 목표로 삼고, 관련 산업에 대한 지원 정책을 발표했다. 기업들은 탄소 배출권 거래에 참여해야 한다.",
            "date": "2024-12-08",
            "source": "정부부 보도자료",
        },
    }

    # 키워드로 뉴스 검색
    results = []
    for category, news in news_data.items():
        if query.lower() in category.lower() or query.lower() in news["title"].lower():
            results.append(
                {
                    "category": category,
                    "title": news["title"],
                    "content": news["content"][:100] + "...",  # 요약
                    "date": news["date"],
                    "source": news["source"],
                }
            )

    print(f"    [도구 실행] search_news('{query}') → {len(results)}개 결과")
    return json.dumps(results, ensure_ascii=False)


@tool
def analyze_sentiment(text: str) -> str:
    """
    텍스트의 감정을 분석합니다.

    Args:
        text: 분석할 텍스트

    Returns:
        감정 분석 결과 (긍정적/중립적/부정적)
    """
    # 간단한 감정 분석 로직
    positive_words = ["좋다", "성공", "기대", "혁신", "발전", "상승", "증가", "긍정적"]
    negative_words = ["실패", "하락", "우려", "위기", "감소", "부정적", "문제", "위험"]

    text_lower = text.lower()
    positive_count = sum(1 for word in positive_words if word in text_lower)
    negative_count = sum(1 for word in negative_words if word in text_lower)

    if positive_count > negative_count:
        sentiment = "긍정적"
    elif negative_count > positive_count:
        sentiment = "부정적"
    else:
        sentiment = "중립적"

    print(f"    [도구 실행] analyze_sentiment('{text[:30]}...') → {sentiment}")
    return sentiment


@tool
def extract_key_info(news_json: str) -> str:
    """
    뉴스 JSON에서 핵심 정보를 추출합니다.

    Args:
        news_json: 뉴스 정보가 담긴 JSON 문자열

    Returns:
        추출된 핵심 정보
    """
    try:
        news_list = json.loads(news_json)
        if not news_list:
            return "뉴스 정보가 없습니다."

        # 첫 번째 뉴스의 핵심 정보 추출
        first_news = news_list[0]
        title = first_news.get("title", "제목 없음")
        date = first_news.get("date", "날짜 없음")
        source = first_news.get("source", "출처 없음")

        key_info = f"제목: {title}, 날짜: {date}, 출처: {source}"
        print(f"    [도구 실행] extract_key_info('{news_json[:50]}...') → {key_info}")
        return key_info

    except json.JSONDecodeError:
        return "JSON 파싱 에러가 발생했습니다."


@tool
def generate_summary(news_info: str, sentiment: str) -> str:
    """
    뉴스 정보와 감정을 바탕으로 요약을 생성합니다.

    Args:
        news_info: 뉴스 핵심 정보
        sentiment: 감정 분석 결과

    Returns:
        생성된 요약
    """
    # 감정에 따른 다른 요약 생성
    if sentiment == "긍정적":
        summary_prefix = "긍정적인 뉴스입니다."
    elif sentiment == "부정적":
        summary_prefix = "부정적인 뉴스입니다."
    else:
        summary_prefix = "중립적인 뉴스입니다."

    summary = f"{summary_prefix} {news_info} 이 뉴스는 현재 이슈가 되고 있습니다."
    print(
        f"    [도구 실행] generate_summary('{news_info[:30]}...', '{sentiment}') → 요약 생성"
    )
    return summary


@tool
def create_report(title: str, content: str, analysis: str) -> str:
    """
    최종 보고서를 생성합니다.

    Args:
        title: 보고서 제목
        content: 보고서 내용
        analysis: 분석 결과

    Returns:
        생성된 보고서
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    report = f"""
===============================================
{title}
===============================================
작성 시각: {timestamp}

내용:
{content}

분석:
{analysis}

===============================================
"""

    print(f"    [도구 실행] create_report('{title}', ...) → 보고서 생성 완료")
    return report


print("📌 1. 복잡한 커스텀 도구 정의 완료")
print("  - search_news: 뉴스 검색")
print("  - analyze_sentiment: 감정 분석")
print("  - extract_key_info: 핵심 정보 추출")
print("  - generate_summary: 요약 생성")
print("  - create_report: 보고서 생성")
print()

# ============================================================================
# 2. LLM 설정
# ============================================================================

llm = ChatAnthropic(
    model_name="claude-3-haiku-20240307", temperature=0, timeout=60, stop=None
)

print("📌 2. LLM 설정 완료")
print(f"  - 모델: claude-3-haiku-20240307")
print(f"  - Temperature: 0")
print()

# ============================================================================
# 3. 고급 ReAct 프롬프트
# ============================================================================

advanced_react_prompt = PromptTemplate.from_template("""
You are an expert research assistant that can analyze complex information using multiple tools.
Think strategically and use tools efficiently to gather comprehensive information.

Available tools:
{tools}

Tool names: {tool_names}

Use the following format:
Question: {input}
Thought: Analyze the question and plan your approach step by step
Action: [tool name]
Action Input: [specific input]
Observation: [tool result]
Thought: Based on the observation, what's the next logical step?
Action: [next tool if needed]
Action Input: [input for next tool]
Observation: [result of next tool]
Thought: Continue this process until you have all necessary information
Final Answer: Provide a comprehensive analysis based on all gathered information

Strategic guidelines:
1. Plan your approach before taking actions
2. Use tools efficiently and avoid unnecessary calls
3. Combine information from multiple tools when needed
4. Provide detailed, well-structured answers
5. Consider the relationships between different pieces of information

Begin!
Thought:{agent_scratchpad}""")

print("📌 3. 고급 ReAct 프롬프트 작성 완료")
print("  - 전략적 접근 방법 가이드")
print("  - 효율적인 도구 사용 지시")
print("  - 정보 종합 및 분석 요구")
print()

# ============================================================================
# 4. Agent 생성 및 설정
# ============================================================================

tools = [
    search_news,
    analyze_sentiment,
    extract_key_info,
    generate_summary,
    create_report,
]

# 고급 Agent 생성
advanced_agent = create_react_agent(llm, tools, advanced_react_prompt)

# 고급 AgentExecutor 설정
advanced_executor = AgentExecutor(
    agent=advanced_agent,
    tools=tools,
    verbose=True,
    max_iterations=15,
    early_stopping_method="generate",
    handle_parsing_errors=True,
    return_intermediate_steps=True,
)

print("📌 4. 고급 Agent 설정 완료")
print("  - 최대 15회 반복")
print("  - 전략적 프롬프트 적용")
print("  - 상세 로깅 활성화")
print()

# ============================================================================
# 5. 복잡한 시나리오 테스트
# ============================================================================

print("=" * 70)
print("📌 5. 복잡한 시나리오 테스트")
print("=" * 70)
print()

# 테스트 케이스 1: 뉴스 검색 및 분석
test_query_1 = "AI 기술 관련 최신 뉴스를 검색하고, 감정을 분석하여 요약을 만들어줘"

print(f"🔍 테스트 1: {test_query_1}")
print("-" * 70)

try:
    result_1 = advanced_executor.invoke({"input": test_query_1})
    print(f"\n✅ 최종 결과:")
    print(result_1["output"])

    # 중간 단계 분석
    if "intermediate_steps" in result_1:
        print("\n📊 도구 호출 순서:")
        for i, (action, observation) in enumerate(result_1["intermediate_steps"], 1):
            print(f"  {i}. {action.tool} → {observation}")

except Exception as e:
    print(f"❌ 에러: {e}")

print("\n" + "=" * 70)

# 테스트 케이스 2: 복합적인 정보 분석
test_query_2 = "애플 주식 시장 동향을 분석하고, 투자들에게 영향을 줄 수 있는 정책 변화를 조사하여 보고서를 작성해줘"

print(f"🔍 테스트 2: {test_query_2}")
print("-" * 70)

try:
    result_2 = advanced_executor.invoke({"input": test_query_2})
    print(f"\n✅ 최종 결과:")
    print(result_2["output"])

    # 중간 단계 분석
    if "intermediate_steps" in result_2:
        print("\n📊 도구 호출 순서:")
        for i, (action, observation) in enumerate(result_2["intermediate_steps"], 1):
            print(f"  {i}. {action.tool} → {observation}")

except Exception as e:
    print(f"❌ 에러: {e}")

print("\n" + "=" * 70)

# 테스트 케이스 3: 동적 도구 선택 능력 테스트
test_query_3 = "최신 경제 뉴스를 검색하고, 검색된 뉴스의 감정을 분석한 후, 그 결과를 바탕으로 투자 보고서를 작성해줘"

print(f"🔍 테스트 3: {test_query_3}")
print("-" * 70)

try:
    result_3 = advanced_executor.invoke({"input": test_query_3})
    print(f"\n✅ 최종 결과:")
    print(result_3["output"])

    # 중간 단계 분석
    if "intermediate_steps" in result_3:
        print("\n📊 도구 호출 순서:")
        for i, (action, observation) in enumerate(result_3["intermediate_steps"], 1):
            print(f"  {i}. {action.tool} → {observation}")

except Exception as e:
    print(f"❌ 에러: {e}")

# ============================================================================
# 6. 도구 의존성 테스트
# ============================================================================

print("\n" + "=" * 70)
print("📌 6. 도구 의존성 테스트")
print("=" * 70)
print()

# 의존성 테스트: 이전 도구 결과를 다음 도구의 입력으로 사용
dependency_test_query = "AI 기술 뉴스를 검색하고, 검색된 뉴스의 감정을 분석한 후, 그 결과를 바탕으로 투자 보고서를 작성해줘"

print(f"🔍 의존성 테스트: {dependency_test_query}")
print("-" * 70)

try:
    result_4 = advanced_executor.invoke({"input": dependency_test_query})
    print(f"\n✅ 최종 결과:")
    print(result_4["output"])

    # 중간 단계 분석
    if "intermediate_steps" in result_4:
        print("\n📊 도구 호출 순서:")
        for i, (action, observation) in enumerate(result_4["intermediate_steps"], 1):
            print(f"  {i}. {action.tool} → {observation}")

except Exception as e:
    print(f"❌ 에러: {e}")

# ============================================================================
# 7. 커스텀 도구 설계 원칙
# ============================================================================

print("\n" + "=" * 70)
print("📌 7. 커스텀 도구 설계 원칙")
print("=" * 70)

print("""
1. 단일 책임 원칙 (Single Responsibility Principle)
   - 각 도구는 하나의 명확한 기능만 수행
   - 도구 간의 의존성 최소화
   - 입력과 출력의 명확한 정의

2. 명확한 인터페이스 설계
   - 일관된 파라미터 이름
   - 상세한 docstring 제공
   - 표준화된 반환 형식
   - 에러 처리 포함

3. 데이터 형식 표준화
   - JSON 형식 사용 (구조화된 데이터)
   - 일관된 키 이름 사용
   - 타입 힌트 명확히 지정
   - 파싱 용이성 고려

4. 견고성 확보
   - 입력값 검증
   - 예외 처리 및 안전한 기본값
   - 민감한 정보 보호
   - 안전한 데이터 처리

5. 확장성 고려
   - 새로운 도구 쉽게 추가 가능
   - 기존 도구와의 호환성 유지
   - 모듈화된 설계
   - 설정 가능한 파라미터

6. 테스트 가능성
   - 단위 테스트 용이성
   - 모의 데이터 사용
   - 경계 조건 테스트
   - 에러 시나리오 검증
""")

# ============================================================================
# 8. Agent의 동적 도구 선택 능력 분석
# ============================================================================

print("\n" + "=" * 70)
print("📌 8. Agent의 동적 도구 선택 능력 분석")
print("=" * 70)

print("""
Agent의 동적 도구 선택 능력:

1. 문제 이해 (Problem Understanding)
   - 복잡한 질문의 구조 파악
   - 필요한 정보 유형 식별
   - 해결에 필요한 도구 목록화

2. 도구 선택 전략 (Tool Selection Strategy)
   - 사용 가능한 도구 목록 분석
   - 효율적인 도구 조합 계획
   - 선행 조건과 후행 조건 고려
   - 비용/시간 최적화

3. 실행 순서 최적화 (Execution Order Optimization)
   - 논리적인 실행 순서 결정
   - 병렬 실행 가능성 검토
   - 의존성 관계 고려
   - 동적 순서 조정

4. 결과 통합 (Result Integration)
   - 여러 도구 결과의 종합
   - 중복 정보 제거
   - 일관된 형식으로 변환
   - 품질 검증

5. 적응성 (Adaptability)
   - 새로운 도구로의 쉬운 확장
   - 기존 도구의 재사용
   - 다양한 입력 유형 처리
   - 예외 상황에서의 안정적인 동작

🎯 실전 적용 사례:
- 비즈니스 인텔리전스 시스템
- 연구 데이터 분석 파이프라인
- 고객 지원 시스템
- 콘텐츠 생성 및 관리
""")

print("\n" + "=" * 70)
print("✅ Phase 6 예제 3 완료!")
print("=" * 70)
print()
print("🎉 다음 단계:")
print("  - 예제 4: 실전 시나리오 Agent")
print("  - 종합적인 문제 해결 능력 검증")
print("  - 프로덕션 수준의 Agent 구현")
print("  - 성능 최적화 및 안정성 확보")
print()
