#!/usr/bin/env python3
"""
Comprehensive Test Runner for DeFi Risk Assessment Project

This script provides a complete test suite runner with coverage analysis,
performance testing, and validation for all service layers.

Usage:
    python run_tests.py [options]

Options:
    --unit          Run only unit tests
    --integration   Run only integration tests
    --coverage      Run with coverage analysis
    --performance   Run performance tests
    --all           Run all tests (default)
    --verbose       Verbose output
    --parallel      Run tests in parallel
    --fail-fast     Stop on first failure
"""

import os
import sys
import argparse
import subprocess
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
import json


class TestRunner:
    """Comprehensive test runner for the DeFi Risk Assessment project."""
    
    def __init__(self, project_root: str = None):
        """Initialize test runner.
        
        Args:
            project_root: Root directory of the project
        """
        self.project_root = project_root or os.getcwd()
        self.backend_path = os.path.join(self.project_root, "backend")
        self.tests_path = os.path.join(self.backend_path, "tests")
        
        # Ensure we're in the right directory
        if not os.path.exists(self.tests_path):
            raise FileNotFoundError(f"Tests directory not found: {self.tests_path}")
    
    def run_unit_tests(self, verbose: bool = False, parallel: bool = False) -> Dict[str, Any]:
        """Run unit tests.
        
        Args:
            verbose: Enable verbose output
            parallel: Run tests in parallel
            
        Returns:
            Test results
        """
        print("🧪 Running Unit Tests...")
        
        cmd = [
            sys.executable, "-m", "pytest",
            os.path.join(self.tests_path, "test_core_services.py"),
            os.path.join(self.tests_path, "test_ml_services.py"),
            os.path.join(self.tests_path, "test_rag_services.py"),
            os.path.join(self.tests_path, "test_data_providers.py"),
            "-m", "unit",
            "--tb=short"
        ]
        
        if verbose:
            cmd.append("-v")
        
        if parallel:
            cmd.extend(["-n", "auto"])
        
        return self._run_command(cmd, "Unit Tests")
    
    def run_integration_tests(self, verbose: bool = False) -> Dict[str, Any]:
        """Run integration tests.
        
        Args:
            verbose: Enable verbose output
            
        Returns:
            Test results
        """
        print("🔗 Running Integration Tests...")
        
        cmd = [
            sys.executable, "-m", "pytest",
            os.path.join(self.tests_path, "test_api_validation.py"),
            os.path.join(self.tests_path, "test_database_introspection.py"),
            "-m", "integration",
            "--tb=short"
        ]
        
        if verbose:
            cmd.append("-v")
        
        return self._run_command(cmd, "Integration Tests")
    
    def run_coverage_tests(self, verbose: bool = False) -> Dict[str, Any]:
        """Run tests with coverage analysis.
        
        Args:
            verbose: Enable verbose output
            
        Returns:
            Test results with coverage
        """
        print("📊 Running Tests with Coverage Analysis...")
        
        cmd = [
            sys.executable, "-m", "pytest",
            self.tests_path,
            "--cov=app",
            "--cov-report=term-missing",
            "--cov-report=html:htmlcov",
            "--cov-report=xml:coverage.xml",
            "--cov-fail-under=80",
            "--tb=short"
        ]
        
        if verbose:
            cmd.append("-v")
        
        return self._run_command(cmd, "Coverage Tests")
    
    def run_performance_tests(self, verbose: bool = False) -> Dict[str, Any]:
        """Run performance tests.
        
        Args:
            verbose: Enable verbose output
            
        Returns:
            Performance test results
        """
        print("⚡ Running Performance Tests...")
        
        cmd = [
            sys.executable, "-m", "pytest",
            self.tests_path,
            "-m", "slow",
            "--tb=short",
            "--durations=10"
        ]
        
        if verbose:
            cmd.append("-v")
        
        return self._run_command(cmd, "Performance Tests")
    
    def run_all_tests(self, verbose: bool = False, parallel: bool = False, fail_fast: bool = False) -> Dict[str, Any]:
        """Run all tests.
        
        Args:
            verbose: Enable verbose output
            parallel: Run tests in parallel
            fail_fast: Stop on first failure
            
        Returns:
            Complete test results
        """
        print("🚀 Running Complete Test Suite...")
        
        cmd = [
            sys.executable, "-m", "pytest",
            self.tests_path,
            "--cov=app",
            "--cov-report=term-missing",
            "--cov-report=html:htmlcov",
            "--cov-report=xml:coverage.xml",
            "--cov-fail-under=80",
            "--tb=short",
            "--maxfail=10",
            "--durations=10"
        ]
        
        if verbose:
            cmd.append("-v")
        
        if parallel:
            cmd.extend(["-n", "auto"])
        
        if fail_fast:
            cmd.append("--maxfail=1")
        
        return self._run_command(cmd, "Complete Test Suite")
    
    def run_specific_test(self, test_file: str, verbose: bool = False) -> Dict[str, Any]:
        """Run a specific test file.
        
        Args:
            test_file: Name of the test file
            verbose: Enable verbose output
            
        Returns:
            Test results
        """
        print(f"🎯 Running Specific Test: {test_file}")
        
        test_path = os.path.join(self.tests_path, test_file)
        if not os.path.exists(test_path):
            raise FileNotFoundError(f"Test file not found: {test_path}")
        
        cmd = [
            sys.executable, "-m", "pytest",
            test_path,
            "--tb=short"
        ]
        
        if verbose:
            cmd.append("-v")
        
        return self._run_command(cmd, f"Test: {test_file}")
    
    def run_test_by_marker(self, marker: str, verbose: bool = False) -> Dict[str, Any]:
        """Run tests by marker.
        
        Args:
            marker: Test marker (e.g., 'ml', 'rag', 'api')
            verbose: Enable verbose output
            
        Returns:
            Test results
        """
        print(f"🏷️ Running Tests with Marker: {marker}")
        
        cmd = [
            sys.executable, "-m", "pytest",
            self.tests_path,
            "-m", marker,
            "--tb=short"
        ]
        
        if verbose:
            cmd.append("-v")
        
        return self._run_command(cmd, f"Marker: {marker}")
    
    def _run_command(self, cmd: List[str], test_name: str) -> Dict[str, Any]:
        """Run a command and return results.
        
        Args:
            cmd: Command to run
            test_name: Name of the test for logging
            
        Returns:
            Command results
        """
        start_time = time.time()
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.backend_path,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            return {
                "test_name": test_name,
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "execution_time": execution_time,
                "command": " ".join(cmd)
            }
            
        except subprocess.TimeoutExpired:
            return {
                "test_name": test_name,
                "success": False,
                "returncode": -1,
                "stdout": "",
                "stderr": "Test execution timed out",
                "execution_time": 300,
                "command": " ".join(cmd)
            }
        except Exception as e:
            return {
                "test_name": test_name,
                "success": False,
                "returncode": -1,
                "stdout": "",
                "stderr": str(e),
                "execution_time": time.time() - start_time,
                "command": " ".join(cmd)
            }
    
    def generate_test_report(self, results: List[Dict[str, Any]]) -> str:
        """Generate a comprehensive test report.
        
        Args:
            results: List of test results
            
        Returns:
            Formatted test report
        """
        report = []
        report.append("📋 COMPREHENSIVE TEST REPORT")
        report.append("=" * 50)
        
        # Summary
        total_tests = len(results)
        successful_tests = sum(1 for r in results if r["success"])
        failed_tests = total_tests - successful_tests
        total_time = sum(r["execution_time"] for r in results)
        
        report.append(f"📊 Summary:")
        report.append(f"   Total Test Suites: {total_tests}")
        report.append(f"   ✅ Successful: {successful_tests}")
        report.append(f"   ❌ Failed: {failed_tests}")
        report.append(f"   ⏱️ Total Time: {total_time:.2f}s")
        report.append("")
        
        # Individual results
        report.append("📝 Individual Results:")
        for result in results:
            status = "✅" if result["success"] else "❌"
            report.append(f"   {status} {result['test_name']}: {result['execution_time']:.2f}s")
            
            if not result["success"] and result["stderr"]:
                report.append(f"      Error: {result['stderr'][:100]}...")
        
        report.append("")
        
        # Recommendations
        if failed_tests > 0:
            report.append("🔧 Recommendations:")
            report.append("   - Review failed test output above")
            report.append("   - Check test dependencies and setup")
            report.append("   - Verify database connections")
            report.append("   - Ensure all required services are running")
        
        return "\n".join(report)
    
    def save_test_results(self, results: List[Dict[str, Any]], filename: str = "test_results.json"):
        """Save test results to file.
        
        Args:
            results: Test results to save
            filename: Output filename
        """
        output_path = os.path.join(self.project_root, filename)
        
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"💾 Test results saved to: {output_path}")


