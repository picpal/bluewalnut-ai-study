**개요**
- 목적: `todo/` 내 생성물(claude, codex, gemini)의 `index.html`(claude는 `todo-app.html`)을 기능/구조/TDD/접근성 측면에서 비교 분석.
- 실행 결과: claude, codex는 정상 동작 확인. gemini는 페이지 로드 후 UI는 보이지만 상호작용 일부가 정상 동작하지 않는 문제가 재현됨(아래 세부 원인 추정 포함).

**평가 기준**
- 기능: 추가/토글/삭제/필터/검색/마감일/우선순위/영속화(LocalStorage) 동작 여부와 오류 처리.
- 구조: 상태 관리 분리, 순수 함수 여부, DOM 렌더/이벤트 위임 구조.
- TDD: 테스트 범위, 격리성(실행 환경 오염 최소화), 보고 방식.
- 접근성/UX: 키보드 사용성, ARIA, 피드백(카운트/빈 상태), 반응형/시각 피드백.

**Claude 분석 (todo/claude/todo-app.html)**
- 구조: 순수 도메인 로직(create/toggle/delete/filter/stats) → 렌더러(renderTodoItem/renderTodoList) → 이벤트(initApp)로 명확히 분리. 상태는 모듈 스코프(todos, nextId)로 관리.
- 기능: 추가/토글/삭제/필터(전체/미완료/완료/우선순위별), 마감일 표시(지남 경고), 통계 카드(전체/완료/미완료), LocalStorage 저장·복원까지 구현.
- TDD: 자체 어설션(assert/assertEqual) + 스위트별 테스트 22개 수준. 페이지 로드시 테스트 실행 후 앱 초기화. 테스트는 로직 단위가 중심이며 UI는 주로 동작 확인 위주.
- 접근성/UX: 빈 상태 화면, 큰 클릭 타겟, 키보드 포커스 표시, ARIA 라벨 일부 적용. 반응형 레이아웃 및 마이크로 인터랙션(hover/animation) 양호.
- 장점: 기능 범위와 구현 완성도가 높고, 코드 가독성/모듈화가 좋음. 에러 처리와 사용자 피드백(알림/상태 갱신) 일관.
- 개선 제안: 
  - 테스트가 LocalStorage 키를 앱과 공유(‘todos’) → 테스트-앱 간 상태 간섭 가능. 테스트용 네임스페이스 분리 권장.
  - 상태를 클래스로 캡슐화하면(예: Store) 테스트/확장 용이성 추가 개선.

**Codex 분석 (todo/codex/index.html)**
- 구조: 순수 유틸(uid/create/toggle/update/filter/search) + `StorageAdapter` + `TodoStore`(상태/영속화) + 얇은 UI 레이어(render, 이벤트 핸들러)로 정돈. DOM 헬퍼(`$`, `$$`) 간결.
- 기능: 추가/토글/삭제/간단 편집(prompt), 필터(전체/미완료/완료), 검색, 우선순위 배지, 마감일 상대 표기(오늘/남은일/만료), LocalStorage 보존.
- TDD: 경량 테스트 러너(Test.run/assert) + `MemoryStorage`로 저장소 격리. 순수 함수와 Store 로직을 중점적으로 검증하며 콘솔 리포트 제공(통과/실패 요약). 테스트-실행 간섭 최소.
- 접근성/UX: 필터 `aria-pressed` 토글, 라이브 카운트, 빈 상태 안내, 키보드 포커스 경로 자연스러움. 반응형/명확한 콘트라스트.
- 장점: 계층 분리가 명확하고 테스트 격리가 우수. 렌더/상태 전이 단순-직관. 안정적인 예외 처리와 XSS 방지(escapeHtml) 반영.
- 개선 제안: 
  - 편집 UI를 프롬프트 대신 인라인 편집으로 개선 여지.
  - 간단한 E2E 상호작용 테스트(예: add→toggle→filter 흐름) 보강 가능.

