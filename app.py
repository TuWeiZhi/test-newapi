from flask import Flask, render_template, Response, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import time
import threading
from log_broadcaster import log_queue
from main import run_keeper_task

app = Flask(__name__)

scheduler = BackgroundScheduler()
task_running = False
task_lock = threading.Lock()

def scheduled_task():
    global task_running
    with task_lock:
        if task_running:
            return
        task_running = True
    
    try:
        run_keeper_task()
    finally:
        with task_lock:
            task_running = False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/trigger', methods=['POST'])
def trigger_task():
    global task_running
    with task_lock:
        if task_running:
            return jsonify({'status': 'error', 'message': 'Task is already running'}), 400
    
    thread = threading.Thread(target=scheduled_task)
    thread.daemon = True
    thread.start()
    
    return jsonify({'status': 'success', 'message': 'Task triggered'})

@app.route('/api/status')
def get_status():
    next_run = scheduler.get_job('keeper_task').next_run_time if scheduler.get_job('keeper_task') else None
    return jsonify({
        'running': task_running,
        'next_run': next_run.isoformat() if next_run else None
    })

@app.route('/api/logs/history')
def get_history():
    from pathlib import Path
    
    main_log = Path('logs/newapi_keeper.log')
    detail_log = Path('logs/request_details.jsonl')
    
    main_lines = []
    detail_lines = []
    
    if main_log.exists():
        with open(main_log, 'r', encoding='utf-8') as f:
            main_lines = f.readlines()[-500:]
    
    if detail_log.exists():
        with open(detail_log, 'r', encoding='utf-8') as f:
            detail_lines = f.readlines()[-500:]
    
    return jsonify({
        'main': [line.strip() for line in main_lines],
        'detail': [line.strip() for line in detail_lines]
    })

@app.route('/api/logs/stream')
def log_stream():
    def generate():
        while True:
            try:
                log_data = log_queue.get(timeout=30)
                yield f"data: {log_data['type']}|{log_data['message']}\n\n"
            except:
                yield f"data: ping|heartbeat\n\n"
    
    return Response(generate(), mimetype='text/event-stream')

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='NewAPI Keeper Dashboard')
    parser.add_argument('-p', '--port', type=int, default=5000, help='Port to run on (default: 5000)')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='Host to bind (default: 0.0.0.0)')
    args = parser.parse_args()
    
    scheduler.add_job(
        scheduled_task,
        'interval',
        hours=12,
        id='keeper_task',
        next_run_time=datetime.now()
    )
    scheduler.start()
    
    app.run(host=args.host, port=args.port, threaded=True)
