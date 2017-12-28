import heapq
import json

import websocket


class GdaxWebSocketFeed():
    def __init__(self, url='wss://ws-feed.gdax.com'):
        self._url = url
        self._ws = None
        self._price_ladders = None

    def _subscribe(self):
        self._ws = websocket.create_connection(self._url)

        message = {
            "type": "subscribe",
            "product_ids": [
                # "BTC-USD",
                "BTC-EUR"
            ],
            "channels": [
                "heartbeat",
                "level2"
            ]
        }

        self._ws.send(json.dumps(message))

    def _unsubscribe(self):
        pass

    def _authenticate(self):
        pass

    def _process_message(self, message: dict):
        type = message['type']

        if type == 'subscriptions':
            print("Subscribed")
        elif type == 'snapshot':
            self._price_ladders = self.PriceLadders(message)
            pass
        elif type == 'l2update':
            pass
        elif type == 'heartbeat':
            pass
        else:
            print(type)

    def _listen(self):
        try:
            received_message = self._ws.recv()
            self._process_message(json.loads(received_message))
        except:
            pass

    def start(self):
        self._subscribe()
        self._authenticate()
        self._unsubscribe()
        while True:
            self._listen()

    class PriceLadders:
        def __init__(self, snapshot: dict, level=10):
            self._level = level
            self._price_ladders = {
                'bids': self._price_size_lists_to_tuples(snapshot['bids'][:self._level]),
                'asks': self._price_size_lists_to_tuples(snapshot['asks'][:self._level])
            }

            heapq._heapify_max(self._price_ladders['bids'])
            heapq.heapify(self._price_ladders['asks'])

        def _price_size_lists_to_tuples(self, price_size_list):
            return [(float(price), float(size)) for price, size in price_size_list]

    class PriceVol:
        def __init__(self, price_vol: list):
            self._price = price_vol[0]
            self._size = price_vol[1]


if __name__ == "__main__":
    gdax = GdaxWebSocketFeed()

    gdax.start()
