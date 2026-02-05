import queue
import threading

log_queue = queue.Queue(maxsize=1000)

def broadcast_log(message: str, log_type: str = 'info'):
    try:
        log_queue.put_nowait({
            'type': log_type,
            'message': message
        })
    except queue.Full:
        pass
