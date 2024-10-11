
from typing import Dict, List, Optional, Union
import logging
#import brotli
import urllib3
urllib3.disable_warnings()
from urllib.parse import urlencode

import json
from requests.adapters import HTTPAdapter, Retry
import requests
import requests.structures
import time
import httpx

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
        debug: bool = False,
        method: str = "get",
        ip: str = ""
    ):

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
        self.source_ip = ip
        # logging.basicConfig(
        #     format="%(levelname)s [%(asctime)s] %(name)s - %(message)s",
        #     datefmt="%Y-%m-%d %H:%M:%S",
        #     level=logging.DEBUG
        # )
        self.retries = retries
        self.backoff_factor = backoff_factor
        self.method = method
        
        #self.urllib()
        #logging.getLogger("urllib3").setLevel(logging.DEBUG)
    def urllib(self):

        http = urllib3.PoolManager()
        #http = urllib3.ProxyManager('http://185.126.4.138:8899',source_address=('', self.local_port), cert_reqs='CERT_NONE')
        #http = urllib3.ProxyManager('http://127.0.0.1:8080',source_address=('', 52001), cert_reqs='CERT_NONE')

        # Build the full URL with query parameters if they exist
        if self.request_params["params"]:
            query_string = urlencode(self.request_params["params"])
            self.url = f"{self.url}?{query_string}"

        # Prepare headers and cookies
        headers = self.request_params["headers"]
        cookies = self.request_params["cookies"]

        # Make the request based on the method
        for i in range(1,20):
            try:
                if self.method == "post":
                    response = http.request(
                        'POST',
                        self.url,
                        headers=headers,
                        #fields= self.request_params["params"],
                        body=urlencode(self.request_params["data"]),
                        preload_content=True
                    )
                else:
                    response = http.request(
                        'GET',
                        self.url,
                        headers=headers,
                        preload_content=True
                    )
                return response

            except Exception as e:
                print(f"An error occurred: {e}")
                print(f"Attempt {i} failed. Retrying in 1 second...")
                time.sleep(1)  # Wait before retrying


    def make_httpx_request(self):
        with httpx.Client(http2=True,verify=False) as client:
            if self.request_params["params"]:
                self.url = self.url + "?" + "&".join(["{}={}".format(k, v) for k, v in self.request_params["params"].items()])
            if self.method == "post":
                self.__response = client.post(self.url, headers=self.request_params["headers"],cookies=self.request_params["cookies"],data=self.request_params["data"], timeout=None)#, verify=False, proxies=self.proxies)
            else:
                self.__response = client.get(self.url, headers=self.request_params["headers"],cookies=self.request_params["cookies"], timeout=None)#, verify=False, proxies=self.proxies)
            return self.__response
    def make_request_with_retry(self):
        cnt = 60
        try:
            s = requests.Session()
            retry_strategy = Retry(total=self.retries, backoff_factor=self.backoff_factor, status_forcelist=[400])
            s.mount('https://', HTTPAdapter(max_retries=retry_strategy))
            
            if self.request_params["params"]:
                self.url = self.url + "?" + "&".join(["{}={}".format(k, v) for k, v in self.request_params["params"].items()])
            if self.method == "post":
                self.__response = s.post(self.url, headers=self.request_params["headers"],cookies=self.request_params["cookies"],verify=False)#,data=self.request_params["data"], verify=False, proxies=self.proxies)
            else:
                self.__response = s.get(self.url, headers=self.request_params["headers"],cookies=self.request_params["cookies"],verify=False)#, verify=False, proxies=self.proxies)
            
            return self.__response
        except Exception as e:
            print(f"[DEBUG] Network Error! Check The Internet Connection, trying again in{cnt/60} minutes{e}")
            time.sleep(cnt)
            pass
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
