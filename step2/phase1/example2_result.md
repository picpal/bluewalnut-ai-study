# Step 1 - 예제 2 실행 결과

## 실행 일시
2025-12-07

## 사용 모델
- **LLM**: Anthropic Claude 3 Haiku (claude-3-haiku-20240307)
- **Temperature**: 0.7

---

## 요청 내용

### PromptTemplate 정의
```python
template = """당신은 친절한 AI 어시스턴트입니다.
사용자의 이름은 {name}이고, 관심사는 {interest}입니다.

사용자에게 관심사와 관련된 추천을 3가지 해주세요."""
```

### 입력 변수
```python
{
    "name": "민수",
    "interest": "파이썬 프로그래밍"
}
```

### 최종 프롬프트 (변수 삽입 후)
```
당신은 친절한 AI 어시스턴트입니다.
사용자의 이름은 민수이고, 관심사는 파이썬 프로그래밍입니다.

사용자에게 관심사와 관련된 추천을 3가지 해주세요.
```

---

## LLM 응답

안녕하세요 민수님. 파이썬 프로그래밍에 관심이 많으시다니 정말 좋습니다. 저는 민수님께 다음과 같은 3가지 추천을 해드리고 싶습니다:

### 1. 파이썬 기초 문법 및 데이터 구조 심화 학습
파이썬의 기본 문법과 리스트, 튜플, 딕셔너리 등 다양한 데이터 구조에 대해 깊이 있게 공부해보세요. 이를 통해 파이썬 언어의 핵심 기능을 완벽히 이해할 수 있습니다.

### 2. 파이썬 라이브러리 활용 실습
NumPy, Pandas, Matplotlib 등 파이썬의 강력한 데이터 분석 및 시각화 라이브러리를 활용해 실습해보세요. 이를 통해 실제 문제 해결에 파이썬을 적용하는 능력을 기를 수 있습니다.

### 3. 파이썬 프로젝트 수행
파이썬으로 직접 프로젝트를 수행해보세요. 예를 들어 웹 스크래핑, 자동화 프로그램 개발, 머신러닝 모델 구현 등 다양한 프로젝트를 직접 해보면서 실무 경험을 쌓을 수 있습니다.

이러한 추천들이 민수님의 파이썬 프로그래밍 학습에 도움이 되었으면 합니다. 더 궁금한 점이 있다면 언제든 말씀해 주세요.

---

## 코드 흐름

```python
# 1. PromptTemplate 생성
prompt = PromptTemplate(
    input_variables=["name", "interest"],
    template=template
)

# 2. LLM 설정
llm = ChatAnthropic(
    model="claude-3-haiku-20240307",
    temperature=0.7
)

# 3. LCEL 체인 구성 (핵심!)
chain = prompt | llm

# 4. 체인 실행
response = chain.invoke({
    "name": "민수",
    "interest": "파이썬 프로그래밍"
})
```

---

## 핵심 학습 포인트

### 1. 파이프 연산자 `|`
```python
chain = prompt | llm
```
- PromptTemplate과 LLM을 연결
- LCEL(LangChain Expression Language)의 핵심 문법
- "프롬프트 출력 → LLM 입력"으로 데이터 흐름 생성

### 2. chain.invoke()
```python
response = chain.invoke({"name": "민수", "interest": "파이썬 프로그래밍"})
```
- 체인 전체를 실행
- 내부적으로 각 단계를 순차 실행:
  1. 입력 데이터 → PromptTemplate
  2. 포맷된 프롬프트 → LLM
  3. LLM 응답 반환

### 3. response.content
```python
print(response.content)
```
- `response`는 `AIMessage` 객체
- `.content`로 실제 텍스트에 접근

---

## PromptTemplate 사용의 장점

### Before (하드코딩)
```python
prompt_text = f"당신은 친절한 AI 어시스턴트입니다.\n사용자의 이름은 {name}이고..."
response = llm.invoke(prompt_text)
```

### After (PromptTemplate)
```python
chain = prompt | llm
response = chain.invoke({"name": name, "interest": interest})
```

**장점:**
1. **재사용성**: 같은 템플릿을 다른 입력값으로 반복 사용
2. **가독성**: 프롬프트 구조가 명확
3. **확장성**: 체인에 다른 컴포넌트 추가 가능 (`prompt | llm | parser`)
4. **검증**: `input_variables`로 필수 변수 명시

---

## 다음 단계

예제 3에서는 이 체인을 여러 입력값으로 **반복 실행**하는 방법을 학습합니다.

```python
countries = ["대한민국", "일본", "프랑스", "브라질"]

for country in countries:
    response = chain.invoke({"country": country})
    print(response.content)
```
