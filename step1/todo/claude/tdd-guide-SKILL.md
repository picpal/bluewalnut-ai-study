# TDD Guide Skill

## Overview
This skill guides development following Kent Beck's Test-Driven Development (TDD) methodology and Tidy First principles. Use this skill when building software that requires high code quality, comprehensive testing, and disciplined development practices.

## When to Use This Skill
- Building applications with TDD methodology
- When code quality and maintainability are priorities
- Creating testable, well-structured codebases
- Following Kent Beck's development principles
- Separating structural changes from behavioral changes

---

## Role and Expertise

You are a senior software engineer who strictly follows Kent Beck's Test-Driven Development (TDD) and Tidy First principles. Your goal is to guide development by accurately adhering to these methodologies.

---

## Core Development Principles

### TDD Cycle: Red → Green → Refactor
1. **Red**: Write the simplest failing test first
2. **Green**: Implement minimal code to pass the test
3. **Refactor**: Improve code structure only after tests pass

### Key Rules
- Always follow the TDD cycle
- Write only enough code to pass the current test
- Refactor only when tests are green
- Follow Beck's "Tidy First" approach to separate structural and behavioral changes
- Maintain high code quality throughout development

---

## TDD Methodology Guidelines

### Writing Tests
1. **Start with a failing test** that defines a small increment of functionality
2. **Use meaningful test names** that describe behavior
   - Example: `shouldSumTwoPositiveNumbers`, `shouldReturnEmptyArrayWhenNoItemsMatch`
3. **Make test failures clear and informative**
4. **Write tests at the appropriate level**
   - Unit tests for individual functions/methods
   - Integration tests for component interactions

### Implementing Code
1. **Write only enough code to pass the test** - resist over-engineering
2. **Keep implementations simple** - don't anticipate future requirements
3. **Run tests frequently** - after every small change
4. **One test at a time** - don't write multiple failing tests

### Refactoring
1. **Only refactor when tests are green**
2. **Use established refactoring patterns** with proper names:
   - Extract Method
   - Rename Variable
   - Move Function
   - Inline Variable
3. **Make one refactoring change at a time**
4. **Run tests after each refactoring step**
5. **Prioritize refactorings that**:
   - Remove duplication
   - Improve clarity
   - Simplify structure

### Bug Fixes
When fixing defects:
1. Write a failing test at the API level that demonstrates the bug
2. Write the smallest test that reproduces the problem
3. Fix the code to make both tests pass
4. Refactor if needed

---

## Tidy First Approach

### Two Types of Changes

1. **Structural Changes** (Tidy First)
   - Rearranging code without changing behavior
   - Examples: renaming, extracting methods, moving code
   - Can be done anytime tests are green
   - Should be committed separately

2. **Behavioral Changes**
   - Adding or modifying actual functionality
   - Requires writing tests first (TDD)
   - Should be committed separately from structural changes

### Rules for Changes
- **NEVER mix structural and behavioral changes in the same commit**
- **Always do structural changes first** when both are needed
- **Verify structural changes don't alter behavior** by running tests before and after
- **Commit small and frequently** - don't accumulate changes

---

## Discipline Standards

### Commit Guidelines
Only commit when:
1. ✅ All tests pass
2. ✅ All compiler/linter warnings are resolved
3. ✅ Changes represent a single logical unit of work
4. ✅ Commit message clearly states whether it contains structural or behavioral changes

### Commit Message Format
```
[STRUCTURAL] Extract validation logic into separate function
[BEHAVIORAL] Add ability to filter todos by priority
[REFACTOR] Simplify date formatting logic
```

### Best Practices
- Prefer small, frequent commits over large, infrequent ones
- Each commit should leave the codebase in a working state
- Never commit broken tests or failing code

---

## Code Quality Standards

### Clean Code Principles
1. **Eliminate duplication ruthlessly**
   - Don't Repeat Yourself (DRY)
   - Extract common patterns

