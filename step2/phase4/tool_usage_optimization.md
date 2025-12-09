# LLM 도구 사용 최적화 가이드

## 개요

LangChain의 Tool Use 패턴에서 LLM은 **도구 사용을 최소화**하도록 설계되어 있습니다.
이 문서는 그 이유와 실전 활용 방법을 설명합니다.

**핵심 원칙:**
> "도구는 LLM이 **할 수 없는** 일을 위한 것이지,
> LLM이 **할 수 있는** 일을 대체하기 위한 것이 아니다"

---

## 도구 사용 최소화 이유

### 1. 비용 최적화 💰

#### 도구 사용 시 비용 구조

```
시나리오: "파이썬이 뭐야?"

[도구 사용 경로]
1. LLM 호출 (도구 선택)          → $0.001
2. search_web API 호출           → $0.005
3. LLM 호출 (결과 통합)          → $0.001
───────────────────────────────────────
총 비용:                          $0.007

[직접 답변 경로]
1. LLM 호출 (직접 답변)          → $0.001
───────────────────────────────────────
총 비용:                          $0.001
```

**비용 차이: 7배**

#### 대규모 서비스 시나리오

```python
# 일일 100만 쿼리 서비스

# 도구 남용 시 (50% 도구 사용)
daily_cost = 1_000_000 * (0.5 * $0.007 + 0.5 * $0.001)
           = 1_000_000 * $0.004
           = $4,000/일
           = $120,000/월

# 도구 최적화 시 (10% 도구 사용)
daily_cost = 1_000_000 * (0.1 * $0.007 + 0.9 * $0.001)
           = 1_000_000 * $0.0016
           = $1,600/일
           = $48,000/월

절감액: $72,000/월 (60% 절감)
```

---

### 2. 응답 속도 (Latency) ⚡

#### 응답 시간 비교

```python
# 도구 사용 시
시작 → LLM 호출(500ms) → 도구 실행(1000ms) → LLM 호출(500ms) → 완료
총 시간: ~2,000ms

# 직접 답변 시
시작 → LLM 호출(500ms) → 완료
총 시간: ~500ms

속도 차이: 4배
```

#### 사용자 체감 품질

| 응답 시간 | 사용자 반응 | 이탈률 |
|----------|-----------|--------|
| 0~500ms  | "빠르다!" | 2% |
| 500~1000ms | "괜찮다" | 5% |
| 1000~2000ms | "느리다" | 15% |
| 2000ms+ | "너무 느리다" | 30% |

**도구 남용 시 이탈률 6배 증가!**

---

### 3. 신뢰성 및 안정성 🛡️

#### 실패 확률 계산

```
도구 체인의 성공률:

LLM 호출 (99.9% 성공)
    ↓
외부 API 호출 (95% 성공)    ← 네트워크 장애, API 다운타임
    ↓
LLM 호출 (99.9% 성공)

전체 성공률 = 0.999 × 0.95 × 0.999 ≈ 94.8%
```

```
직접 답변 성공률:

LLM 호출 (99.9% 성공)

전체 성공률 = 99.9%
```

**신뢰성 차이: 5% 포인트**

#### 장애 시나리오

```python
# 외부 도구 장애 발생 시

[도구 의존 시스템]
- 날씨 API 다운 → 모든 날씨 질문 실패
- 검색 API 다운 → 모든 검색 질문 실패
→ 서비스 전체 품질 저하

[도구 최소화 시스템]
- 날씨 API 다운 → 날씨 질문만 실패
- 나머지 90% 질문은 정상 작동
→ 부분 장애, 서비스 지속 가능
```

---

### 4. 토큰 효율성 📊

#### 토큰 사용량 비교

