import heapq
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
        except:
            self._unsubscribe()

    def start(self):
        self._ws = websocket.create_connection(self._url)

        self._subscribe()
        self._authenticate()

        while self._running:
            self._listen()


class PriceLadders:
    def __init__(self, snapshot: dict, level=10):
        self._level = level
        self._price_ladders = {
            'buy': PriceLadder('buy', snapshot['bids'][:self._level]),
            'sell': PriceLadder('sell', snapshot['asks'][:self._level])
        }

    def update(self, changes: list):
        for change in changes:
            side, price, size = change

            self._price_ladders[side].update(float(price), float(size))


class PriceLadder:
    def __init__(self, side: str, price_sizes: list):
        self._side = side
        self._prices = [float(price) for price, _ in price_sizes]
        self._price_sizes = {float(price): float(size) for price, size in price_sizes}

        if self._side == 'buy':
            # used to find the min price
            heapq.heapify(self._prices)
        elif self._side == 'sell':
            # used to find the max price
            heapq._heapify_max(self._prices)
        else:
            raise Exception("Unknown side {}" % self._side)

    def update(self, price: float, size: float):
        if size == 0:
            # matched.  remove from ladder
            if price not in self._price_sizes:
                return

            self._prices.remove(price)
            del self._price_sizes[price]
        elif price in self._price_sizes:
            # update on existing prices
            self._price_sizes[price] = size
        else:
            # new price
            removed_price = None
            if self._side == 'buy':
                # keep the largest prices and pop the smallest
                if price > self._prices[0]:
                    removed_price = heapq.heapreplace(self._prices, price)
            else:
                # keep the smallest prices and pop the largest
                if price < self._prices[0]:
                    removed_price = heapq._heapreplace_max(self._prices, price)

            if removed_price:
                del self._price_sizes[removed_price]
                self._price_sizes[price] = size


if __name__ == "__main__":
    gdax = GdaxWebSocketFeed()
    gdax.start()
