"""Performance tracking for monitoring."""

from typing import Dict, Any, List
from datetime import datetime, timedelta
from collections import defaultdict


class PerformanceTracker:
    """Tracks system performance metrics."""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the tracker.
        
        Args:
            config: Configuration.
        """
        self.config = config or {}
        self._metrics = defaultdict(list)
        self._start_time = datetime.utcnow()
    
    def record_latency(self, operation: str, duration_ms: float) -> None:
        """Record operation latency.
        
        Args:
            operation: Operation name.
            duration_ms: Duration in milliseconds.
        """
        self._metrics[f"latency_{operation}"].append({
            "timestamp": datetime.utcnow().isoformat(),
            "duration_ms": duration_ms
        })
    
    def record_request(self, endpoint: str, status: int, duration_ms: float) -> None:
        """Record HTTP request.
        
        Args:
            endpoint: API endpoint.
            status: Response status code.
            duration_ms: Request duration.
        """
        self._metrics["requests"].append({
            "timestamp": datetime.utcnow().isoformat(),
            "endpoint": endpoint,
            "status": status,
            "duration_ms": duration_ms
        })
    
    def record_error(self, error_type: str, message: str) -> None:
        """Record an error.
        
        Args:
            error_type: Type of error.
            message: Error message.
        """
        self._metrics["errors"].append({
            "timestamp": datetime.utcnow().isoformat(),
            "type": error_type,
            "message": message
        })
    
    def get_latency_stats(self, operation: str = None) -> Dict[str, Any]:
        """Get latency statistics.
        
        Args:
            operation: Specific operation or None for all.
            
        Returns:
            Latency statistics.
        """
        if operation:
            key = f"latency_{operation}"
            latencies = [m["duration_ms"] for m in self._metrics[key]]
        else:
            latencies = []
            for key in self._metrics:
                if key.startswith("latency_"):
                    latencies.extend(m["duration_ms"] for m in self._metrics[key])
        
        if not latencies:
            return {"count": 0, "mean_ms": 0, "p50_ms": 0, "p95_ms": 0, "p99_ms": 0}
        
        latencies.sort()
        n = len(latencies)
        
        return {
            "count": n,
            "mean_ms": sum(latencies) / n,
            "min_ms": latencies[0],
            "max_ms": latencies[-1],
            "p50_ms": latencies[n // 2],
            "p95_ms": latencies[int(n * 0.95)],
            "p99_ms": latencies[int(n * 0.99)]
        }
    
    def get_request_stats(self) -> Dict[str, Any]:
        """Get request statistics.
        
        Returns:
            Request statistics.
        """
        requests = self._metrics.get("requests", [])
        
        if not requests:
            return {"total": 0, "by_status": {}}
        
        by_status = defaultdict(int)
        for req in requests:
            by_status[req["status"]] += 1
        
        return {
            "total": len(requests),
            "by_status": dict(by_status),
            "success_rate": by_status.get(200, 0) / len(requests) * 100
        }
    
    def get_error_stats(self) -> Dict[str, Any]:
        """Get error statistics.
        
        Returns:
            Error statistics.
        """
        errors = self._metrics.get("errors", [])
        
        if not errors:
            return {"count": 0, "by_type": {}}
        
        by_type = defaultdict(int)
        for err in errors:
            by_type[err["type"]] += 1
        
        return {
            "count": len(errors),
            "by_type": dict(by_type)
        }
    
    def get_summary(self) -> Dict[str, Any]:
        """Get complete performance summary.
        
        Returns:
            Performance summary.
        """
        uptime = (datetime.utcnow() - self._start_time).total_seconds()
        
        return {
            "uptime_seconds": uptime,
            "latency": self.get_latency_stats(),
            "requests": self.get_request_stats(),
            "errors": self.get_error_stats()
        }
    
    def reset(self) -> None:
        """Reset all metrics."""
        self._metrics.clear()
        self._start_time = datetime.utcnow()


class CostTracker:
    """Tracks API costs."""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the tracker.
        
        Args:
            config: Configuration.
        """
        self.config = config or {}
        self._costs = []
        self._budget_limit = config.get("budget_limit", 100.0) if config else 100.0
    
    def record_cost(
        self,
        provider: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        cost: float
    ) -> None:
        """Record API cost.
        
        Args:
            provider: Model provider.
            model: Model name.
            input_tokens: Input tokens used.
            output_tokens: Output tokens generated.
            cost: Cost in USD.
        """
        self._costs.append({
            "timestamp": datetime.utcnow().isoformat(),
            "provider": provider,
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost": cost
        })
    
    def get_total_cost(self) -> float:
        """Get total cost.
        
        Returns:
            Total cost in USD.
        """
        return sum(c["cost"] for c in self._costs)
    
    def get_cost_by_provider(self) -> Dict[str, float]:
        """Get cost breakdown by provider.
        
        Returns:
            Cost by provider.
        """
        by_provider = defaultdict(float)
        for cost in self._costs:
            by_provider[cost["provider"]] += cost["cost"]
        return dict(by_provider)
    
    def get_budget_status(self) -> Dict[str, Any]:
        """Get budget status.
        
        Returns:
            Budget status.
        """
        total = self.get_total_cost()
        remaining = self._budget_limit - total
        percentage = (total / self._budget_limit) * 100 if self._budget_limit > 0 else 0
        
        return {
            "total_cost": total,
            "budget_limit": self._budget_limit,
            "remaining": remaining,
            "percentage_used": percentage,
            "is_over_budget": total > self._budget_limit
        }
    
    def get_token_summary(self) -> Dict[str, int]:
        """Get token usage summary.
        
        Returns:
            Token counts.
        """
        total_input = sum(c["input_tokens"] for c in self._costs)
        total_output = sum(c["output_tokens"] for c in self._costs)
        
        return {
            "total_input_tokens": total_input,
            "total_output_tokens": total_output,
            "total_tokens": total_input + total_output
        }