```python
# 시나리오: "파이썬이 뭐야?"

[도구 사용 시 메시지 히스토리]
[
    HumanMessage("파이썬이 뭐야?"),                    # 10 tokens
    AIMessage(
        content="",
        tool_calls=[{
            "name": "search_web",
            "args": {"query": "파이썬 프로그래밍 언어"}
        }]
    ),                                                  # 50 tokens
    ToolMessage(
        content="Python은 1991년 귀도 반 로섬이 개발한 "
                "고급 프로그래밍 언어입니다. 간결한 문법과 "
                "풍부한 라이브러리로 인해..."
    ),                                                  # 200 tokens
    AIMessage(
        content="파이썬은 1991년에 개발된 프로그래밍 "
                "언어로, 간결한 문법과 다양한 활용도로..."
    )                                                   # 150 tokens
]
총 토큰: 410 tokens

[직접 답변 시 메시지 히스토리]
[
    HumanMessage("파이썬이 뭐야?"),                    # 10 tokens
    AIMessage(
        content="파이썬은 1991년에 개발된 프로그래밍 "
                "언어로, 간결한 문법과 다양한 활용도로..."
    )                                                   # 150 tokens
]
총 토큰: 160 tokens

토큰 절감: 250 tokens (61% 절감)
```

#### 컨텍스트 윈도우 관리

```python
# 긴 대화 시나리오 (20턴)

[도구 남용]
- 평균 400 tokens/턴
- 20턴 × 400 = 8,000 tokens
- 컨텍스트 윈도우: 8K 초과 → 요약 필요

[도구 최적화]
- 평균 160 tokens/턴
- 20턴 × 160 = 3,200 tokens
- 컨텍스트 윈도우: 8K 이내 → 전체 히스토리 유지 ✅
```

---

### 5. LLM 훈련 철학 🎯

#### Anthropic/OpenAI의 설계 원칙

```
도구는 "보조 수단"이지 "주된 수단"이 아니다

도구를 사용해야 할 때:
✅ 실시간 데이터 (날씨, 주가, 뉴스)
✅ LLM이 모르는 정보 (회사 내부 DB, 최신 이벤트)
✅ 계산/연산 (복잡한 수학, 데이터 처리)
✅ 외부 시스템 조작 (이메일 전송, 파일 생성)

도구 사용 불필요:
❌ LLM이 이미 아는 일반 지식
❌ 간단한 대화 및 인사
❌ 추론/분석 작업
❌ 창의적 작문
```

#### LLM의 내부 판단 로직 (의사 코드)

```python
def should_use_tool(query, tool, llm_knowledge):
    """
    Claude/GPT가 도구를 사용할지 판단하는 로직
    """
    # 1단계: LLM이 이미 아는 정보인가?
    if llm_knowledge.has_answer(query):
        # 실시간 데이터가 필요한가?
        if query.requires_realtime_data():
            return True   # 날씨, 주가 → 도구 사용
        else:
            return False  # 일반 지식 → 직접 답변

    # 2단계: 간단한 대화인가?
    if query.is_simple_conversation():
        return False  # "안녕하세요" → 직접 답변

    # 3단계: 도구가 정말 필요한가?
    if query.requires_external_data():
        return True   # 외부 데이터 필요 → 도구 사용

    if query.requires_computation():
        return True   # 계산 필요 → 도구 사용

    # 4단계: 기본값은 도구 사용 안 함
    return False
```

---

### 6. 사용자 경험 (UX) 😊

#### 도구 남용의 UX 문제

```
사용자: "파이썬이 뭐야?"

[나쁜 UX - 도구 남용]
시스템: 💭 검색 중입니다... (1초)
시스템: 💭 결과를 분석하고 있습니다... (1초)
시스템: 💭 답변을 생성하고 있습니다... (1초)
───────────────────────────────────────
3초 후 답변 제공
사용자: "왜 이렇게 오래 걸려? 😤"

[좋은 UX - 직접 답변]
시스템: 💬 "파이썬은 1991년에..."
───────────────────────────────────────
0.5초 후 즉시 답변
사용자: "빠르네! 👍"
```

#### 대화 흐름의 자연스러움

```
[도구 남용 - 부자연스러움]
사용자: "안녕하세요"
시스템: 💭 search_web("인사말 답변 방법") 호출...
시스템: "안녕하세요! 무엇을 도와드릴까요?"
→ 2초 지연, 부자연스러움

[도구 최적화 - 자연스러움]
사용자: "안녕하세요"
시스템: "안녕하세요! 무엇을 도와드릴까요?"
→ 즉시 응답, 자연스러운 대화
```