def main():
    """Main entry point for the test runner."""
    parser = argparse.ArgumentParser(description="Comprehensive Test Runner for DeFi Risk Assessment")
    
    # Test type options
    parser.add_argument("--unit", action="store_true", help="Run only unit tests")
    parser.add_argument("--integration", action="store_true", help="Run only integration tests")
    parser.add_argument("--coverage", action="store_true", help="Run with coverage analysis")
    parser.add_argument("--performance", action="store_true", help="Run performance tests")
    parser.add_argument("--all", action="store_true", help="Run all tests (default)")
    
    # Test execution options
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--parallel", "-p", action="store_true", help="Run tests in parallel")
    parser.add_argument("--fail-fast", action="store_true", help="Stop on first failure")
    
    # Specific test options
    parser.add_argument("--test-file", help="Run specific test file")
    parser.add_argument("--marker", help="Run tests with specific marker")
    
    # Output options
    parser.add_argument("--save-results", action="store_true", help="Save results to file")
    parser.add_argument("--report-only", action="store_true", help="Generate report only")
    
    args = parser.parse_args()
    
    # Initialize test runner
    try:
        runner = TestRunner()
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    
    # Determine which tests to run
    results = []
    
    if args.test_file:
        # Run specific test file
        result = runner.run_specific_test(args.test_file, args.verbose)
        results.append(result)
    
    elif args.marker:
        # Run tests by marker
        result = runner.run_test_by_marker(args.marker, args.verbose)
        results.append(result)
    
    elif args.unit:
        # Run unit tests
        result = runner.run_unit_tests(args.verbose, args.parallel)
        results.append(result)
    
    elif args.integration:
        # Run integration tests
        result = runner.run_integration_tests(args.verbose)
        results.append(result)
    
    elif args.coverage:
        # Run coverage tests
        result = runner.run_coverage_tests(args.verbose)
        results.append(result)
    
    elif args.performance:
        # Run performance tests
        result = runner.run_performance_tests(args.verbose)
        results.append(result)
    
    else:
        # Run all tests (default)
        result = runner.run_all_tests(args.verbose, args.parallel, args.fail_fast)
        results.append(result)
    
    # Generate and display report
    if not args.report_only:
        report = runner.generate_test_report(results)
        print("\n" + report)
    
    # Save results if requested
    if args.save_results:
        runner.save_test_results(results)
    
    # Exit with appropriate code
    all_successful = all(r["success"] for r in results)
    sys.exit(0 if all_successful else 1)


if __name__ == "__main__":
    main()

