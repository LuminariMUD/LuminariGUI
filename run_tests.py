#!/usr/bin/env python3
"""
LuminariGUI Test Runner
Orchestrates all testing suites and provides unified reporting.
"""

import os
import sys
import subprocess
import json
import time
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

# Import test modules
try:
    from test_lua_syntax import LuaSyntaxTester
    from test_lua_quality import LuaQualityAnalyzer
    from test_functions import LuaFunctionTester
    from test_events import EventSystemTester
    from test_system import SystemTester
    from test_performance import PerformanceTester
except ImportError as e:
    print(f"Error importing test modules: {e}")
    sys.exit(1)

class TestRunner:
    def __init__(self, xml_file="LuminariGUI.xml"):
        self.xml_file = xml_file
        self.results = {}
        self.start_time = None
        self.end_time = None
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.errors = []
        self.warnings = []
        
    def _check_dependencies(self):
        """Check if required dependencies are available."""
        deps = {
            'lua': ['lua', 'lua5.1', 'lua5.2', 'lua5.3', 'lua5.4', 'luajit'],
            'luac': ['luac', 'luac5.1', 'luac5.2', 'luac5.3', 'luac5.4'],
            'luacheck': ['luacheck']
        }
        
        available = {}
        missing = []
        
        for dep_name, executables in deps.items():
            found = False
            for exe in executables:
                if self._find_executable(exe):
                    available[dep_name] = exe
                    found = True
                    break
            if not found:
                missing.append(dep_name)
        
        return available, missing
    
    def _find_executable(self, name):
        """Find executable in PATH."""
        for path in os.environ["PATH"].split(os.pathsep):
            full_path = os.path.join(path, name)
            if os.path.isfile(full_path) and os.access(full_path, os.X_OK):
                return full_path
        return None
    
    def _run_test_suite(self, test_name, test_class, args=None):
        """Run a single test suite."""
        print(f"Running {test_name}...")
        
        try:
            # Create test instance
            if args:
                tester = test_class(self.xml_file, **args)
            else:
                tester = test_class(self.xml_file)
            
            # Run appropriate test method
            if hasattr(tester, 'run_tests'):
                success = tester.run_tests()
            elif hasattr(tester, 'run_analysis'):
                success = tester.run_analysis()
            elif hasattr(tester, 'run_benchmarks'):
                success = tester.run_benchmarks()
            else:
                raise Exception(f"No run method found for {test_name}")
            
            # Get results
            results = tester.get_results()
            
            return {
                'name': test_name,
                'success': success,
                'results': results,
                'errors': getattr(tester, 'errors', []),
                'warnings': getattr(tester, 'warnings', [])
            }
            
        except Exception as e:
            return {
                'name': test_name,
                'success': False,
                'results': {},
                'errors': [str(e)],
                'warnings': []
            }
    
    def run_all_tests(self, parallel=True, skip_optional=False):
        """Run all test suites."""
        print("LuminariGUI Test Runner")
        print("=" * 50)
        
        # Check dependencies
        available, missing = self._check_dependencies()
        
        if missing:
            print(f"Missing dependencies: {', '.join(missing)}")
            if not skip_optional:
                print("Install missing dependencies or use --skip-optional")
                return False
        
        print(f"Available tools: {', '.join(available.keys())}")
        
        # Check if XML file exists
        if not os.path.exists(self.xml_file):
            print(f"Error: XML file not found: {self.xml_file}")
            return False
        
        print(f"Testing XML file: {self.xml_file}")
        print("")
        
        # Define test suites
        test_suites = [
            ('Lua Syntax', LuaSyntaxTester),
            ('Lua Quality', LuaQualityAnalyzer),
            ('Function Tests', LuaFunctionTester),
            ('Event System', EventSystemTester),
            ('System Tests', SystemTester),
            ('Performance', PerformanceTester)
        ]
        
        # Filter based on available dependencies
        filtered_suites = []
        for name, test_class in test_suites:
            if name == 'Lua Syntax' and 'luac' not in available:
                if not skip_optional:
                    print(f"Skipping {name} (luac not available)")
                continue
            elif name == 'Lua Quality' and 'luacheck' not in available:
                if not skip_optional:
                    print(f"Skipping {name} (luacheck not available)")
                continue
            elif 'lua' not in available:
                if not skip_optional:
                    print(f"Skipping {name} (lua not available)")
                continue
            
            filtered_suites.append((name, test_class))
        
        if not filtered_suites:
            print("No test suites available to run")
            return False
        
        self.start_time = time.time()
        
        # Run tests
        if parallel and len(filtered_suites) > 1:
            self._run_parallel_tests(filtered_suites)
        else:
            self._run_sequential_tests(filtered_suites)
        
        self.end_time = time.time()
        
        # Generate summary
        self._generate_summary()
        
        return self.failed_tests == 0
    
    def _run_sequential_tests(self, test_suites):
        """Run tests sequentially."""
        for test_name, test_class in test_suites:
            result = self._run_test_suite(test_name, test_class)
            self.results[test_name] = result
            
            if result['success']:
                self.passed_tests += 1
            else:
                self.failed_tests += 1
            
            self.total_tests += 1
            self.errors.extend(result['errors'])
            self.warnings.extend(result['warnings'])
    
    def _run_parallel_tests(self, test_suites):
        """Run tests in parallel."""
        print("Running tests in parallel...")
        
        with ThreadPoolExecutor(max_workers=4) as executor:
            # Submit all test jobs
            future_to_test = {
                executor.submit(self._run_test_suite, test_name, test_class): test_name
                for test_name, test_class in test_suites
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_test):
                test_name = future_to_test[future]
                try:
                    result = future.result()
                    self.results[test_name] = result
                    
                    if result['success']:
                        self.passed_tests += 1
                        print(f"✓ {test_name} completed successfully")
                    else:
                        self.failed_tests += 1
                        print(f"✗ {test_name} failed")
                    
                    self.total_tests += 1
                    self.errors.extend(result['errors'])
                    self.warnings.extend(result['warnings'])
                    
                except Exception as e:
                    print(f"✗ {test_name} crashed: {e}")
                    self.failed_tests += 1
                    self.total_tests += 1
                    self.errors.append(f"{test_name}: {str(e)}")
    
    def _generate_summary(self):
        """Generate test summary."""
        duration = self.end_time - self.start_time
        
        print("\n" + "=" * 50)
        print("TEST SUMMARY")
        print("=" * 50)
        print(f"Total test suites: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.failed_tests}")
        print(f"Duration: {duration:.2f} seconds")
        print("")
        
        # Per-suite results
        for test_name, result in self.results.items():
            status = "PASS" if result['success'] else "FAIL"
            print(f"{test_name}: {status}")
            
            # Show specific metrics if available
            if 'results' in result:
                results = result['results']
                if 'total_issues' in results:
                    print(f"  Issues: {results['total_issues']}")
                if 'benchmark_results' in results:
                    print(f"  Benchmarks: {len(results['benchmark_results'])}")
        
        # Errors and warnings
        if self.errors:
            print(f"\nErrors ({len(self.errors)}):")
            for error in self.errors[:10]:  # Show first 10
                print(f"  {error}")
            if len(self.errors) > 10:
                print(f"  ... and {len(self.errors) - 10} more")
        
        if self.warnings:
            print(f"\nWarnings ({len(self.warnings)}):")
            for warning in self.warnings[:5]:  # Show first 5
                print(f"  {warning}")
            if len(self.warnings) > 5:
                print(f"  ... and {len(self.warnings) - 5} more")
        
        # Overall result
        print("\n" + "=" * 50)
        if self.failed_tests == 0:
            print("ALL TESTS PASSED ✓")
        else:
            print(f"TESTS FAILED ({self.failed_tests}/{self.total_tests}) ✗")
        print("=" * 50)
    
    def generate_report(self, format='text', output_file=None):
        """Generate detailed test report."""
        if format == 'json':
            report = {
                'summary': {
                    'total_tests': self.total_tests,
                    'passed_tests': self.passed_tests,
                    'failed_tests': self.failed_tests,
                    'duration': self.end_time - self.start_time if self.end_time else 0,
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                },
                'results': self.results,
                'errors': self.errors,
                'warnings': self.warnings
            }
            
            report_text = json.dumps(report, indent=2)
        else:
            # Text format
            report_lines = [
                "LuminariGUI Test Report",
                "=" * 50,
                f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}",
                f"XML File: {self.xml_file}",
                "",
                "SUMMARY",
                "-" * 20,
                f"Total test suites: {self.total_tests}",
                f"Passed: {self.passed_tests}",
                f"Failed: {self.failed_tests}",
                f"Duration: {self.end_time - self.start_time:.2f} seconds" if self.end_time else "Duration: N/A",
                ""
            ]
            
            # Detailed results
            for test_name, result in self.results.items():
                report_lines.extend([
                    f"{test_name.upper()}",
                    "-" * len(test_name),
                    f"Status: {'PASS' if result['success'] else 'FAIL'}",
                    f"Errors: {len(result['errors'])}",
                    f"Warnings: {len(result['warnings'])}",
                    ""
                ])
                
                if result['errors']:
                    report_lines.append("Errors:")
                    for error in result['errors']:
                        report_lines.append(f"  {error}")
                    report_lines.append("")
                
                if result['warnings']:
                    report_lines.append("Warnings:")
                    for warning in result['warnings']:
                        report_lines.append(f"  {warning}")
                    report_lines.append("")
            
            report_text = '\n'.join(report_lines)
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(report_text)
            print(f"Report saved to: {output_file}")
        else:
            print(report_text)
    
    def run_single_test(self, test_name):
        """Run a single test suite."""
        test_map = {
            'syntax': ('Lua Syntax', LuaSyntaxTester),
            'quality': ('Lua Quality', LuaQualityAnalyzer),
            'functions': ('Function Tests', LuaFunctionTester),
            'events': ('Event System', EventSystemTester),
            'system': ('System Tests', SystemTester),
            'performance': ('Performance', PerformanceTester)
        }
        
        if test_name not in test_map:
            print(f"Unknown test: {test_name}")
            print(f"Available tests: {', '.join(test_map.keys())}")
            return False
        
        name, test_class = test_map[test_name]
        
        self.start_time = time.time()
        result = self._run_test_suite(name, test_class)
        self.end_time = time.time()
        
        self.results[name] = result
        self.total_tests = 1
        
        if result['success']:
            self.passed_tests = 1
            self.failed_tests = 0
        else:
            self.passed_tests = 0
            self.failed_tests = 1
        
        self.errors = result['errors']
        self.warnings = result['warnings']
        
        self._generate_summary()
        
        return result['success']

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Run LuminariGUI tests')
    parser.add_argument('--xml', default='LuminariGUI.xml', help='XML file to test')
    parser.add_argument('--parallel', action='store_true', help='Run tests in parallel')
    parser.add_argument('--sequential', action='store_true', help='Run tests sequentially')
    parser.add_argument('--skip-optional', action='store_true', help='Skip tests with missing dependencies')
    parser.add_argument('--test', help='Run specific test suite (syntax, quality, functions, events, system, performance)')
    parser.add_argument('--report', help='Generate report file')
    parser.add_argument('--format', choices=['text', 'json'], default='text', help='Report format')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--quiet', '-q', action='store_true', help='Quiet mode')
    
    args = parser.parse_args()
    
    # Create test runner
    runner = TestRunner(args.xml)
    
    # Run tests
    if args.test:
        success = runner.run_single_test(args.test)
    else:
        parallel = args.parallel or (not args.sequential)
        success = runner.run_all_tests(parallel=parallel, skip_optional=args.skip_optional)
    
    # Generate report if requested
    if args.report:
        runner.generate_report(format=args.format, output_file=args.report)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()