# Performance Metrics Database - Usage Guide

## Overview

The `performance_metrics.db` file stores performance data collected by the ToTh (Theorem-of-Thought) optimization system. This guide shows you how to view and utilize this data.

## Quick Start

### View Summary Statistics

```bash
# View last 24 hours (default)
python3 ops/scripts/view_performance_metrics.py --summary

# View last 7 days
python3 ops/scripts/view_performance_metrics.py --summary --hours 168

# View all available data
python3 ops/scripts/view_performance_metrics.py --all
```

### View Statistics by Reasoning Mode

```bash
python3 ops/scripts/view_performance_metrics.py --by-mode
```

### View Recent Records

```bash
# Show last 10 records
python3 ops/scripts/view_performance_metrics.py --recent 10

# Show last 50 records
python3 ops/scripts/view_performance_metrics.py --recent 50
```

### View Performance Trends

```bash
# Show hourly trends for last 24 hours
python3 ops/scripts/view_performance_metrics.py --trends --hours 24
```

### Export Data

```bash
# Export to JSON file
python3 ops/scripts/view_performance_metrics.py --export metrics.json

# Export last 7 days
python3 ops/scripts/view_performance_metrics.py --export weekly_metrics.json --hours 168
```

## Using Python Directly

You can also use the `PerformanceMonitor` class directly in your code:

```python
from toth_integration.optimization import PerformanceMonitor

# Initialize monitor
monitor = PerformanceMonitor("performance_metrics.db")

# Get summary for last 24 hours
summary = monitor.get_performance_summary(hours=24)
print(f"Total requests: {summary['total_requests']}")
print(f"Avg execution time: {summary['avg_execution_time']}s")
print(f"Cache hit rate: {summary['cache_hit_rate']:.1f}%")
print(f"Error rate: {summary['error_rate']:.1f}%")
```

## Using SQLite Directly

You can also query the database directly using SQLite:

```bash
# Open database
sqlite3 performance_metrics.db

# View all tables
.tables

# View schema
.schema performance_metrics

# Get total record count
SELECT COUNT(*) FROM performance_metrics;

# Get recent records
SELECT * FROM performance_metrics ORDER BY timestamp DESC LIMIT 10;

# Get average execution time by reasoning mode
SELECT reasoning_mode, AVG(execution_time), COUNT(*) 
FROM performance_metrics 
GROUP BY reasoning_mode;

# Get cache hit rate
SELECT 
    SUM(CASE WHEN cache_hit THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as cache_hit_rate
FROM performance_metrics;
```

## Data Fields

The database stores the following metrics:

- **timestamp** - When the operation occurred
- **query_hash** - Unique identifier for the query
- **reasoning_mode** - Which reasoning mode was used
- **execution_time** - How long the operation took (seconds)
- **confidence** - Confidence score (0.0 to 1.0)
- **cache_hit** - Whether result came from cache (boolean)
- **optimization_applied** - Whether optimizations were used (boolean)
- **batch_processed** - Whether processed in batch (boolean)
- **error_occurred** - Whether an error happened (boolean)
- **memory_usage_mb** - Memory consumption (MB)
- **cpu_usage_percent** - CPU usage percentage

## Common Use Cases

### 1. Monitor System Performance

```bash
# Check overall health
python3 ops/scripts/view_performance_metrics.py --summary --hours 1
```

### 2. Identify Slow Operations

```bash
# Find slowest operations
sqlite3 performance_metrics.db "SELECT * FROM performance_metrics ORDER BY execution_time DESC LIMIT 10;"
```

### 3. Track Error Rates

```bash
# Check error rate
python3 ops/scripts/view_performance_metrics.py --summary | grep "Error Rate"
```

### 4. Analyze Cache Effectiveness

```bash
# View cache hit rate
python3 ops/scripts/view_performance_metrics.py --summary | grep "Cache Hit"
```

### 5. Compare Reasoning Modes

```bash
# See which modes are fastest/most reliable
python3 ops/scripts/view_performance_metrics.py --by-mode
```

## Integration with Monitoring

The performance data can be integrated with monitoring systems:

```python
from ops.scripts.view_performance_metrics import PerformanceMetricsViewer

viewer = PerformanceMetricsViewer()
summary = viewer.get_summary(24)

# Send to monitoring system
if summary['error_rate'] > 5.0:
    alert("High error rate detected!")
    
if summary['avg_execution_time'] > 10.0:
    alert("Slow performance detected!")
```

## File Location

- **Database**: `performance_metrics.db` (root of workspace)
- **Viewer Script**: `ops/scripts/view_performance_metrics.py`
- **Source Code**: `toth_integration/optimization.py` (PerformanceMonitor class)

## Notes

- The database is automatically created when `PerformanceMonitor` is first used
- Data accumulates over time - consider archiving old data periodically
- The database is listed in `.gitignore` and should not be committed to version control