---

## 실제 예제 분석

### Example 1 - 시나리오 3: "파이썬이 뭐야?"

```python
# 도구 정의
tools = [get_weather, calculate, search_web]

# 사용자 질문
query = "파이썬이 뭐야?"

# LLM의 판단 과정
"""
1. 질문 분석: "파이썬" = 프로그래밍 언어 정보 요청
2. 지식 확인: LLM 훈련 데이터에 파이썬 정보 있음 ✅
3. 실시간 필요: No (일반 지식)
4. 도구 필요성: No
5. 결정: 직접 답변 제공
"""

# 결과
response.tool_calls = None  # 도구 호출 없음
response.content = "Python은 1991년 귀도 반 로섬이 개발한..."
```

**예상:** search_web 사용
**실제:** 직접 답변
**이유:** LLM이 이미 파이썬에 대해 알고 있음

---

### Example 3 - 시나리오 3: "서울 날씨가 좋으면 추천 장소 알려줘"

```python
# 1단계: 날씨 확인
query_1 = "서울 날씨"

# LLM 판단
"""
1. 질문 분석: "서울 날씨" = 실시간 날씨 정보
2. 지식 확인: LLM은 현재 날씨를 모름
3. 실시간 필요: Yes ✅
4. 도구 필요성: Yes
5. 결정: get_weather 도구 사용
"""
tool_calls = [{"name": "get_weather", "args": {"city": "서울"}}]
result = "맑음, 기온 15도"

# 2단계: 추천 장소
query_2 = "서울 추천 장소"

# LLM 판단
"""
1. 질문 분석: "서울 관광지 추천"
2. 지식 확인: LLM은 서울 관광지를 알고 있음 ✅
3. 실시간 필요: No (일반 지식)
4. 도구 필요성: No
5. 결정: 직접 답변 제공
"""
tool_calls = None
response.content = "날씨가 좋으니 남산, 경복궁, 한강공원..."
```

**예상:** search_web("서울 추천 장소") 사용
**실제:** 직접 답변
**이유:** LLM이 이미 서울 관광지를 알고 있음

---

## 도구 사용 vs 직접 답변 비교표

| 측면 | 도구 사용 | 직접 답변 | 차이 |
|------|----------|----------|------|
| **응답 속도** | 2~5초 | 0.5초 | **4~10배** 빠름 |
| **API 비용** | $0.007 | $0.001 | **7배** 저렴 |
| **토큰 사용** | 410 tokens | 160 tokens | **2.5배** 절약 |
| **신뢰성** | 94.8% | 99.9% | **5%p** 향상 |
| **외부 의존성** | 있음 (API, 네트워크) | 없음 | **독립적** |
| **장애 영향** | 전체 서비스 | 부분적 | **견고함** |
| **컨텍스트 윈도우** | 빠르게 소진 | 느리게 소진 | **2.5배** 효율 |
| **사용자 만족도** | 낮음 (느림) | 높음 (빠름) | **UX 향상** |

**결론: 도구 최소화가 모든 면에서 우수**

---

## 실전 활용 가이드

### 1. 도구 설계 시 명확한 docstring

#### ❌ 나쁜 예

```python
def get_weather(city: str) -> str:
    """날씨 정보를 제공합니다."""
    # ...
```

**문제점:**
- "날씨 정보"가 실시간인지 불명확
- LLM이 자신의 지식으로 답변 가능하다고 오판 가능

#### ✅ 좋은 예

```python
def get_weather(city: str) -> str:
    """
    지정된 도시의 **실시간** 날씨 정보를 조회합니다.

    이 도구는 현재 기온, 날씨 상태, 습도 등의 최신 정보를 제공합니다.
    역사적 날씨 데이터나 일반적인 기후 정보는 제공하지 않습니다.

    Args:
        city: 날씨를 조회할 도시 이름 (예: "서울", "뉴욕")

    Returns:
        현재 날씨 정보 문자열 (예: "맑음, 기온 15도")
    """
    # ...
```

