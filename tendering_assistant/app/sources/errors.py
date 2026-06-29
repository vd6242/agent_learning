class SourceConfigurationError(RuntimeError):
    """Raised when a tender source connector is missing required setup
    (API endpoint, credentials, etc.)."""
