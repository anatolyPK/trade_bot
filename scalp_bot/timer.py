import time

class Timer:
    def __init__(self, time_work_sec):
        self._start_time = 0
        self.time_work = time_work_sec
  
    def start(self):
        self._start_time = time.perf_counter()

    def is_ready(self):
        if time.perf_counter() - self._start_time > self.time_work:
            return True
        return False
 
    def stop(self):
        elapsed_time = time.perf_counter() - self._start_time
        self._start_time = None
