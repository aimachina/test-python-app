from flask import Flask
import logging
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.logging import LoggingInstrumentor

# Configure the OpenTelemetry tracer provider and the OTLP exporter
resource = Resource.create(attributes={"service.name": "test-python-app"})
provider = TracerProvider(resource=resource)
otlp_exporter = OTLPSpanExporter(endpoint="http://tempo.monitor.svc.cluster.local:4317", insecure=True)
span_processor = BatchSpanProcessor(otlp_exporter)
provider.add_span_processor(span_processor)
trace.set_tracer_provider(provider)

# Initialize logging with OpenTelemetry instrumentation
LoggingInstrumentor().instrument(set_logging_format=True)

# Create Flask application
app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)

# Configure basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/')
def index():
    logger.info("Root endpoint was called")
    return "Hello, OpenTelemetry with Tempo!", 200

@app.route('/error')
def error():
    logger.error("Error endpoint was triggered")
    return "Error logged", 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=9097)
