import websockets

import time
import json
import hmac
import hashlib
import asyncio
import logging

from .constants import *
from .config import *
from errors import *


class wsclient:
    # Constants
    testnet_urls = {
        PerpetualStream: "wss://stream-testnet.bybit.com/v5/public/linear",
        PrivateStream: "wss://stream-testnet.bybit.com/v5/private",
        OrderEntryStream: "wss://stream-testnet.bybit.com/v5/trade"
    }

    def __init__(self, api: str, secret: str) -> None:
        self.api = api
        self.secret = secret
        asyncio.get_event_loop().run_until_complete(self.auth())

    def gen_signature(self, payload, timeStamp, apiKey, secretKey, recvWindow):
        param_str = str(timeStamp) + apiKey + recvWindow + payload
        hash = hmac.new(bytes(secretKey, "utf-8"),
                        param_str.encode("utf-8"), hashlib.sha256)
        signature = hash.hexdigest()
        return signature

    async def auth(self):
        logging.info('Start of auth')
        expires = int((time.time() + 1) * 10000)
        signature = str(hmac.new(bytes(self.secret, "utf-8"),
                                 bytes(f"GET/realtime{expires}", "utf-8"),
                                 digestmod="sha256").hexdigest())

        async with websockets.connect(self.testnet_urls[PrivateStream]) as websocket:
            await websocket.send(json.dumps({
                "op": "auth",
                "args": [self.api, expires, signature]
            })
            )
            response = json.loads(await websocket.recv())
            logging.info(response)
            if not response["success"]:
                raise AuthError()
            print(f"Received: {response}")


logging.basicConfig(level=logging.INFO, filename=TEST_LOG_FILE, filemode="w")
wscl = wsclient('3x4DuwUNYk17nI4cB01', 'T6MovHAoVNbfRMzFhWfHt97YIwlQlolX7vaR')
