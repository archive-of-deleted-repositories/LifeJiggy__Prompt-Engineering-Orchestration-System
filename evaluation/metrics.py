"""Metrics collection module."""


class MetricsCollector:
    """Collects and reports metrics."""
    
    def __init__(self, config: dict = None):
        """Initialize the metrics collector.
        
        Args:
            config: Configuration.
        """
        self.config = config or {}
        self._metrics = {}
    
    def record(self, metric_name: str, value: float, labels: dict = None) -> None:
        """Record a metric.
        
        Args:
            metric_name: Name of the metric.
            value: Metric value.
            labels: Optional labels.
        """
        if metric_name not in self._metrics:
            self._metrics[metric_name] = []
        self._metrics[metric_name].append({"value": value, "labels": labels or {}})
    
    def get_metric(self, metric_name: str) -> list[dict]:
        """Get metric values.
        
        Args:
            metric_name: Name of the metric.
            
        Returns:
            List of metric values.
        """
        return self._metrics.get(metric_name, [])
    
    def get_all_metrics(self) -> dict:
        """Get all metrics.
        
        Returns:
            All metrics dictionary.
        """
        return self._metrics.copy()
    
    def reset(self) -> None:
        """Reset all metrics."""
        self._metrics = {}
