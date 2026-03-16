from prometheus_client import Counter, Histogram, start_http_server
from functools import wraps

REQUEST_COUNT = Counter('api_requests_total', 'Total API requests', ['method', 'endpoint'])
REQUEST_LATENCY = Histogram('api_request_duration_seconds', 'Request latency')

def track_latency(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        REQUEST_COUNT.labels(method='POST', endpoint=func.__name__).inc()
        with REQUEST_LATENCY.time():
            return func(*args, **kwargs)
    return wrapper

def setup_metrics(app):
    \"\"\"Setup Prometheus metrics server and middleware.\"\"\"
    from prometheus_client import start_http_server, Counter, Histogram, generate_latest

    # Global metrics (if not already defined)
    global REQUEST_COUNT, REQUEST_LATENCY
    REQUEST_COUNT = Counter('archcompass_requests_total', 'Total requests', ['method', 'endpoint'])
    REQUEST_LATENCY = Histogram('archcompass_request_duration_seconds', 'Request latency')

    # Start metrics server on port 9090
    start_http_server(9090)
    print("Prometheus metrics server started on :9090/metrics")

    # Example app metrics binding (Flask example)
    if app:
        @app.before_request
        def metrics_start():
            request.environ['request_start'] = [time.time()]

        @app.after_request
        def metrics_end(response):
            resp_time = time.time() - request.environ['request_start'][0]
            REQUEST_COUNT.labels(method=request.method, endpoint=request.path).inc()
            REQUEST_LATENCY.observe(resp_time)
            return response

    return {"metrics_port": 9090}
