import logging
from typing import Literal

import dotenv
from azure.monitor.opentelemetry import configure_azure_monitor
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
configure_azure_monitor()
logger = logging.getLogger(__name__)

mlflow.langchain.autolog()

# Set up MLflow tracking to Databricks
mlflow.set_tracking_uri("databricks")
mlflow.set_experiment("/Shared/langgraph-tracing-demo")

@tool
def get_weather(city: Literal["nyc", "sf"]):
    """Use this to get weather information."""
    if city == "nyc":
        return "It might be cloudy in nyc"
    elif city == "sf":
        return "It's always sunny in sf"


llm = ChatDatabricks(
    model="azure-openai-gpt-4o-ptu",
)
tools = [get_weather]

# llm_with_tools = llm.bind_tools(tools)
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
    logger.info("databricks test")
    return events["messages"][-1].content

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
