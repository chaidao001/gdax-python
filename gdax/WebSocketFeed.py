import json

import websocket


class GdaxWebSocketFeed:
    def __init__(self, url='wss://ws-feed.gdax.com', product_ids=None, channels=None):
        if channels is None:
            self._channels = [
                'level2'
            ]
        if product_ids is None:
            self._product_ids = [
                'BTC-USD'
            ]

        self._url = url
        self._ws = None
        self._price_ladders = None
        self._running = True

    def _subscribe(self):
        message = {
            "type": "subscribe",
            "product_ids": self._product_ids,
            "channels": self._channels
        }
        self._ws.send(json.dumps(message))

    def _unsubscribe(self):
        message = {
            "type": "unsubscribe",
            "product_ids": self._product_ids,
            "channels": self._channels
        }
        self._ws.send(json.dumps(message))

    def _authenticate(self):
        pass

    def _process_message(self, message: dict):
        type = message['type']

        if type == 'subscriptions':
            channels = message['channels']

            if channels:
                print("Subscribed")
            else:
                print("Unsubscribed")
                self._running = False
        elif type == 'snapshot':
            self._price_ladders = PriceLadders(message)
        elif type == 'l2update':
            self._price_ladders.update(message['changes'])
        else:
            print(message)

    def _listen(self):
        try:
            received_message = self._ws.recv()
            self._process_message(json.loads(received_message))
        except KeyboardInterrupt:
            print("Interrupted")
            self._unsubscribe()

    def start(self):
        self._ws = websocket.create_connection(self._url)

        self._subscribe()
        self._authenticate()

        while self._running:
            self._listen()


class PriceLadders:
    def __init__(self, snapshot: dict):
        self._price_ladders = {
            'buy': PriceLadder(snapshot['bids']),
            'sell': PriceLadder(snapshot['asks'])
        }

    def update(self, changes: list):
        for change in changes:
            side, price, size = change
            self._price_ladders[side].update(float(price), float(size))


class PriceLadder:
    def __init__(self, price_sizes: list):
        self._price_sizes = {float(price): float(size) for price, size in price_sizes}

    def update(self, price: float, size: float):
        if size == 0:
            # price fully matched.  remove from ladder
            del self._price_sizes[price]
        else:
            self._price_sizes[price] = size

if __name__ == "__main__":
    gdax = GdaxWebSocketFeed()
    gdax.start()
