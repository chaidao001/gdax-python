from unittest import TestCase

from gdax.WebSocketFeed import PriceLadder


class TestConfig(TestCase):
    def setUp(self):
        price_sizes = [['5.0', '100'], ['12.5', '2.123'], ['1.2', '0.2']]
        self.buy_ladder = PriceLadder('buy', price_sizes)
        self.sell_ladder = PriceLadder('sell', price_sizes)

    def test_init_first_price_is_min_for_buy(self):
        self.assertEqual(self.buy_ladder._prices[0], 1.2)

    def test_init_first_price_is_max_for_sell(self):
        self.assertEqual(self.sell_ladder._prices[0], 12.5)

    def test_update_remove_existing_price_when_size_is_zero(self):
        self.buy_ladder.update(5.0, 0)

        self.assertFalse(5.0 in self.buy_ladder._prices)
        self.assertFalse(5.0 in self.buy_ladder._price_sizes)

    def test_update_do_nothing_when_size_is_zero_and_price_not_in_ladder(self):
        self.buy_ladder.update(15.0, 0)

        self.assertFalse(15.0 in self.buy_ladder._prices)
        self.assertFalse(15.0 in self.buy_ladder._price_sizes)

    def test_update_update_price_when_price_in_ladder_and_size_not_zero(self):
        self.buy_ladder.update(12.5, 100)

        self.assertTrue(12.5 in self.buy_ladder._prices)
        self.assertEqual(self.buy_ladder._price_sizes[12.5], 100)

    def test_update_remove_min_price_when_new_price_higher_than_min_for_buy(self):
        self.buy_ladder.update(1.3, 100)

        self.assertTrue(1.3 in self.buy_ladder._prices)
        self.assertEqual(self.buy_ladder._price_sizes[1.3], 100)
        self.assertFalse(1.2 in self.buy_ladder._prices)
        self.assertFalse(1.2 in self.buy_ladder._price_sizes)

    def test_update_do_nothing_when_new_price_lower_than_min_for_buy(self):
        self.buy_ladder.update(1.1, 100)

        self.assertFalse(1.1 in self.buy_ladder._prices)
        self.assertFalse(1.1 in self.buy_ladder._price_sizes)
        self.assertTrue(1.2 in self.buy_ladder._prices)
        self.assertEqual(self.buy_ladder._price_sizes[1.2], 0.2)

    def test_update_remove_max_price_when_new_price_lower_than_max_for_sell(self):
        self.sell_ladder.update(10, 1)

        self.assertTrue(10 in self.sell_ladder._prices)
        self.assertEqual(self.sell_ladder._price_sizes[10], 1)
        self.assertFalse(12.5 in self.sell_ladder._prices)
        self.assertFalse(12.5 in self.sell_ladder._price_sizes)

    def test_update_do_nothing_when_new_price_higher_than_max_for_sell(self):
        self.sell_ladder.update(100, 1)

        self.assertFalse(100 in self.sell_ladder._prices)
        self.assertFalse(100 in self.sell_ladder._price_sizes)
        self.assertTrue(12.5 in self.sell_ladder._prices)
        self.assertEqual(self.sell_ladder._price_sizes[12.5], 2.123)
