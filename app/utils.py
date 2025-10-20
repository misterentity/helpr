import re
import logging
from urllib.parse import urlparse, urljoin
from flask import request

logger = logging.getLogger(__name__)

def validate_email_or_username(value):
    """
    Validate that the input is either a valid email or a reasonable username.
    
    Args:
        value: String to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not value or len(value) < 3:
        return False
    
    # Check if it's a valid email format
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if re.match(email_pattern, value):
        return True
    
    # Check if it's a valid username (alphanumeric, underscores, hyphens, dots)
    username_pattern = r'^[a-zA-Z0-9._-]{3,50}$'
    if re.match(username_pattern, value):
        return True
    
    return False

def sanitize_input(value):
    """
    Sanitize user input by trimming and removing control characters.
    Note: HTML escaping is handled automatically by Jinja2 templates.
    
    Args:
        value: String to sanitize
        
    Returns:
        str: Sanitized string
    """
    if not value:
        return ""
    
    # Strip whitespace
    value = value.strip()
    
    # Remove any control characters (except newline, carriage return, tab)
    value = ''.join(char for char in value if ord(char) >= 32 or char in '\n\r\t')
    
    return value

def format_error_message(error):
    """
    Format error messages for user display.
    
    Args:
        error: Exception or error message
        
    Returns:
        str: Formatted error message
    """
    error_str = str(error)
    
    # Make common errors more user-friendly
    if "already has access" in error_str.lower() or "already invited" in error_str.lower():
        return "This user already has access or has been invited."
    elif "not found" in error_str.lower():
        return "User not found. Please check the username or email address."
    elif "invalid token" in error_str.lower():
        return "Server configuration error. Please contact the administrator."
    elif "unauthorized" in error_str.lower():
        return "Authentication error. Please contact the administrator."
    
    # Return generic message for unknown errors
    return "An error occurred while processing your request."

def is_safe_url(target, host_url):
    """
    Validate that a redirect URL is safe (local, relative path).
    
    Args:
        target: The URL to redirect to
        host_url: The host URL to validate against
        
    Returns:
        bool: True if safe, False otherwise
    """
    if not target:
        return False
    
    # Parse the target URL
    ref_url = urlparse(host_url)
    test_url = urlparse(urljoin(host_url, target))
    
    # Ensure the scheme and netloc match (same host) or target is relative
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc

def setup_logging():
    """Configure application logging."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('app.log'),
            logging.StreamHandler()
        ]
)

