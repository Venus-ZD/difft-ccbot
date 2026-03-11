import collections
import hashlib
import hmac
import time
import uuid
from urllib.parse import urlparse, parse_qs

import requests

ALGORITHM_HMAC_SHA256 = "HmacSHA256"
HEADER_NAME_APPID = "X-Signature-appid"
HEADER_NAME_TIMESTAMP = "X-Signature-timestamp"
HEADER_NAME_NONCE = "X-Signature-nonce"
HEADER_NAME_ALGORITHM = "X-Signature-algorithm"
HEADER_NAME_SIGNEDHEADERS = "X-Signature-signedHeaders"
HEADER_NAME_SIGNATURE = "X-Signature-signature"


class _Signature:
    def __init__(self, timestamp, nonce, algorithm, signature):
        self.timestamp = timestamp
        self.nonce = nonce
        self.algorithm = algorithm
        self.signature = signature


class Authenticator(requests.auth.AuthBase):
    def __init__(self, appid: str, key: bytes):
        self._appid = appid
        self._key = key
        self._headerToSign = ["Content-Type", "Content-Length"]

    def __call__(self, r):
        method = r.method
        parsed_url = urlparse(r.url)
        uri = parsed_url.path
        query_parameters = parse_qs(parsed_url.query)
        sorted_query_parameters = collections.OrderedDict(sorted(query_parameters.items()))
        headers = r.headers
        headerToSign = {}
        headerToSignList = []
        for k in headers:
            if k in self._headerToSign:
                headerToSign[k] = headers[k]
                headerToSignList.append(k)
        headerToSignStr = ",".join(headerToSignList)
        sorted_headers = collections.OrderedDict(sorted(headerToSign.items()))
        body = r.body
        dataToSign = self._build_data(method, uri, sorted_query_parameters, sorted_headers, body)
        signature = self._sign(dataToSign)
        r.headers.update({
            HEADER_NAME_APPID: self._appid,
            HEADER_NAME_TIMESTAMP: signature.timestamp,
            HEADER_NAME_NONCE: signature.nonce,
            HEADER_NAME_ALGORITHM: signature.algorithm,
            HEADER_NAME_SIGNEDHEADERS: headerToSignStr,
            HEADER_NAME_SIGNATURE: signature.signature,
        })
        return r

    def _build_data(self, method, uri, parameters, headers, body):
        data = method + ";" + uri + ";"
        for k in parameters:
            for i in parameters[k]:
                data += k + "=" + i + ","
        data = data[:-1]
        data += ";"
        for k in headers:
            data += k.lower() + "=" + headers[k] + ","
        data = data[:-1]
        data += ";"
        data = data.encode("utf-8")
        if body:
            data += body
        return data

    def _sign(self, msg: bytes) -> _Signature:
        ts = int(time.time() * 1000)
        nonce = uuid.uuid4().hex
        prefix = ";".join([self._appid, str(ts), nonce]) + ";"
        msg = prefix.encode("utf-8") + msg
        sign_str = hmac.new(self._key, msg, hashlib.sha256).hexdigest()
        return _Signature(timestamp=ts, nonce=nonce, algorithm=ALGORITHM_HMAC_SHA256, signature=sign_str)
