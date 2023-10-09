from pydantic import BaseModel


class OpenTelemetryAdapterConfig(BaseModel):
    """
    Configuration settings for the OpenTelemetry adapter.
    """

    # Hostname or IP address of the OpenTelemetry backend.
    backend_host: str

    # Port number to connect to the OpenTelemetry backend.
    backend_port: int

    # Any additional configuration settings specific to the chosen OpenTelemetry exporter backend.
    # Add fields for exporter-specific settings as needed.
    backend_config: dict