**개선점:**
- "실시간" 명시 → LLM이 도구 필요성 인지
- 구체적인 기능 설명 → 정확한 사용 판단
- 예시 제공 → 입력/출력 형식 명확화

---

### 2. 도구 호출 강제 (필요 시)

#### 방법 1: Few-shot 예제로 유도

```python
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

messages = [
    SystemMessage(
        content="날씨 관련 질문에는 반드시 get_weather 도구를 사용하세요. "
                "일반 지식으로 답변하지 마세요."
    ),

    # Few-shot 예제
    HumanMessage(content="서울 날씨는?"),
    AIMessage(
        content="",
        tool_calls=[{
            "name": "get_weather",
            "args": {"city": "서울"}
        }]
    ),

    # 실제 사용자 질문
    HumanMessage(content="부산 날씨는?")
]

response = llm_with_tools.invoke(messages)
# → get_weather('부산') 호출 확률 증가
```

#### 방법 2: tool_choice 파라미터 (OpenAI)

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4")
llm_with_tools = llm.bind_tools(
    tools=[get_weather],
    tool_choice={
        "type": "function",
        "function": {"name": "get_weather"}
    }
)

# get_weather 도구를 강제로 호출
response = llm_with_tools.invoke([
    HumanMessage(content="서울 날씨는?")
])
```

#### 방법 3: 조건부 검증

```python
response = llm_with_tools.invoke(messages)

# 날씨 질문인데 도구를 안 썼다면?
if "날씨" in user_query and not response.tool_calls:
    print("⚠️ 경고: 날씨 질문에 도구를 사용하지 않음")

    # 재시도 또는 수동 도구 호출
    weather_result = get_weather(extract_city(user_query))
```

---

### 3. 도구 사용 모니터링

#### 기본 통계 수집

```python
class ToolUsageMonitor:
    def __init__(self):
        self.stats = {
            "total_queries": 0,
            "tool_used": 0,
            "direct_answer": 0,
            "tool_usage_by_name": {}
        }

    def record_query(self, response):
        self.stats["total_queries"] += 1

        if response.tool_calls:
            self.stats["tool_used"] += 1
            for tool_call in response.tool_calls:
                tool_name = tool_call["name"]
                self.stats["tool_usage_by_name"][tool_name] = \
                    self.stats["tool_usage_by_name"].get(tool_name, 0) + 1
        else:
            self.stats["direct_answer"] += 1

    def get_tool_usage_rate(self):
        if self.stats["total_queries"] == 0:
            return 0.0
        return self.stats["tool_used"] / self.stats["total_queries"]

    def report(self):
        total = self.stats["total_queries"]
        tool_rate = self.get_tool_usage_rate()

        print(f"📊 도구 사용 통계")
        print(f"  총 쿼리: {total}")
        print(f"  도구 사용: {self.stats['tool_used']} ({tool_rate:.1%})")
        print(f"  직접 답변: {self.stats['direct_answer']} ({1-tool_rate:.1%})")
        print(f"\n  도구별 사용:")
        for tool, count in self.stats["tool_usage_by_name"].items():
            print(f"    - {tool}: {count}회")

# 사용
monitor = ToolUsageMonitor()

for query in user_queries:
    response = llm_with_tools.invoke([HumanMessage(content=query)])
    monitor.record_query(response)

monitor.report()
```

#### 이상 탐지 및 알림

```python
def check_tool_usage_health(monitor):
    """도구 사용 패턴 이상 탐지"""
    tool_rate = monitor.get_tool_usage_rate()

    # 도구 과다 사용
    if tool_rate > 0.5:
        print("⚠️ 경고: 도구 사용률이 50%를 초과했습니다.")
        print("   - 도구 docstring이 너무 광범위하지 않은지 확인")
        print("   - LLM이 직접 답변 가능한 질문에도 도구를 쓰고 있는지 검토")
        print(f"   - 현재 사용률: {tool_rate:.1%}")

    # 도구 과소 사용 (실시간 데이터 도구의 경우)
    weather_usage = monitor.stats["tool_usage_by_name"].get("get_weather", 0)
    if weather_usage < monitor.stats["total_queries"] * 0.05:
        print("⚠️ 경고: 날씨 도구 사용률이 5% 미만입니다.")
        print("   - 날씨 질문이 있는데 도구를 안 쓰고 있는지 확인")
        print(f"   - 현재 사용: {weather_usage}회")

