# Databricks OpenTelemetry Issue

## Steps to Reproduce

1. **Run without Azure Monitor**:
    - Comment out `configure_azure_monitor()` in `main.py`
    - Start the application
    - Send a request to the root endpoint
    - Verify that traces appear in Databricks

2. **Run with Azure Monitor**:
    - Uncomment `configure_azure_monitor()` in `main.py`
    - Start the application
    - Send a request to the root endpoint
    - Observe that traces are not collected in Databricks
    - Verify that traces are collected in Azure Monitor

## Expected Behavior
- Traces should be collected by Databricks regardless of Azure Monitor configuration

## Actual Behavior
- Traces are only collected when Azure Monitor is disabled
- No traces appear in Databricks when Azure Monitor is enabled