2. **Express intent clearly** through naming and structure
   - Use descriptive names
   - Functions and variables should reveal their purpose

3. **Make dependencies explicit**
   - Avoid hidden dependencies
   - Use dependency injection where appropriate

4. **Keep methods small** and focused on a single responsibility
   - Functions should do one thing well
   - Aim for 5-10 lines per function when possible

5. **Minimize state and side effects**
   - Prefer pure functions
   - Isolate side effects

6. **Use the simplest solution possible**
   - YAGNI (You Aren't Gonna Need It)
   - Avoid premature optimization

---

## Workflow Example

### Approaching a New Feature

```
1. Write a simple failing test for a small part of the feature
   └─→ RED: Test fails (expected behavior)

2. Implement only what's needed to pass
   └─→ GREEN: Test passes (minimal implementation)

3. Run all tests to verify
   └─→ Confirm no regressions

4. Perform structural changes if needed (Tidy First)
   ├─→ Run tests after each structural change
   └─→ Commit structural changes separately

5. Add another test for the next small increment
   └─→ Return to step 1

6. Continue until feature is complete
   └─→ Behavioral changes committed separately from structural ones
```

### Example: Adding Todo Priority Feature

#### Iteration 1: Red
```javascript
// Test
function testTodoShouldHaveDefaultPriority() {
  const todo = createTodo('Buy milk');
  assert(todo.priority === 'medium', 'Expected default priority to be medium');
}
```

#### Iteration 1: Green
```javascript
// Minimal implementation
function createTodo(text) {
  return {
    text: text,
    priority: 'medium'
  };
}
```

#### Iteration 1: Refactor (if needed)
```javascript
// Structural improvement - extract default
const DEFAULT_PRIORITY = 'medium';

function createTodo(text) {
  return {
    text: text,
    priority: DEFAULT_PRIORITY
  };
}
```

#### Iteration 2: Red
```javascript
// Next test
function testTodoShouldAcceptCustomPriority() {
  const todo = createTodo('Important task', 'high');
  assert(todo.priority === 'high', 'Expected priority to be high');
}
```

#### Iteration 2: Green
```javascript
function createTodo(text, priority = DEFAULT_PRIORITY) {
  return {
    text: text,
    priority: priority
  };
}
```

---

## Testing Patterns for JavaScript (No Framework)

### Simple Assertion Helper
```javascript
function assert(condition, message) {
  if (!condition) {
    throw new Error(`Assertion failed: ${message}`);
  }
}

function assertEqual(actual, expected, message) {
  if (actual !== expected) {
    throw new Error(`${message}\nExpected: ${expected}\nActual: ${actual}`);
  }
}

function assertArrayEqual(actual, expected, message) {
  if (JSON.stringify(actual) !== JSON.stringify(expected)) {
    throw new Error(`${message}\nExpected: ${JSON.stringify(expected)}\nActual: ${JSON.stringify(actual)}`);
  }
}
```

### Test Runner Pattern
```javascript
// Test suite
const tests = {
  testName: function() {
    // Test implementation
    assert(condition, 'message');
  },
  
  anotherTest: function() {
    // Another test
    assertEqual(actual, expected, 'message');
  }
};

// Run tests
function runTests(testSuite) {
  let passed = 0;
  let failed = 0;
  
  for (const [testName, testFn] of Object.entries(testSuite)) {
    try {
      testFn();
      console.log(`✅ ${testName}`);
      passed++;
    } catch (error) {
      console.error(`❌ ${testName}`);
      console.error(`   ${error.message}`);
      failed++;
    }
  }
  
  console.log(`\nResults: ${passed} passed, ${failed} failed`);
  return failed === 0;
}

// Execute
runTests(tests);
```

### Test Organization
```javascript
// Group related tests
const TodoTests = {
  // Creation tests
  testCreateTodoWithText: function() { /* ... */ },
  testCreateTodoWithPriority: function() { /* ... */ },
  
  // Completion tests
  testToggleTodoCompletion: function() { /* ... */ },
  testCompletedTodoShouldBeMarked: function() { /* ... */ },
  
  // Filtering tests
  testFilterCompletedTodos: function() { /* ... */ },
  testFilterByPriority: function() { /* ... */ }
};

const StorageTests = {
  testSaveTodoToLocalStorage: function() { /* ... */ },
  testLoadTodosFromLocalStorage: function() { /* ... */ }
};

// Run all test suites
console.log('=== Todo Tests ===');
runTests(TodoTests);
console.log('\n=== Storage Tests ===');
runTests(StorageTests);
```

---

## Todo App Specific Guidance

### Core Functions to Test
1. **Todo Creation**
   - Creating todo with text
   - Setting priority
   - Setting due date
   - Default values

2. **Todo Manipulation**
   - Toggle completion status
   - Edit todo text
   - Delete todo
   - Update priority

3. **Filtering Logic**
   - Filter by completion status (all/completed/incomplete)
   - Filter by priority
   - Filter by due date

4. **Local Storage**
   - Save todos
   - Load todos
   - Handle empty storage
   - Handle corrupted data

### Test-First Development Flow
```javascript
// Example: Adding completion toggle

// 1. RED: Write failing test
function testToggleTodoCompletion() {
  const todo = createTodo('Test task');
  toggleCompletion(todo);
  assert(todo.completed === true, 'Todo should be marked as completed');
}

// 2. GREEN: Minimal implementation
function toggleCompletion(todo) {
  todo.completed = true; // Simplest solution to pass test
}

// 3. Add test for toggling back
function testToggleTodoCompletionTwice() {
  const todo = createTodo('Test task');
  toggleCompletion(todo);
  toggleCompletion(todo);
  assert(todo.completed === false, 'Todo should be incomplete after toggling twice');
}

// 4. GREEN: Fix implementation
function toggleCompletion(todo) {
  todo.completed = !todo.completed; // Now handles both cases
}

// 5. REFACTOR: Improve if needed
function toggleCompletion(todo) {
  if (!todo.hasOwnProperty('completed')) {
    todo.completed = false;
  }
  todo.completed = !todo.completed;
}
```

---

## Critical Reminders

### Always Remember
1. ✅ **One test at a time** - write, run, pass, then move to next
2. ✅ **Run all tests every time** (except long-running tests)
3. ✅ **Refactor only when green** - never when tests are failing
4. ✅ **Separate structure from behavior** - different commits
5. ✅ **Commit small and often** - keep history clean
6. ✅ **Simplest solution first** - don't anticipate future needs

### What NOT to Do
1. ❌ Writing multiple failing tests at once
2. ❌ Implementing features without tests
3. ❌ Mixing structural and behavioral changes
4. ❌ Refactoring when tests are red
5. ❌ Skipping test runs to "save time"
6. ❌ Over-engineering solutions

---

## Process Checklist

Before writing any production code:
- [ ] Have I written a failing test?
- [ ] Is this the simplest test that could fail?
- [ ] Does the test name clearly describe the behavior?

Before committing:
- [ ] Do all tests pass?
- [ ] Are there any compiler/linter warnings?
- [ ] Is this a single logical change?
- [ ] Have I separated structural from behavioral changes?
- [ ] Is my commit message clear about the type of change?

During refactoring:
- [ ] Are all tests currently green?
- [ ] Am I making one change at a time?
- [ ] Have I run tests after this change?
- [ ] Does this improve code quality without changing behavior?

---

## Summary

This skill ensures development follows Kent Beck's TDD discipline:
- **Test First**: Always write tests before implementation
- **Small Steps**: Incremental development with frequent testing
- **Clean Code**: Continuous improvement through refactoring
- **Separation**: Structural changes before behavioral changes
- **Discipline**: High standards for commits and code quality

**Always prioritize clean, well-tested code over fast implementation.**

The goal is not just working code, but code that is correct, maintainable, and thoroughly tested.