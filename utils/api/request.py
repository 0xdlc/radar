
from typing import Dict, List, Optional, Union
import logging
#import brotli
import json
import gzip
from requests.adapters import HTTPAdapter, Retry
import requests
import requests.structures
import cloudscraper
import time
import httpx
import ssl


class APIRequest(object):
    
    #Class to make requests to the Endpoints and Handle Network Errors
    
    # __content_encodings = {
    #     "": lambda x: x,
    #     "br": brotli.decompress,
    #     "gzip": gzip.decompress
    # }

    def __init__(
        self,
        url: str,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        data: Optional[Dict] = None,
        cookies: Optional[Dict] = None,
        exclude_status_codes: List[int] = list(),
        retries: int = 10,
        backoff_factor: int = 3,
        debug: bool = False
    ):

        """
        Constructor of the APIRequest class.
        self.retries = retries
        self.backoff_factor = backoff_factor
        self.make_request_with_retry()
        :param url: URL for the request
        :param params: params that will be inserted on the URL for the request
        :param headers: headers for the request
        :param data: data for the request. If "data" is None, request will be a GET. Otherwise, it will be a POST
        :param cookies: cookies for the request
        :param exclude_status_codes: raise for status code except those on the excluded list
        """
        self.url = url
        self.stat = False #will be true if internet went out  
        self.request_params = {
            "params": params,
            "headers": headers,
            "data": data,
            "cookies": cookies
        }
        self.proxies = {
            "https":"127.0.0.1:8080",
            "http":"127.0.0.1:8080"
        }
        # self.proxies = {
        #     "http://": httpx.HTTPTransport(proxy="http://127.0.0.1:8080"),
        #     "https://": httpx.HTTPTransport(proxy="http://127.0.0.1:8080"),
        # }
        if debug:
            logging.basicConfig(
                format="%(levelname)s [%(asctime)s] %(name)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
                level=logging.DEBUG
            )
        self.retries = retries
        self.backoff_factor = backoff_factor
        self.scraper = cloudscraper.create_scraper(browser='chrome')
        #self.make_request_with_retry()
        self.context = ssl.create_default_context()
        self.context.load_verify_locations(cafile="/home/madvillain/Downloads/ca.pem")
        self.make_request_with_retry()
    def make_httpx_request(self):
        with httpx.Client(http2=True) as client:
            if self.request_params["params"]:
                url_with_params = self.url + "?" + "&".join(["{}={}".format(k, v) for k, v in self.request_params["params"].items()])
                self.__response = client.get(url_with_params, headers=self.request_params["headers"])
            else:
                self.__response = client.get(self.url, headers=self.request_params["headers"], cookies=self.request_params["cookies"])
        print("made req")
        return self.__response
    def make_request_with_retry(self):
        cnt = 60
        try:
            s = requests.Session()
            retry_strategy = Retry(total=self.retries, backoff_factor=self.backoff_factor, status_forcelist=[402,409,503,520])
            s.mount('https://', HTTPAdapter(max_retries=retry_strategy))
            if self.request_params["params"]:
                url_with_params = self.url + "?" + "&".join(["{}={}".format(k, v) for k, v in self.request_params["params"].items()])
                self.__response = s.get(url_with_params, headers=self.request_params["headers"])
            else:
                self.__response = s.get(self.url, headers=self.request_params["headers"],cookies=self.request_params["cookies"])#, verify=False, proxies=self.proxies)

            return self.__response
        except Exception as e:
            print(f"[DEBUG] Network Error! Check The Internet Connection, trying again in{cnt/60} minutes{e}")
            time.sleep(cnt)
            #cnt += 60
            self.retries -= 1
            pass
        # #self.stat=True
        # return #self.stat
        # #return None
    def get_content(self) -> Union[Dict, bytes]:
        """
        Return the received content from the request.
        """
        content = self.__response.content

        content_encoding = self.__response.headers.get("Content-Encoding", "")
        content_type = self.__response.headers["Content-Type"]

        # Try to decode the content.
        try: content = self.__content_encodings[content_encoding](content)
        except Exception: pass

        # Return a dictionary if the content type is JSON.
        if "application/json" in content_type:
            return json.loads(content)

        return content

    def get_cookies(self) -> Dict:
        """
        Return the received cookies from the request.
        """
        return self.__response.cookies.get_dict()

    def get_headers(self) -> requests.structures.CaseInsensitiveDict:
        """
        Return the headers of the response.
        """
        return self.__response.headers

    def get_response_object(self) -> requests.models.Response:
        """
        Return the received response object.
        """
        return self.__response

    def get_status_code(self) -> int:
        """
        Return the status code of the response.
        """
        return self.__response.status_code
