# LangChain 학습 로드맵

## 학습 목표
LangChain의 핵심 개념을 단계별로 이해하고 실습한다. 오버스펙보다는 **개념의 명확한 이해**에 집중한다.

## 환경 설정
- **언어**: Python 3.11+
- **주요 라이브러리**: langchain, langchain-openai (또는 langchain-anthropic)
- **브랜치 전략**: 각 단계별로 브랜치 생성 후 완료 시 main에 merge

---

## Step 1: LangChain + PromptTemplate + Prompt | LLM 체인

### 목표
- LangChain의 기본 구조 이해
- PromptTemplate으로 동적 프롬프트 생성
- 간단한 LLM 체인 구성

### 구현 내용
- PromptTemplate 생성 및 변수 삽입
- LLM 호출 (OpenAI 또는 Anthropic)
- 기본 체인 연결: `prompt | llm`

### 예제 시나리오
- 사용자 이름을 입력받아 개인화된 인사말 생성

### 학습 포인트
- Runnable 인터페이스의 개념
- LCEL(LangChain Expression Language) 파이프 연산자 `|`의 의미

---

## Step 2: Output Parsing (JSON/Dict)

### 목표
- LLM 출력을 구조화된 데이터로 변환
- Pydantic 모델 기반 출력 파싱

### 구현 내용
- `PydanticOutputParser` 또는 `StructuredOutputParser` 사용
- LLM 응답을 JSON으로 파싱
- 체인에 파서 추가: `prompt | llm | parser`

### 예제 시나리오
- "영화 제목과 감독 추출" - LLM에게 영화 정보를 요청하고 JSON으로 파싱

### 학습 포인트
- OutputParser의 역할
- Pydantic 모델 정의 방법
- 파싱 실패 시 에러 핸들링

---

## Step 3: Function Calling — 단일 함수

### 목표
- LLM의 Function Calling 기능 이해
- 단일 함수 바인딩 및 호출

### 구현 내용
- Python 함수 정의 (예: 날씨 조회, 계산기)
- LLM에 함수 스키마 바인딩
- LLM이 함수 호출 여부 판단하도록 설정

### 예제 시나리오
- "서울의 날씨 알려줘" → LLM이 `get_weather("Seoul")` 함수 호출 판단

### 학습 포인트
- `bind_tools()` 메서드
- 함수 스키마 정의 (매개변수, 반환값)
- LLM의 함수 호출 판단 로직

---

## Step 4: Tool Use — 여러 함수 + 수동 실행 루프

### 목표
- 여러 도구를 LLM이 선택하도록 설정
- 수동 루프로 도구 실행 제어

### 구현 내용
- 여러 함수(도구) 정의: 날씨, 계산기, 검색 등
- LLM이 적절한 도구 선택
- 수동 while 루프로 도구 실행 및 결과 피드백

### 예제 시나리오
- "서울 날씨와 뉴욕 날씨를 비교해줘" → 날씨 도구를 두 번 호출

### 학습 포인트
- 도구 선택 로직
- 도구 실행 결과를 LLM에 다시 전달하는 방법
- 반복 호출의 종료 조건

---

## Step 5: Workflow — LCEL 기반 다단계 파이프라인

### 목표
- LCEL을 활용한 복잡한 워크플로우 구성
- 여러 단계를 체인으로 연결

### 구현 내용
- 다단계 체인: 입력 → 요약 → 번역 → 분석
- `RunnableSequence` 또는 `RunnableParallel` 활용
- 중간 결과를 다음 단계로 전달

### 예제 시나리오
- 긴 영문 기사를 입력 → 요약 → 한글 번역 → 핵심 키워드 추출

### 학습 포인트
- LCEL의 조합 가능성
- 병렬 실행 vs 순차 실행
- 중간 단계의 상태 관리

---

## Step 6: Agent — Tool 자동 선택 + ReAct 루프

### 목표
- LangChain Agent 개념 이해
- ReAct(Reasoning + Acting) 패턴 학습

### 구현 내용
- `create_react_agent()` 또는 `AgentExecutor` 사용
- 도구 자동 선택 및 반복 실행
- Agent가 스스로 작업 완료 판단

### 예제 시나리오
- "오늘 서울 날씨를 확인하고, 비가 오면 우산 추천 메시지 작성해줘"
  → Agent가 날씨 도구 호출 → 결과 분석 → 조건부 메시지 생성

### 학습 포인트
- Agent의 자율성
- ReAct 루프의 동작 원리 (Thought → Action → Observation)
- Agent 종료 조건 및 최대 반복 횟수

---

## Step 7: Prompt Chain & 디버깅 — 단계별 로그/튜닝

### 목표
- 복잡한 프롬프트 체인 최적화
- 디버깅 및 로깅 기법 습득

### 구현 내용
- `langchain.globals.set_debug(True)` 활성화
- 각 단계별 중간 출력 로깅
- 프롬프트 튜닝 (few-shot 예제 추가, 지시문 개선)

### 예제 시나리오
- Step 6의 Agent 실행 과정을 상세히 로깅하고 성능 개선

### 학습 포인트
- 디버깅 모드 활성화
- LangSmith 또는 콜백 핸들러 사용
- 프롬프트 품질이 결과에 미치는 영향
- 토큰 사용량 모니터링

---

## 브랜치 전략

```
main
 ├─ step1-prompt-chain
 ├─ step2-output-parsing
 ├─ step3-function-calling
 ├─ step4-tool-use
 ├─ step5-workflow
 ├─ step6-agent
 └─ step7-debugging
```

각 단계 완료 후 main에 merge하여 점진적으로 학습 내용을 누적한다.

---

## 실습 진행 방식

1. **브랜치 생성**: `git checkout -b step1-prompt-chain`
2. **코드 작성**: 해당 단계의 개념을 담은 최소한의 코드
3. **README 업데이트**: 각 단계별 학습 내용과 실행 방법 기록
4. **테스트 및 확인**: 코드 실행 및 결과 검증
5. **Merge**: `git checkout main && git merge step1-prompt-chain`

---

## 참고 자료
- [LangChain 공식 문서](https://python.langchain.com/)
- [LCEL 가이드](https://python.langchain.com/docs/expression_language/)
- [Agent 튜토리얼](https://python.langchain.com/docs/modules/agents/)
