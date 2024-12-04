
from requests.adapters import HTTPAdapter, Retry
from curl_cffi import requests as cffi_requests
from typing import Dict, List, Optional, Union
import requests.structures
import requests
#import brotli
import urllib3
import logging
import httpx
import time
import json


urllib3.disable_warnings()
class HTTPClientError(Exception):
    """Base exception class for HTTP client errors"""
    def __init__(self, message: str, original_error: Exception = None, status_code: int = None):
        self.message = message
        self.original_error = original_error
        self.status_code = status_code
        super().__init__(self.message)

class ConnectionError(HTTPClientError):
    """Raised when a connection cannot be established"""
    pass

class TimeoutError(HTTPClientError):
    """Raised when the request times out"""
    pass

class ResponseError(HTTPClientError):
    """Raised when receiving an invalid response"""
    pass

class errorCodes:
    def __init__(self):
        self._errors = {'connection':1,
                      'timeout':2,
                      'status':3,
                      'dns': 4,
                      'unexpected': 5
                      }
        
    def __getattr__(self,error):
        if error in self._errors:
            return self._errors[error]
        raise AttributeError(f"No such error as '{error}'") from None


class APIRequest(object):
    """main api that initiates a request"""
    def __init__(
        self,
        url: str,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        data: Optional[Dict] = None, # form values(dict/list/tuple) or binary data to use in body, Content-Type: application/x-www-form-urlencoded will be added if a dict is given.
        json: Optional[Dict] = None, # json values to use in body, Content-Type: application/json will be added automatically.
        cookies: Optional[Dict] = None,
        retries: int = 10,
        backoff_factor: int = 3,
        status_forcelist: List[int] = frozenset([402,409,503,520]),
        debug: bool = False,
        proxies: dict = None,
        method: int = 1,
        verify: bool = False,
        timeout : int = 30,
        return_error_code: bool = False
    ):
        methods = ["GET", "POST"] #Only supporting these methods for now...
        self.status_forcelist = status_forcelist
        self.backoff_factor = backoff_factor
        self.url = url
        self.retries = retries
        self.backoff_factor = backoff_factor
        self.verify = verify
        self.proxies = proxies
        self.method = methods[method]
        self.return_error_code = return_error_code
        self.timeout = timeout
        self.request_params = {
            "params": params,
            "headers": headers,
            "data": data,
            "cookies": cookies,
            "json": json
        }

        if debug:
            logging.basicConfig(
                format="%(levelname)s [%(asctime)s] %(name)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
                level=logging.DEBUG,
            )
        

    def _handle_exception(self, error: Exception, url: str) -> None:
        _error = errorCodes()
        if isinstance(error, (requests.ConnectionError, httpx.ConnectError, cffi_requests.ConnectionError)):
            print(f"There was an Error while connecting to: '{url}'. Check the internet connection")
            return _error.connection
            # raise ConnectionError(
            #     f"There was an Error while connecting to: {url}. Check the internet connection",
            #     original_error=error
            # ) from None
        elif isinstance(error, (requests.Timeout, httpx.TimeoutException, cffi_requests.Timeout)):
            print(f"Timeout error: '{url}'. Check the internet connection")
            return _error.timeout
            # raise TimeoutError(
            #     f"Request to {url} timed out",
            #     original_error=error
            # )
        elif isinstance(error, (requests.HTTPError, httpx.HTTPError, cffi_requests.exceptions.HTTPError)):
            status_code = None
            if hasattr(error, 'response'):
                status_code = error.response.status_code
            raise ResponseError(
                f"HTTP error occurred: {str(error)}",
                original_error=error,
                status_code=status_code
            )
        else:
            print(f"Timeout error: '{url}'. Check the internet connection")
            return _error.unexpected
            # raise HTTPClientError(
            #     f"Unexpected error: {str(error)}",
            #     original_error=error
            # )


    def CloudScraper_request(self):
        import cloudscraper
        cnt = 60
        try:
            # Create a cloudscraper instance
            scraper = cloudscraper.create_scraper()  # This will handle Cloudflare challenges
            # Set up retry strategy
            retry_strategy = Retry(total=self.retries, backoff_factor=self.backoff_factor, status_forcelist=self.status_forcelist)
            adapter = HTTPAdapter(max_retries=retry_strategy)
            
            # Mount the adapter to the scraper
            scraper.mount('https://', adapter)

            # Construct the URL with parameters if they exist
            if self.request_params["params"]:
                self.url = self.url + "?" + "&".join(["{}={}".format(k, v) for k, v in self.request_params["params"].items()])

            # Make the request based on the method
            if self.method == "POST":
                self.__response = scraper.post(
                    self.url,
                    headers=self.request_params["headers"],
                    cookies=self.request_params["cookies"],
                    verify=self.verify
                )
            else:
                self.__response = scraper.get(
                    self.url,
                    headers=self.request_params["headers"],
                    cookies=self.request_params["cookies"],
                    verify=self.verify
                )
            
            return self.__response
        except Exception as e:
            if self.return_error_code:
                self._handle_exception(e, self.url)
                return e
            else:
                self._handle_exception(e, self.url)            

    def httpx_request(self):
        with httpx.Client(http2=True) as client:
            try:
                if self.request_params["params"]:
                    url_with_params = self.url + "?" + "&".join(["{}={}".format(k, v) for k, v in self.request_params["params"].items()])
                    self.__response = client.get(url_with_params, headers=self.request_params["headers"])
                else:
                    self.__response = client.get(self.url, headers=self.request_params["headers"], cookies=self.request_params["cookies"])
            except Exception as e:
                return self._handle_exception(e, self.url)
        return self.get_content()

    def requests_request(self):
        cnt = 60
        try:
            s = requests.Session()
            retry_strategy = Retry(total=self.retries, backoff_factor=self.backoff_factor, status_forcelist=self.status_forcelist)
            s.mount('https://', HTTPAdapter(max_retries=retry_strategy))
            s.proxies = self.proxies
            if self.method == "POST":
                request_body = self.request_params["data"]
                self.__response = s.post(self.url, headers=self.request_params["headers"], cookies=self.request_params["cookies"], verify=self.verify)

            if self.request_params["params"]:
                url_with_params = self.url + "?" + "&".join(["{}={}".format(k, v) for k, v in self.request_params["params"].items()])
                self.__response = s.get(url_with_params, headers=self.request_params["headers"],cookies=self.request_params["cookies"],verify=self.verify)
            else:
                self.__response = s.get(self.url, headers=self.request_params["headers"],cookies=self.request_params["cookies"], verify=self.verify)#, proxies=self.proxies)#verify="cert.pub"

            return self.get_content()
        except Exception as e:
            if self.return_error_code:
                return self._handle_exception(e, self.url)
            else:
                self._handle_exception(e, self.url)       

    def curl_cffi_request(self):
        try:
            s = cffi_requests.Session(proxies=self.proxies, timeout=self.timeout, verify=self.verify)
            s.proxies = self.proxies
            if self.method=="POST":
                if self.request_params["json"]:
                    self.__response = s.post(self.url,headers=self.request_params["headers"], 
                           cookies=self.request_params["cookies"], 
                           json=self.request_params["json"])
                if self.request_params["data"]:
                    self.__response = s.post(self.url,headers=self.request_params["headers"], 
                                            cookies=self.request_params["cookies"], 
                                            data=self.request_params["data"])
            else:
                if self.request_params["params"]:
                    url_with_params = self.url + "?" + "&".join(["{}={}".format(k, v) for k, v in self.request_params["params"].items()])
                    self.__response = s.get(url_with_params,
                                            headers=self.request_params["headers"],
                                            cookies=self.request_params['cookies'],
                                            )

                else:
                    self.__response = s.get(self.url, headers=self.request_params["headers"],cookies=self.request_params["cookies"])#, proxies=self.proxies)#verify="cert.pub"
            if self.__response.status_code not in self.status_forcelist:
                return self.get_content()
            else:
                self.retries-=1
                while True:
                    if self.retries < 1 or self.__response not in self.status_forcelist:
                        break
                    self.__response.close()
                    time.sleep(self.backoff_factor)

                
                

        except Exception as e:
            if self.return_error_code:
                return self._handle_exception(e, self.url)
            else:
                self._handle_exception(e, self.url)

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
