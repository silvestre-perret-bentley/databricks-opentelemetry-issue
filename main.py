import logging
from typing import Literal

import dotenv
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
import uvicorn
from fastapi import FastAPI

import mlflow.langchain
from databricks_langchain import ChatDatabricks
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver

dotenv.load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set up MLflow tracking first (this creates the initial tracer provider)
mlflow.langchain.autolog()
mlflow.set_tracking_uri("databricks")
mlflow.set_experiment("/Shared/langgraph-tracing-demo")

# NOW configure Azure Monitor to work alongside Databricks
def configure_dual_tracing():
    """Configure tracing to send to both Databricks and Azure Monitor"""
    from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    import os
    
    # Get the existing provider (set up by MLflow)
    existing_provider = trace.get_tracer_provider()
    
    # Check if it's a real TracerProvider
    if existing_provider.__class__.__name__ == "TracerProvider":
        print("✅ Found Databricks tracer provider - adding Azure Monitor")
        
        # Create Azure Monitor exporter
        connection_string = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")
        if connection_string:
            azure_exporter = AzureMonitorTraceExporter(connection_string=connection_string)
            azure_processor = BatchSpanProcessor(azure_exporter)
            existing_provider.add_span_processor(azure_processor)
            print("✅ Traces will now go to BOTH Databricks and Azure Monitor!")
        else:
            print("⚠️  No Azure Monitor connection string found")
    else:
        print("⚠️  No Databricks provider found - using Azure Monitor only")
        from azure.monitor.opentelemetry import configure_azure_monitor
        configure_azure_monitor()

# Configure dual tracing
configure_dual_tracing()

@tool
def get_weather(city: Literal["nyc", "sf"]):
    """Use this to get weather information."""
    if city == "nyc":
        return "It might be cloudy in nyc"
    elif city == "sf":
        return "It's always sunny in sf"

llm = ChatDatabricks(model="azure-openai-gpt-4o-ptu")
tools = [get_weather]
agent_executor = create_react_agent(llm, tools, checkpointer=MemorySaver())

app = FastAPI()
FastAPIInstrumentor.instrument_app(app)

@app.get("/")
async def root():
    events = await agent_executor.ainvoke(
        {
            "messages": [
                {
                    "role": "user", 
                    "content": "Hi, I'm Bob and I live in SF.",
                }
            ]
        },
        config={"configurable": {"thread_id": "abc123"}},
    )
    logger.info("Test successful - check both Databricks and Azure Monitor for traces!")
    return events["messages"][-1].content

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)