class RetryableError(Exception):
    """Exception raised for errors that are temporary and may succeed if retried."""
    pass