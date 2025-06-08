import logging
from datetime import datetime

# Set up a specific logger for requests
# This logger will write to a file named 'requests.log'
requests_logger = logging.getLogger('requests')
requests_logger.setLevel(logging.INFO)

# Create a file handler to manage the log file
handler = logging.FileHandler('requests.log')

# Set a simple formatter to only output the message
formatter = logging.Formatter('%(message)s')
handler.setFormatter(formatter)

# Add the handler to the logger
if not requests_logger.handlers:
    requests_logger.addHandler(handler)


class RequestLoggingMiddleware:
    """
    Middleware that logs information about each incoming request to a file.
    """
    def __init__(self, get_response):
        """
        One-time configuration and initialization for the middleware.
        """
        self.get_response = get_response
    
    def __call__(self, request):
        """
        This method is called for each request.
        """
        # Determine the user for the log message.
        # If the user is authenticated, use their username. Otherwise, note that they are anonymous.
        user = request.user if request.user.is_authenticated else 'AnonymousUser'

        # Log the required information using our configured logger.
        requests_logger.info(f"{datetime.now()} - User: {user} - Path: {request.path}")

        # Continue processing the request by calling the next middleware or view.
        response = self.get_response(request)

        return response