# 주기적 체크
check_tool_usage_health(monitor)
```

---

### 4. 도구 입력 검증 및 정규화

#### 문제: 언어 불일치

```python
# Phase 4 Example 3에서 발견된 문제
def get_weather(city: str) -> str:
    weather_data = {
        "서울": "맑음, 15도",  # 한글 키
        "뉴욕": "흐림, 10도"
    }
    return weather_data.get(city, f"{city}의 날씨 정보 없음")

# 문제 발생
get_weather("Seoul")  # → "Seoul의 날씨 정보 없음" ❌
```

#### 해결 1: 매핑 테이블

```python
def get_weather(city: str) -> str:
    """
    지정된 도시의 실시간 날씨를 조회합니다.

    Args:
        city: 도시 이름 (한글 또는 영어)
    """
    # 영어 → 한글 변환
    CITY_MAPPING = {
        "seoul": "서울",
        "new york": "뉴욕",
        "tokyo": "도쿄",
        "paris": "파리",
        "london": "런던"
    }

    # 정규화: 소문자 변환
    city_normalized = city.lower().strip()

    # 변환 시도
    city_kr = CITY_MAPPING.get(city_normalized, city)

    # 날씨 데이터
    weather_data = {
        "서울": "맑음, 기온 15도",
        "뉴욕": "흐림, 기온 10도",
        "도쿄": "비, 기온 18도",
        "파리": "눈, 기온 2도",
        "런던": "안개, 기온 8도"
    }

    return weather_data.get(city_kr, f"{city}의 날씨 정보를 찾을 수 없습니다.")

# 테스트
print(get_weather("Seoul"))     # ✅ "맑음, 기온 15도"
print(get_weather("서울"))      # ✅ "맑음, 기온 15도"
print(get_weather("NEW YORK"))  # ✅ "흐림, 기온 10도"
```

#### 해결 2: 다국어 키 지원

```python
def get_weather(city: str) -> str:
    """실시간 날씨를 조회합니다 (한글/영어 모두 지원)."""

    # 소문자 변환
    city = city.lower().strip()

    # 다국어 키
    weather_data = {
        "서울": "맑음, 기온 15도",
        "seoul": "맑음, 기온 15도",
        "뉴욕": "흐림, 기온 10도",
        "new york": "흐림, 기온 10도",
        "도쿄": "비, 기온 18도",
        "tokyo": "비, 기온 18도"
    }

    return weather_data.get(city, f"{city}의 날씨 정보를 찾을 수 없습니다.")
```

---

### 5. 도구 실패 처리 및 재시도

#### 기본 에러 처리

```python
def execute_tool_safely(tool_call):
    """도구를 안전하게 실행 (에러 처리 포함)"""
    tool_name = tool_call["name"]
    tool_args = tool_call["args"]

    try:
        # 도구 실행
        if tool_name == "get_weather":
            result = get_weather(**tool_args)
        elif tool_name == "calculate":
            result = calculate(**tool_args)
        else:
            result = f"알 수 없는 도구: {tool_name}"

        # 결과 검증
        if "찾을 수 없습니다" in result or "오류" in result:
            print(f"⚠️ 도구 실행 실패: {tool_name}")
            return {
                "success": False,
                "result": result,
                "error": "Tool execution failed"
            }

        return {
            "success": True,
            "result": result
        }

    except Exception as e:
        print(f"❌ 도구 실행 예외: {tool_name} - {str(e)}")
        return {
            "success": False,
            "result": None,
            "error": str(e)
        }
