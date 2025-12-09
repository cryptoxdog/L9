#!/usr/bin/env python3
"""
Performance Metrics Viewer
View and analyze data from performance_metrics.db
"""

import sqlite3
import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import argparse

class PerformanceMetricsViewer:
    """View and analyze performance metrics from database"""
    
    def __init__(self, db_path: str = "performance_metrics.db"):
        self.db_path = Path(db_path)
        if not self.db_path.exists():
            print(f"❌ Database not found: {self.db_path}")
            print(f"   Expected location: {self.db_path.absolute()}")
            sys.exit(1)
    
    def get_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get performance summary for specified period"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        cursor.execute('''
            SELECT 
                COUNT(*) as total_requests,
                AVG(execution_time) as avg_execution_time,
                MIN(execution_time) as min_execution_time,
                MAX(execution_time) as max_execution_time,
                AVG(confidence) as avg_confidence,
                SUM(CASE WHEN cache_hit THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as cache_hit_rate,
                SUM(CASE WHEN error_occurred THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as error_rate,
                SUM(CASE WHEN optimization_applied THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as optimization_rate,
                AVG(memory_usage_mb) as avg_memory_usage,
                AVG(cpu_usage_percent) as avg_cpu_usage
            FROM performance_metrics
            WHERE timestamp >= ?
        ''', (cutoff_time,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result and result['total_requests'] > 0:
            return {
                'total_requests': result['total_requests'],
                'avg_execution_time': round(result['avg_execution_time'] or 0, 3),
                'min_execution_time': round(result['min_execution_time'] or 0, 3),
                'max_execution_time': round(result['max_execution_time'] or 0, 3),
                'avg_confidence': round(result['avg_confidence'] or 0, 3),
                'cache_hit_rate': round(result['cache_hit_rate'] or 0, 2),
                'error_rate': round(result['error_rate'] or 0, 2),
                'optimization_rate': round(result['optimization_rate'] or 0, 2),
                'avg_memory_usage_mb': round(result['avg_memory_usage'] or 0, 2),
                'avg_cpu_usage_percent': round(result['avg_cpu_usage'] or 0, 2),
                'period_hours': hours
            }
        
        return {
            'total_requests': 0,
            'period_hours': hours,
            'message': 'No data available for specified period'
        }
    
    def get_recent_records(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most recent records"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM performance_metrics
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_by_reasoning_mode(self, hours: int = 24) -> Dict[str, Dict[str, Any]]:
        """Get statistics grouped by reasoning mode"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        cursor.execute('''
            SELECT 
                reasoning_mode,
                COUNT(*) as count,
                AVG(execution_time) as avg_time,
                AVG(confidence) as avg_confidence,
                SUM(CASE WHEN error_occurred THEN 1 ELSE 0 END) as errors
            FROM performance_metrics
            WHERE timestamp >= ?
            GROUP BY reasoning_mode
            ORDER BY count DESC
        ''', (cutoff_time,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return {
            row['reasoning_mode'] or 'unknown': {
                'count': row['count'],
                'avg_execution_time': round(row['avg_time'] or 0, 3),
                'avg_confidence': round(row['avg_confidence'] or 0, 3),
                'errors': row['errors'],
                'error_rate': round((row['errors'] / row['count']) * 100, 2) if row['count'] > 0 else 0
            }
            for row in rows
        }
    
    def get_trends(self, hours: int = 24, interval_hours: int = 1) -> List[Dict[str, Any]]:
        """Get performance trends over time"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        # Group by time intervals
        cursor.execute('''
            SELECT 
                datetime(CAST(strftime('%s', timestamp) / ? AS INTEGER) * ?, 'unixepoch') as interval_start,
                COUNT(*) as count,
                AVG(execution_time) as avg_time,
                AVG(confidence) as avg_confidence,
                SUM(CASE WHEN error_occurred THEN 1 ELSE 0 END) as errors
            FROM performance_metrics
            WHERE timestamp >= ?
            GROUP BY interval_start
            ORDER BY interval_start
        ''', (interval_hours * 3600, interval_hours * 3600, cutoff_time))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                'interval': row['interval_start'],
                'count': row['count'],
                'avg_execution_time': round(row['avg_time'] or 0, 3),
                'avg_confidence': round(row['avg_confidence'] or 0, 3),
                'errors': row['errors']
            }
            for row in rows
        ]
    
    def export_json(self, hours: int = 24, output_file: Optional[str] = None) -> str:
        """Export data as JSON"""
        data = {
            'summary': self.get_summary(hours),
            'by_reasoning_mode': self.get_by_reasoning_mode(hours),
            'trends': self.get_trends(hours),
            'recent_records': self.get_recent_records(50)
        }
        
        json_str = json.dumps(data, indent=2, default=str)
        
        if output_file:
            Path(output_file).write_text(json_str)
            return f"✅ Exported to {output_file}"
        
        return json_str

def print_summary(summary: Dict[str, Any]):
    """Print formatted summary"""
    print("\n" + "="*70)
    print("PERFORMANCE METRICS SUMMARY")
    print("="*70)
    print(f"Period: Last {summary.get('period_hours', 0)} hours")
    print()
    
    if summary.get('message'):
        print(f"⚠️  {summary['message']}")
        return
    
    print(f"📊 Total Requests: {summary['total_requests']}")
    print()
    print("⏱️  Execution Time:")
    print(f"   Average: {summary['avg_execution_time']}s")
    print(f"   Min: {summary['min_execution_time']}s")
    print(f"   Max: {summary['max_execution_time']}s")
    print()
    print("🎯 Confidence:")
    print(f"   Average: {summary['avg_confidence']:.1%}")
    print()
    print("⚡ Performance:")
    print(f"   Cache Hit Rate: {summary['cache_hit_rate']:.1f}%")
    print(f"   Optimization Rate: {summary['optimization_rate']:.1f}%")
    print(f"   Error Rate: {summary['error_rate']:.1f}%")
    print()
    print("💻 Resource Usage:")
    print(f"   Memory: {summary['avg_memory_usage_mb']:.1f} MB")
    print(f"   CPU: {summary['avg_cpu_usage_percent']:.1f}%")
    print("="*70)

def print_by_mode(by_mode: Dict[str, Dict[str, Any]]):
    """Print statistics by reasoning mode"""
    if not by_mode:
        print("\n⚠️  No data by reasoning mode")
        return
    
    print("\n" + "="*70)
    print("STATISTICS BY REASONING MODE")
    print("="*70)
    print()
    
    for mode, stats in by_mode.items():
        print(f"📋 {mode or 'Unknown'}:")
        print(f"   Requests: {stats['count']}")
        print(f"   Avg Time: {stats['avg_execution_time']}s")
        print(f"   Avg Confidence: {stats['avg_confidence']:.1%}")
        print(f"   Errors: {stats['errors']} ({stats['error_rate']:.1f}%)")
        print()

def print_recent(records: List[Dict[str, Any]]):
    """Print recent records"""
    if not records:
        print("\n⚠️  No recent records")
        return
    
    print("\n" + "="*70)
    print(f"RECENT RECORDS (Last {len(records)})")
    print("="*70)
    print()
    
    for i, record in enumerate(records, 1):
        print(f"{i}. {record.get('timestamp', 'N/A')}")
        print(f"   Mode: {record.get('reasoning_mode', 'N/A')}")
        print(f"   Time: {record.get('execution_time', 0):.3f}s")
        print(f"   Confidence: {record.get('confidence', 0):.1%}")
        print(f"   Cache: {'✅' if record.get('cache_hit') else '❌'}")
        print(f"   Error: {'❌' if record.get('error_occurred') else '✅'}")
        print()

def main():
    parser = argparse.ArgumentParser(description='View performance metrics from performance_metrics.db')
    parser.add_argument('--db', default='performance_metrics.db', help='Path to database file')
    parser.add_argument('--hours', type=int, default=24, help='Hours of data to analyze (default: 24)')
    parser.add_argument('--summary', action='store_true', help='Show summary statistics')
    parser.add_argument('--by-mode', action='store_true', help='Show statistics by reasoning mode')
    parser.add_argument('--recent', type=int, metavar='N', help='Show N most recent records')
    parser.add_argument('--trends', action='store_true', help='Show performance trends')
    parser.add_argument('--export', metavar='FILE', help='Export data as JSON to FILE')
    parser.add_argument('--all', action='store_true', help='Show all available data')
    
    args = parser.parse_args()
    
    viewer = PerformanceMetricsViewer(args.db)
    
    if args.all:
        print_summary(viewer.get_summary(args.hours))
        print_by_mode(viewer.get_by_reasoning_mode(args.hours))
        print_recent(viewer.get_recent_records(10))
    elif args.summary:
        print_summary(viewer.get_summary(args.hours))
    elif args.by_mode:
        print_by_mode(viewer.get_by_reasoning_mode(args.hours))
    elif args.recent:
        print_recent(viewer.get_recent_records(args.recent))
    elif args.trends:
        trends = viewer.get_trends(args.hours)
        print("\n" + "="*70)
        print("PERFORMANCE TRENDS")
        print("="*70)
        for trend in trends:
            print(f"{trend['interval']}: {trend['count']} requests, "
                  f"{trend['avg_execution_time']}s avg, "
                  f"{trend['errors']} errors")
    elif args.export:
        result = viewer.export_json(args.hours, args.export)
        print(result)
    else:
        # Default: show summary
        print_summary(viewer.get_summary(args.hours))

if __name__ == "__main__":
    main()

