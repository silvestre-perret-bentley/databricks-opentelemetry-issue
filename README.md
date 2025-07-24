# Databricks OpenTelemetry Issue

## Prerequisites

- Python 3.11 or higher
- [uv](https://docs.astral.sh/uv/) package manager
- Access to Databricks workspace
- Azure Monitor configuration

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd databricks-opentelemetry-issue
   ```

2. **Install dependencies using uv**:
   ```bash
   uv sync
   ```

3. **Set up environment variables**:
   Create a `.env` file in the project root with your Databricks and Azure credentials:
   ```env
   DATABRICKS_HOST=your-databricks-host
   DATABRICKS_TOKEN=your-databricks-token
   AZURE_MONITOR_CONNECTION_STRING=your-azure-monitor-connection-string
   ```

## Running the Application

Start the FastAPI web server using uv:

```bash
uv run fastapi run main.py
```

The server will start on `http://0.0.0.0:8000` by default.

## API Endpoints

- **GET /** - Root endpoint that demonstrates the LangGraph agent in action
  - Sends a greeting message to the agent
  - Returns the agent's response

## Remarks

If you comment out the line `configure_azure_monitor()` in `main.py`, the application traces will correctly be collected by Databricks. 

However, when the Azure Monitor configuration is enabled, the traces are not collected by Databricks.