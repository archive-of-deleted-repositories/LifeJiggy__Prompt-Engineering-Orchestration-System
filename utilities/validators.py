"""Input and output validation utilities."""


class InputValidator:
    """Validates input data."""
    
    def __init__(self, config: dict = None):
        """Initialize the validator.
        
        Args:
            config: Configuration.
        """
        self.config = config or {}
    
    def validate(self, data: dict) -> tuple[bool, list[str]]:
        """Validate input data.
        
        Args:
            data: Data to validate.
            
        Returns:
            Tuple of (is_valid, list_of_errors).
        """
        return True, []
    
    def sanitize(self, data: dict) -> dict:
        """Sanitize input data.
        
        Args:
            data: Data to sanitize.
            
        Returns:
            Sanitized data.
        """
        return data


class OutputValidator:
    """Validates output data."""
    
    def __init__(self, config: dict = None):
        """Initialize the validator.
        
        Args:
            config: Configuration.
        """
        self.config = config or {}
    
    def validate(self, output: str) -> tuple[bool, list[str]]:
        """Validate output.
        
        Args:
            output: Output to validate.
            
        Returns:
            Tuple of (is_valid, list_of_warnings).
        """
        return True, []
    
    def check_safety(self, output: str) -> tuple[bool, str]:
        """Check output for safety issues.
        
        Args:
            output: Output to check.
            
        Returns:
            Tuple of (is_safe, warning_message).
        """
        return True, ""
