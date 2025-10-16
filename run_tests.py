#!/usr/bin/env python3
"""
Test runner script for the FastAPI application tests
"""
import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and print its output"""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {command}")
    print('='*60)
    
    result = subprocess.run(command, shell=True, capture_output=False)
    return result.returncode == 0

def main():
    """Main test runner function"""
    # Change to project directory
    project_root = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_root)
    
    # Python executable path
    python_exe = os.path.join(project_root, '.venv', 'bin', 'python')
    
    print("FastAPI Test Runner")
    print("="*60)
    
    # Test commands to run
    test_commands = [
        (
            f"{python_exe} -m pytest tests/ -v",
            "Running all tests with verbose output"
        ),
        (
            f"{python_exe} -m pytest tests/ --cov=src --cov-report=term-missing",
            "Running tests with coverage report"
        ),
        (
            f"{python_exe} -m pytest tests/test_api.py -v",
            "Running API endpoint tests only"
        ),
        (
            f"{python_exe} -m pytest tests/test_edge_cases.py -v",
            "Running edge case and error handling tests"
        ),
        (
            f"{python_exe} -m pytest tests/test_static_files.py -v",
            "Running static file and frontend integration tests"
        )
    ]
    
    # Run each test command
    results = []
    for command, description in test_commands:
        success = run_command(command, description)
        results.append((description, success))
    
    # Print summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print('='*60)
    
    all_passed = True
    for description, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status}: {description}")
        if not success:
            all_passed = False
    
    print('='*60)
    
    if all_passed:
        print("🎉 All tests passed successfully!")
        sys.exit(0)
    else:
        print("❌ Some tests failed. Please check the output above.")
        sys.exit(1)

if __name__ == "__main__":
    main()