# Step 1 - 예제 3 실행 결과

## 실행 일시
2025-12-07

## 사용 모델
- **LLM**: Anthropic Claude 3 Haiku (claude-3-haiku-20240307)
- **Temperature**: 0 (일관된 답변)

---

## 예제 목표

**체인 재사용성 학습**
- 한 번 정의한 체인을 여러 입력값으로 반복 실행
- 반복문을 통한 효율적인 데이터 처리

---

## 요청 내용

### PromptTemplate 정의
```python
template = "{country}의 수도는 어디인가요? 간단히 답변해주세요."

prompt = PromptTemplate(
    input_variables=["country"],
    template=template
)
```

### 체인 구성
```python
llm = ChatAnthropic(
    model="claude-3-haiku-20240307",
    temperature=0  # 일관된 답변
)

chain = prompt | llm
```

### 반복 실행 코드
```python
countries = ["대한민국", "일본", "프랑스"]

for country in countries:
    response = chain.invoke({"country": country})
    print(f"{country}: {response.content}")
```

---

## 실행 결과

### 1번째 실행 - 대한민국
**입력:**
```
대한민국의 수도는 어디인가요? 간단히 답변해주세요.
```

**응답:**
```
서울입니다.
```

---

### 2번째 실행 - 일본
**입력:**
```
일본의 수도는 어디인가요? 간단히 답변해주세요.
```

**응답:**
```
일본의 수도는 도쿄입니다.
```

---

### 3번째 실행 - 프랑스
**입력:**
```
프랑스의 수도는 어디인가요? 간단히 답변해주세요.
```

**응답:**
```
프랑스의 수도는 파리입니다.
```

---

## 코드 분석

### 핵심 코드 (step1_example3_multiple_chains.py:43-51)

```python
# 체인 구성 (한 번만!)
chain = prompt | llm

# 여러 입력값으로 재사용
countries = ["대한민국", "일본", "프랑스"]

for country in countries:
    response = chain.invoke({"country": country})
    print(f"{country}: {response.content}")
```

### 동작 원리

각 반복마다:
1. `{"country": "대한민국"}` → `prompt`로 전달
2. `prompt`가 프롬프트 생성: "대한민국의 수도는 어디인가요? 간단히 답변해주세요."
3. 프롬프트가 `llm`으로 전달 (`|` 연산자)
4. `llm`이 응답 생성
5. `response.content`로 결과 출력

이 과정이 3번 반복됩니다.

---

## 핵심 학습 포인트

### 1. 체인 재사용성
```python
# ✅ 좋은 방법: 체인을 한 번만 정의
chain = prompt | llm

for country in countries:
    response = chain.invoke({"country": country})
```

```python
# ❌ 나쁜 방법: 매번 체인 재정의
for country in countries:
    prompt = PromptTemplate(...)
    llm = ChatAnthropic(...)
    chain = prompt | llm  # 불필요한 반복!
    response = chain.invoke({"country": country})
```

**장점:**
- 코드 효율성 향상
- 메모리 절약 (객체 생성 횟수를 줄이게 되어 메모리 할당/해제 횟수가 줄어들고 가비지 컬렉션 부담이 감소)
- 가독성 향상

---

### 2. temperature=0의 의미

```python
llm = ChatAnthropic(
    model="claude-3-haiku-20240307",
    temperature=0  # 결정적 답변
)
```

**temperature 값에 따른 차이:**

| temperature | 특징 | 사용 사례 |
|-------------|------|-----------|
| **0** | 가장 확실한 답변, 일관성 높음 | 사실 정보, 번역, 수학 문제 |
| **0.3-0.5** | 약간의 변화, 적절한 균형 | 일반적인 대화, 요약 |
| **0.7-1.0** | 창의적, 다양한 답변 | 브레인스토밍, 창작 |

**예제 3에서 temperature=0을 사용한 이유:**
- 수도 정보는 **정확한 사실**
- 매번 같은 답변이 필요
- 창의성이 필요 없음

---

### 3. 체인과 반복문의 조합

```python
chain = prompt | llm

# 패턴 1: 단순 반복
for item in items:
    response = chain.invoke({"var": item})

# 패턴 2: 결과 수집
results = []
for item in items:
    response = chain.invoke({"var": item})
    results.append(response.content)

# 패턴 3: 조건부 처리
for item in items:
    response = chain.invoke({"var": item})
    if "특정조건" in response.content:
        # 추가 처리
        pass
```

---

## 예제 2 vs 예제 3 비교

### 예제 2: 단일 실행
```python
chain = prompt | llm

response = chain.invoke({
    "name": "민수",
    "interest": "파이썬 프로그래밍"
})

print(response.content)
```
- **특징**: 한 번만 실행, 복잡한 프롬프트
- **용도**: 상세한 응답이 필요한 경우

### 예제 3: 반복 실행
```python
chain = prompt | llm

for country in ["대한민국", "일본", "프랑스"]:
    response = chain.invoke({"country": country})
    print(response.content)
```
- **특징**: 여러 번 실행, 간단한 프롬프트
- **용도**: 대량의 데이터 처리

---

## 실전 활용 예시

### 1. 대량 번역
```python
chain = translation_prompt | llm

sentences = ["Hello", "Good morning", "Thank you"]
for sentence in sentences:
    translated = chain.invoke({"text": sentence})
    print(translated.content)
```

### 2. 여러 고객에게 개인화된 메시지
```python
chain = email_prompt | llm

customers = [
    {"name": "철수", "product": "노트북"},
    {"name": "영희", "product": "마우스"},
    {"name": "민수", "product": "키보드"}
]

for customer in customers:
    email = chain.invoke(customer)
    print(email.content)
```

### 3. 데이터 분석
```python
chain = analysis_prompt | llm

data_points = [100, 200, 150, 300]
for value in data_points:
    analysis = chain.invoke({"value": value})
    print(analysis.content)
```

---

## 다음 단계

Step 2에서는 **Output Parsing**을 학습합니다:
- LLM의 텍스트 응답을 구조화된 데이터(JSON, Dict)로 변환
- Pydantic 모델을 활용한 타입 안전성 확보

예를 들어:
```python
# 현재 (예제 3): 텍스트 응답
"프랑스의 수도는 파리입니다."

# Step 2: 구조화된 응답
{
    "country": "프랑스",
    "capital": "파리",
    "continent": "유럽"
}
```

---

## 요약

예제 3을 통해 배운 것:
1. ✅ 한 번 정의한 체인을 여러 입력값으로 재사용
2. ✅ temperature=0으로 일관된 답변 생성
3. ✅ 반복문과 체인의 효율적 조합
4. ✅ 프롬프트 템플릿의 재사용성 이해
