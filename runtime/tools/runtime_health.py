"""
Runtime Health Monitor
"""
import psutil
import logging

logger = logging.getLogger(__name__)


def check_runtime_health() -> dict:
    """
    Check L9 Runtime health.
    
    Returns:
        Health metrics including CPU, memory, disk
    """
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Determine status
        if cpu_percent > 90 or memory.percent > 90 or disk.percent > 90:
            status = "critical"
        elif cpu_percent > 80 or memory.percent > 80 or disk.percent > 80:
            status = "degraded"
        else:
            status = "healthy"
        
        health = {
            "status": status,
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "memory_available_mb": memory.available / (1024 * 1024),
            "disk_percent": disk.percent,
            "disk_free_gb": disk.free / (1024 * 1024 * 1024)
        }
        
        logger.info(f"Runtime health: {status}")
        return health
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


if __name__ == "__main__":
    # Standalone execution
    health = check_runtime_health()
    print(f"Runtime Health: {health['status']}")
    print(f"  CPU: {health.get('cpu_percent', 0):.1f}%")
    print(f"  Memory: {health.get('memory_percent', 0):.1f}%")
    print(f"  Disk: {health.get('disk_percent', 0):.1f}%")

