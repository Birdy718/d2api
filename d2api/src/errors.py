#!/usr/bin/env python
# -*- coding: utf-8 -*-
class BaseError(Exception):
    """Generic error wrapper."""
    def __init__(self, msg):
        self._msg = msg
        
    def __str__(self):
        return repr(self._msg)

class APIAuthenticationError(BaseError):
    """Error for invalid API key."""
    def __init__(self, api_key = None):
        self._msg = f"HTTP 403: Authentication error caused by API key \"{api_key}\"."

class APIMethodUnavailable(BaseError):
    """Error if the API method is discontued/broken."""
    def __init__(self, method_url = None):
        self._msg = f"HTTP 404: \"{method_url}\" is an unsupported/discontinued API method."

class APIInsufficientArguments(BaseError):
    """Error for incomplete API call.""" 
    def __init__(self, query = None, params = {}):
        self._msg = f"HTTP 400: Insufficient arguments for \"{query}\". Parameters provided: {params}"

class APITimeoutError(BaseError):
    """Error for server timeout."""
    def __init__(self):
        self._msg = "HTTP 503: Timeout error."