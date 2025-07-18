import logging
from datetime import datetime
from django.http import HttpResponseForbidden

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
        # First, pass the request down the chain to the view.
        # This will allow DRF's authentication to run and update the request object.
        response = self.get_response(request)

        # AFTER the view has been processed and the response is on its way back,
        # request.user will have been correctly set by JWTAuthentication

        # print("Request:  ", request.__dict__.get('user'))
        # Determine the user for the log message.
        # If the user is authenticated, use their username. Otherwise, note that they are anonymous.
        user = request.user if request.user.is_authenticated else 'AnonymousUser'

        # Log the required information using our configured logger.
        requests_logger.info(f"{datetime.now()} - User: {user} - Path: {request.path}")

        # # Continue processing the request by calling the next middleware or view.
        # response = self.get_response(request)

        return response


class RestrictAccessByTimeMiddleware:
    """
    Middleware to restrict access to the application outside of specified hours.
    """

    def __init__(self, get_response):
        """
        One-time configuration and initialization for the middleware.
        """
        self.get_response = get_response
    
    def __call__(self, request):
        """
        This method is called for each request.
        It checks the current time and denies access if it's outside business hours.
        """
        # Define the allowed time window (9 AM to 6 PM)
        start_hour = 9  # 9:00 AM
        end_hour = 18  # 6:00 PM (18:00 in 24-hour format)
        current_hour = datetime.now().hour

        # Check if the current hour is outside the allowed window
        if not (start_hour <= current_hour < end_hour):
            # If outside the allowed hours, return a 403 Forbidden response.
            return HttpResponseForbidden("Access to this service is restricted to between 9 AM and 6 PM.")
        
        # If within the allowed hours, continue processing the request.
        response = self.get_response(request)
        return response