```

#### 재시도 로직

```python
def execute_tool_with_retry(tool_call, max_retries=2):
    """도구 실행 실패 시 재시도"""

    for attempt in range(max_retries):
        result = execute_tool_safely(tool_call)

        if result["success"]:
            return result["result"]

        # 실패 시 매개변수 변환 시도
        if attempt < max_retries - 1:
            print(f"  재시도 {attempt + 1}/{max_retries - 1}...")

            # 예: 영어 도시명을 한글로 변환 재시도
            if tool_call["name"] == "get_weather":
                city = tool_call["args"]["city"]
                # 변환 로직
                city_mapping = {"Seoul": "서울", "New York": "뉴욕"}
                if city in city_mapping:
                    tool_call["args"]["city"] = city_mapping[city]
                    continue

        # 최종 실패
        return result.get("result", f"도구 실행 실패: {result.get('error')}")
```

---

## 베스트 프랙티스

### 1. 도구 설계 체크리스트

```markdown
✅ docstring에 "실시간", "최신", "현재" 등 키워드 포함 (실시간 도구인 경우)
✅ 도구의 목적과 기능을 명확히 설명
✅ Args와 Returns를 구체적으로 문서화
✅ 예시 포함 (입력/출력 샘플)
✅ LLM이 오판할 수 있는 모호한 표현 제거
```

#### 예시

```python
def get_stock_price(symbol: str) -> str:
    """
    ✅ 지정된 주식의 **실시간** 가격을 조회합니다.

    ✅ 이 도구는 현재 주식 시장의 최신 가격 정보를 제공합니다.
    역사적 주가 데이터나 예측 정보는 제공하지 않습니다.

    ✅ Args:
        symbol: 주식 심볼 (예: "AAPL", "GOOGL", "TSLA")

    ✅ Returns:
        현재 주가 정보 (예: "AAPL: $182.50 (+1.2%)")

    ✅ Example:
        >>> get_stock_price("AAPL")
        "AAPL: $182.50 (+1.2%)"
    """
    # ...
```

---

### 2. 도구 사용률 목표

```python
# 권장 도구 사용률

도구 유형별 목표:

[실시간 데이터 도구]
- get_weather: 5~15%
- get_stock_price: 3~10%
- search_news: 5~15%
목표: 실시간 정보 요청 시에만 사용

[계산 도구]
- calculate: 5~20%
- analyze_data: 10~25%
목표: 복잡한 계산 시에만 사용

[외부 시스템 도구]
- send_email: 1~5%
- create_file: 2~8%
목표: 명시적 요청 시에만 사용

[전체 도구 사용률]
목표: 10~30%
경고: 50% 초과 시 최적화 필요
```

---

### 3. 모니터링 대시보드

```python
import time
from datetime import datetime

class ToolUsageDashboard:
    def __init__(self):
        self.queries = []

    def log_query(self, query, response, latency):
        """쿼리 로깅"""
        self.queries.append({
            "timestamp": datetime.now(),
            "query": query,
            "tool_used": bool(response.tool_calls),
            "tool_calls": response.tool_calls or [],
            "latency": latency
        })

    def generate_report(self, last_n_hours=24):
        """대시보드 리포트 생성"""
        cutoff = datetime.now() - timedelta(hours=last_n_hours)
        recent = [q for q in self.queries if q["timestamp"] > cutoff]

        total = len(recent)
        tool_used = sum(1 for q in recent if q["tool_used"])

        # 평균 지연시간
        avg_latency_tool = sum(q["latency"] for q in recent if q["tool_used"]) / tool_used if tool_used > 0 else 0
        avg_latency_direct = sum(q["latency"] for q in recent if not q["tool_used"]) / (total - tool_used) if total > tool_used else 0

        print(f"\n📊 도구 사용 대시보드 (최근 {last_n_hours}시간)")
        print(f"{'='*60}")
        print(f"총 쿼리: {total}")
        print(f"도구 사용: {tool_used} ({tool_used/total*100:.1f}%)")
        print(f"직접 답변: {total-tool_used} ({(total-tool_used)/total*100:.1f}%)")
        print(f"\n평균 응답 시간:")
        print(f"  - 도구 사용 시: {avg_latency_tool:.2f}초")
        print(f"  - 직접 답변 시: {avg_latency_direct:.2f}초")
        print(f"  - 속도 차이: {avg_latency_tool/avg_latency_direct:.1f}배" if avg_latency_direct > 0 else "")

        # 도구별 사용 횟수
        tool_counts = {}
        for q in recent:
            for tc in q.get("tool_calls", []):
                tool_counts[tc["name"]] = tool_counts.get(tc["name"], 0) + 1

        if tool_counts:
            print(f"\n도구별 사용 횟수:")
            for tool, count in sorted(tool_counts.items(), key=lambda x: x[1], reverse=True):
                print(f"  - {tool}: {count}회 ({count/total*100:.1f}%)")

