# FastAPI Tests

This directory contains comprehensive test suites for the Mergington High School Activities FastAPI application.

## Test Structure

### Test Files

- **`test_api.py`** - Core API endpoint tests
  - Root endpoint redirection
  - Activities listing endpoint  
  - Signup functionality
  - Unregister functionality
  - Integration workflow tests

- **`test_edge_cases.py`** - Edge cases and error handling
  - Invalid input validation
  - Error response format verification
  - Concurrency scenario testing
  - Data integrity checks

- **`test_static_files.py`** - Frontend integration tests
  - Static file serving (HTML, CSS, JS)
  - Frontend-backend API contract validation
  - Content validation for static assets

- **`conftest.py`** - Test configuration and fixtures
  - Test client setup
  - Activity data reset fixtures
  - Sample data generators

## Running Tests

### Prerequisites

Install test dependencies:
```bash
pip install -r requirements.txt
```

### Run All Tests
```bash
# Basic test run
python -m pytest tests/ -v

# With coverage reporting  
python -m pytest tests/ --cov=src --cov-report=term-missing --cov-report=html

# Using the test runner script
python run_tests.py
```

### Run Specific Test Categories
```bash
# API endpoint tests only
python -m pytest tests/test_api.py -v

# Edge case tests only  
python -m pytest tests/test_edge_cases.py -v

# Frontend integration tests only
python -m pytest tests/test_static_files.py -v
```

### Run Individual Test Classes
```bash
# Test signup functionality
python -m pytest tests/test_api.py::TestSignupEndpoint -v

# Test error handling
python -m pytest tests/test_edge_cases.py::TestErrorHandling -v
```

## Test Coverage

The test suite achieves **100% code coverage** on the FastAPI backend (`src/app.py`).

Coverage reports are generated in:
- Terminal output (with `--cov-report=term-missing`)
- HTML report in `htmlcov/` directory (with `--cov-report=html`)

## Test Categories

### 1. API Endpoint Tests (`test_api.py`)

**Root Endpoint**
- Verifies redirection to static index page

**Activities Endpoint**
- Tests activity data retrieval
- Validates response format and structure
- Ensures all activities are returned

**Signup Endpoint**  
- Successful registration scenarios
- Duplicate registration prevention
- Non-existent activity handling
- URL encoding support

**Unregister Endpoint**
- Successful unregistration
- Non-registered participant handling
- Non-existent activity handling
- URL encoding support

**Integration Scenarios**
- Complete signup → unregister workflows
- Multiple activity registrations
- Capacity management verification

### 2. Edge Cases & Error Handling (`test_edge_cases.py`)

**Error Handling**
- Invalid email format handling
- Long input validation
- Special character support
- Case sensitivity verification
- Missing parameter validation

**Concurrency & Race Conditions**
- Simultaneous registration handling
- Rapid signup/unregister sequences

**Data Integrity**
- Activity metadata immutability
- Participant list uniqueness
- Empty state handling

**Response Format**
- Consistent success response structure
- Consistent error response structure
- Data type validation

### 3. Frontend Integration (`test_static_files.py`)

**Static File Serving**
- HTML, CSS, JS accessibility
- Proper content-type headers
- 404 handling for missing files

**Content Validation**
- Required HTML elements presence
- JavaScript function verification
- CSS class definitions
- Asset linking verification

**Frontend-Backend Integration**
- API endpoint compatibility
- Data structure alignment
- Error format compatibility

## Test Fixtures

### `client` 
FastAPI test client for making HTTP requests

### `reset_activities`
Resets activity data to initial state before/after each test

### `sample_activity` / `empty_activity`
Provides test activity data structures

## Test Configuration

**`pytest.ini`**
- Sets test discovery patterns
- Configures output verbosity
- Filters deprecation warnings
- Sets Python path for imports

## Continuous Integration

The tests are designed to be easily integrated into CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run tests
  run: |
    pip install -r requirements.txt
    python -m pytest tests/ --cov=src --cov-report=xml
    
- name: Upload coverage
  uses: codecov/codecov-action@v1
```

## Best Practices

1. **Test Isolation** - Each test is independent and can run in any order
2. **Data Reset** - Activity data is reset before each test
3. **Comprehensive Coverage** - Tests cover happy path, edge cases, and error conditions
4. **Real API Testing** - Uses FastAPI TestClient for authentic request/response testing
5. **Clear Documentation** - Test names and docstrings clearly describe test purposes

## Adding New Tests

When adding new functionality:

1. Add API endpoint tests to `test_api.py`
2. Add edge case tests to `test_edge_cases.py` 
3. Add frontend integration tests to `test_static_files.py` if UI changes are involved
4. Update fixtures in `conftest.py` if new test data is needed
5. Run full test suite to ensure no regressions