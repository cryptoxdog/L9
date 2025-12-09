# tests/memory/test_concurrency.py

from memory.shared.concurrency_manager import concurrency
import threading

def test_lock_exclusivity():
    results = []
    
    def task():
        with concurrency.lock("test_key"):
            results.append("locked")
    
    t1 = threading.Thread(target=task)
    t2 = threading.Thread(target=task)
    
    t1.start()
    t2.start()
    
    t1.join()
    t2.join()
    
    assert len(results) == 2