# 사용 예시
dashboard = ToolUsageDashboard()

for query in user_queries:
    start = time.time()
    response = llm_with_tools.invoke([HumanMessage(content=query)])
    latency = time.time() - start

    dashboard.log_query(query, response, latency)

dashboard.generate_report(last_n_hours=24)
```

---

### 4. A/B 테스트

```python
def ab_test_tool_optimization():
    """도구 최적화 효과 측정"""

    # A그룹: 기본 설정 (도구 최소화 없음)
    llm_a = ChatAnthropic(model="claude-3-haiku-20240307")
    tools_a = [get_weather_basic, calculate, search_web]
    llm_with_tools_a = llm_a.bind_tools(tools_a)

    # B그룹: 최적화 설정 (명확한 docstring, 실시간 키워드)
    llm_b = ChatAnthropic(model="claude-3-haiku-20240307")
    tools_b = [get_weather_optimized, calculate, search_web]
    llm_with_tools_b = llm_b.bind_tools(tools_b)

    test_queries = [
        "파이썬이 뭐야?",
        "서울 날씨는?",
        "123 곱하기 456은?",
        "안녕하세요"
    ]

    results = {"A": [], "B": []}

    for query in test_queries:
        # A 그룹
        start = time.time()
        response_a = llm_with_tools_a.invoke([HumanMessage(content=query)])
        latency_a = time.time() - start
        results["A"].append({
            "query": query,
            "tool_used": bool(response_a.tool_calls),
            "latency": latency_a
        })

        # B 그룹
        start = time.time()
        response_b = llm_with_tools_b.invoke([HumanMessage(content=query)])
        latency_b = time.time() - start
        results["B"].append({
            "query": query,
            "tool_used": bool(response_b.tool_calls),
            "latency": latency_b
        })

    # 결과 분석
    print("A/B 테스트 결과:")
    for group in ["A", "B"]:
        tool_rate = sum(1 for r in results[group] if r["tool_used"]) / len(results[group])
        avg_latency = sum(r["latency"] for r in results[group]) / len(results[group])
        print(f"\n그룹 {group}:")
        print(f"  도구 사용률: {tool_rate:.1%}")
        print(f"  평균 지연시간: {avg_latency:.2f}초")
```

---

## 요약

### 핵심 원칙

**도구 사용 최소화 = 비용↓ + 속도↑ + 신뢰성↑**

1. **비용**: 7배 절감
2. **속도**: 4배 향상
3. **토큰**: 2.5배 효율
4. **신뢰성**: 5%p 향상
5. **UX**: 사용자 만족도 증가

### 실천 가이드

```python
# 1. 명확한 docstring (실시간 키워드)
def get_weather(city: str) -> str:
    """**실시간** 날씨를 조회합니다."""

# 2. 입력 검증 및 정규화
city = city.lower().strip()
city_kr = CITY_MAPPING.get(city, city)

# 3. 도구 사용 모니터링
monitor = ToolUsageMonitor()
monitor.record_query(response)

# 4. 목표 사용률 유지
if tool_usage_rate > 0.5:
    print("⚠️ 도구 과다 사용")

# 5. A/B 테스트로 최적화 검증
```

### 언제 도구를 사용해야 하는가?

```
✅ 사용:
- 실시간 데이터 (날씨, 주가, 뉴스)
- LLM이 모르는 정보 (내부 DB, 최신 이벤트)
- 계산/연산 (복잡한 수학)
- 외부 시스템 조작 (이메일, 파일)

❌ 불필요:
- LLM이 아는 일반 지식
- 간단한 대화
- 추론/분석
- 창의적 작문
```

**"필요할 때만, 정확하게, 효율적으로"**
