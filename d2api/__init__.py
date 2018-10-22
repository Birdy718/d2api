import os
import requests
from .src import endpoints
from .src.wrappers import *
from .src.errors import *
import logging

class APIWrapper:
    def __init__(self, api_key = None, log_enabled = False):

        self.api_key = api_key if api_key else os.environ.get('DOTA2_API_KEY')
        if log_enabled:
            logger = logging.getLogger("d2api")
            logger.setLevel(logging.DEBUG)
            self.logger = logger
        else:
            logging.getLogger("requests").setLevel(logging.WARNING)


    def __api_call(self, url = endpoints.GET_MATCH_HISTORY, **kwargs):
        kwargs['key'] = self.api_key
        response = requests.get(url, params = kwargs, timeout = 60)
        status = response.status_code
        if status == 200:
            return response
        elif status == 403:
            raise APIAuthenticationError()
        elif status == 503:
            raise APITimeoutError()
        else:
            raise BaseError(msg = response.reason)

    def get_match_history(self, **kwargs):
        api_response = self.__api_call(endpoints.GET_MATCH_HISTORY, **kwargs)
        return GetMatchHistory(api_response)

    def get_match_history_by_sequence_num(self, **kwargs):
        api_response = self.__api_call(endpoints.GET_MATCH_HISTORY_BY_SEQ_NUM, **kwargs)
        return GetMatchHistory(api_response)

    def get_match_details(self, match_id, **kwargs):
        kwargs['match_id'] = match_id
        api_response = self.__api_call(endpoints.GET_MATCH_DETAILS, **kwargs)
        return GetMatchDetails(api_response)

    def get_heroes(self, **kwargs):
        kwargs['language'] = kwargs.get('language', 'en_us')
        api_response = self.__api_call(endpoints.GET_HEROES, **kwargs)
        return GetHeroes(api_response)

    def get_game_items(self, **kwargs):
        kwargs['language'] = kwargs.get('language', 'en_us')
        api_response = self.__api_call(endpoints.GET_GAME_ITEMS, **kwargs)
        return GetGameItems(api_response)
    
