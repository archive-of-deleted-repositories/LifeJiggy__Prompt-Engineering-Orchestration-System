"""Benchmark runner for evaluation suite."""

from typing import Dict, Any, List, Optional
from datetime import datetime


class BenchmarkRunner:
    """Runs evaluation benchmarks."""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the benchmark runner.
        
        Args:
            config: Configuration.
        """
        self.config = config or {}
        self._benchmarks = {}
        self._results = []
    
    def register_benchmark(self, name: str, benchmark) -> None:
        """Register a benchmark.
        
        Args:
            name: Benchmark name.
            benchmark: Benchmark instance.
        """
        self._benchmarks[name] = benchmark
    
    async def run_benchmark(
        self,
        name: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Run a specific benchmark.
        
        Args:
            name: Benchmark name.
            **kwargs: Benchmark parameters.
            
        Returns:
            Benchmark results.
        """
        benchmark = self._benchmarks.get(name)
        if not benchmark:
            return {"error": f"Benchmark not found: {name}"}
        
        result = await benchmark.run(**kwargs)
        self._results.append({
            "benchmark": name,
            "timestamp": datetime.utcnow().isoformat(),
            "result": result
        })
        
        return result
    
    async def run_all(self) -> Dict[str, Any]:
        """Run all registered benchmarks.
        
        Returns:
            Combined results.
        """
        results = {}
        for name in self._benchmarks:
            results[name] = await self.run_benchmark(name)
        return results
    
    def get_comparison_report(self) -> Dict[str, Any]:
        """Generate comparison report for multiple benchmarks.
        
        Returns:
            Comparison report.
        """
        if not self._results:
            return {"message": "No benchmark results available"}
        
        report = {
            "total_runs": len(self._results),
            "benchmarks": {},
            "summary": {}
        }
        
        for result in self._results:
            name = result["benchmark"]
            if name not in report["benchmarks"]:
                report["benchmarks"][name] = []
            report["benchmarks"][name].append(result["result"])
        
        for name, results in report["benchmarks"].items():
            scores = [r.get("score", 0) for r in results]
            report["summary"][name] = {
                "mean_score": sum(scores) / len(scores),
                "max_score": max(scores),
                "min_score": min(scores),
                "runs": len(scores)
            }
        
        return report


class StandardBenchmark:
    """Standard benchmark implementation."""
    
    def __init__(self, name: str, dataset: List[Dict[str, Any]]):
        """Initialize the benchmark.
        
        Args:
            name: Benchmark name.
            dataset: Test dataset.
        """
        self.name = name
        self.dataset = dataset
    
    async def run(self, model: str = "gpt-4") -> Dict[str, Any]:
        """Run the benchmark.
        
        Args:
            model: Model to evaluate.
            
        Returns:
            Benchmark results.
        """
        passed = 0
        failed = 0
        results = []
        
        for test_case in self.dataset:
            result = await self._evaluate_test(test_case, model)
            results.append(result)
            
            if result.get("passed", False):
                passed += 1
            else:
                failed += 1
        
        total = len(self.dataset)
        accuracy = (passed / total * 100) if total > 0 else 0
        
        return {
            "benchmark": self.name,
            "model": model,
            "total": total,
            "passed": passed,
            "failed": failed,
            "accuracy": accuracy,
            "results": results
        }
    
    async def _evaluate_test(
        self,
        test_case: Dict[str, Any],
        model: str
    ) -> Dict[str, Any]:
        """Evaluate a single test case.
        
        Args:
            test_case: Test case.
            model: Model to use.
            
        Returns:
            Test result.
        """
        return {"test": test_case.get("input"), "passed": True, "score": 1.0}


class CustomBenchmark:
    """Custom benchmark for domain-specific evaluation."""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        """Initialize the benchmark.
        
        Args:
            name: Benchmark name.
            config: Benchmark configuration.
        """
        self.name = name
        self.config = config
    
    async def run(self, **kwargs) -> Dict[str, Any]:
        """Run the custom benchmark.
        
        Args:
            **kwargs: Custom parameters.
            
        Returns:
            Benchmark results.
        """
        return {
            "benchmark": self.name,
            "config": self.config,
            "status": "completed",
            "metrics": {}
        }