**Gemini 분석 (todo/gemini/index.html)**
- 구조: 순수 함수(add/delete/toggle/filter/storage) + 전역 `appState`(todos/filter) + 렌더(템플릿 문자열) + 이벤트 위임 구조. 테스트 러너 내장(TestRunner.test/expect/run)로 결과 패널 제공.
- 기능: 추가/토글/삭제, 필터(전체/미완료/완료), 우선순위/마감일 표시, LocalStorage 저장·복원 구현. 기본 UX는 단순하고 직관적.
- TDD: 핵심 로직과 Storage에 대한 단위 테스트 포함. 다만 테스트가 실제 LocalStorage 키(`todos`)를 사용하여 러닝 타임 상태와 충돌 가능.
- 접근성/UX: 기본적인 시각 피드백은 양호. ARIA/키보드 관련 세부 배려는 상대적으로 적음.
- 관찰된 문제(실행 시 동작 불능):
  - 증상: 초기 렌더/테스트 출력은 보이나, 항목 추가/삭제/토글 등의 상호작용 시 에러로 동작 중단되는 케이스가 발생.
  - 유력 원인 추정:
    - 이벤트 위임 가드 미흡: 클릭 타깃에 대해 `e.target.classList.contains(...)` 또는 `e.target.closest(...)`를 직접 호출. `e.target`이 항상 `Element`라는 가정이 깨질 경우(특정 브라우저/플러그인/컴포넌트 변형) 런타임 에러 발생 가능. 안전하게 `const el = e.target instanceof Element ? e.target : null;` 가드 후 `el.closest(...)` 사용 권장.
    - 테스트와 앱의 LocalStorage 키 충돌: 테스트가 `localStorage.setItem('todos', ...)`를 사용하여 실행 직후 상태를 오염. 초기 구동/렌더 타이밍에 비일관 데이터로 인해 예외 상황(파싱/렌더 가정 불일치) 가능.
    - 키보드 처리 `keypress` 사용: 현대 브라우저에서 비권장. `keydown`/`keyup`으로 교체 필요. 환경에 따라 Enter 처리 누락 가능.
    - 중첩 템플릿 리터럴 사용: 렌더 템플릿 내 `${ todo.dueDate ? \
      `<span>...</span>` : '' }` 형태는 문법상 유효하지만 복잡도 상승으로 치명적 오타가 발생하기 쉬움. 간단한 헬퍼(함수)로 분리 권장.
- 수정 제안:
  - 이벤트 위임 안전화: `const el = e.target instanceof Element ? e.target : null; const delBtn = el && el.closest('.btn-delete'); if (delBtn) { ... } else if (el && el.closest('.todo-checkbox')) { ... }` 처럼 분기 명확화. 체크박스 클릭만 토글하도록 제한.
  - 테스트-앱 Storage 분리: 테스트에는 별도 네임스페이스 사용(예: `todos_test`) 또는 In‑Memory mock 도입.
  - 입력 처리: `keypress` → `keydown`으로 교체. Enter만 처리하도록 분기 명확화.
  - 렌더 분리: 작은 DOM 생성 헬퍼를 사용하거나 조건부 마크업을 함수로 추출해 템플릿 중첩 제거.

**종합 비교**
- 안정성: codex ≈ claude > gemini
- 테스트 격리/품질: codex(메모리 어댑터 격리) > claude(공유 키 사용) > gemini(공유 키 + 실행 중 테스트)
- 구조화/가독성: codex(계층 분리 명확) ≥ claude(모듈 분리 양호) > gemini(전역 혼재)
- 접근성/UX: claude(상태 카드/빈 상태/포커스 표시) ≥ codex(라이브 카운트/ARIA) > gemini(기본만 제공)

**권장 개선사항 요약**
- 공통: 테스트와 실행 상태를 격리(별도 Storage 키 또는 메모리 모킹). XSS/에러 처리 일관성 유지.
- gemini: 이벤트 위임 가드 보강, `keypress` → `keydown`, 렌더 템플릿 단순화, 테스트 네임스페이스 분리.
- claude: Store 캡슐화 또는 Adapter 도입으로 테스트/확장성 향상.
- codex: 인라인 편집 UX 개선, 간단한 E2E 흐름 테스트 추가.

**파일 경로 참고**
- claude: `todo/claude/todo-app.html`
- codex: `todo/codex/index.html`
- gemini: `todo/gemini/index.html`

