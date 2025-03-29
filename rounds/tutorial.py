import json
from typing import Any
import numpy as np
from datamodel import Listing, Observation, Order, OrderDepth, ProsperityEncoder, Symbol, Trade, TradingState

class Logger:
    def __init__(self) -> None:
        self.logs = ""
        self.max_log_length = 3750

    def print(self, *objects: Any, sep: str = " ", end: str = "\n") -> None:
        self.logs += sep.join(map(str, objects)) + end

    def flush(self, state: TradingState, orders: dict[Symbol, list[Order]], conversions: int, trader_data: str) -> None:
        base_length = len(
            self.to_json(
                [
                    self.compress_state(state, ""),
                    self.compress_orders(orders),
                    conversions,
                    "",
                    "",
                ]
            )
        )

        # We truncate state.traderData, trader_data, and self.logs to the same max. length to fit the log limit
        max_item_length = (self.max_log_length - base_length) // 3

        print(
            self.to_json(
                [
                    self.compress_state(state, self.truncate(state.traderData, max_item_length)),
                    self.compress_orders(orders),
                    conversions,
                    self.truncate(trader_data, max_item_length),
                    self.truncate(self.logs, max_item_length),
                ]
            )
        )

        self.logs = ""

    def compress_state(self, state: TradingState, trader_data: str) -> list[Any]:
        return [
            state.timestamp,
            trader_data,
            self.compress_listings(state.listings),
            self.compress_order_depths(state.order_depths),
            self.compress_trades(state.own_trades),
            self.compress_trades(state.market_trades),
            state.position,
            self.compress_observations(state.observations),
        ]

    def compress_listings(self, listings: dict[Symbol, Listing]) -> list[list[Any]]:
        compressed = []
        for listing in listings.values():
            compressed.append([listing.symbol, listing.product, listing.denomination])

        return compressed

    def compress_order_depths(self, order_depths: dict[Symbol, OrderDepth]) -> dict[Symbol, list[Any]]:
        compressed = {}
        for symbol, order_depth in order_depths.items():
            compressed[symbol] = [order_depth.buy_orders, order_depth.sell_orders]

        return compressed

    def compress_trades(self, trades: dict[Symbol, list[Trade]]) -> list[list[Any]]:
        compressed = []
        for arr in trades.values():
            for trade in arr:
                compressed.append(
                    [
                        trade.symbol,
                        trade.price,
                        trade.quantity,
                        trade.buyer,
                        trade.seller,
                        trade.timestamp,
                    ]
                )

        return compressed

    def compress_observations(self, observations: Observation) -> list[Any]:
        conversion_observations = {}
        for product, observation in observations.conversionObservations.items():
            conversion_observations[product] = [
                observation.bidPrice,
                observation.askPrice,
                observation.transportFees,
                observation.exportTariff,
                observation.importTariff,
                observation.sugarPrice,
                observation.sunlightIndex,
            ]

        return [observations.plainValueObservations, conversion_observations]

    def compress_orders(self, orders: dict[Symbol, list[Order]]) -> list[list[Any]]:
        compressed = []
        for arr in orders.values():
            for order in arr:
                compressed.append([order.symbol, order.price, order.quantity])

        return compressed

    def to_json(self, value: Any) -> str:
        return json.dumps(value, cls=ProsperityEncoder, separators=(",", ":"))

    def truncate(self, value: str, max_length: int) -> str:
        if len(value) <= max_length:
            return value

        return value[: max_length - 3] + "..."

logger = Logger()

class Product:
    def __init__(self, limit: int = 0, id: str = "") -> None:
        # Position limit for the product
        self.limit = limit
        # Current position of the product
        self.position = 0
        # Product ID for dictionary lookup
        self.id = id

    def update(self, state: TradingState) -> None:
        # Update the position based on the state
        if self.id not in state.position:
            self.position = 0
        else:
            self.position = state.position[self.id]
        # Placeholder for any other updates needed

    def trade(self, state: TradingState) -> list[Order]:
        # Placeholder for the trade logic, returns an empty list of orders
        return []
    
class RainforestResin(Product):
    def __init__(self) -> None:
        super().__init__(limit=50, id="RAINFOREST_RESIN")

    def trade(self, state: TradingState) -> list[Order]:
        self.update(state)
        orders: list[Order] = []
        order_depth: OrderDepth = state.order_depths[self.id]
        
        # Observed fair price of 10,000
        fair_price = 10000
        # Alternative method of finding fair price, taking the mean of the highest and lowest sells/buys
        # fair_price = (max(order_depth.sell_orders.keys()) + min(order_depth.buy_orders.keys())) / 2

        if len(order_depth.sell_orders) != 0:
            # Select sell order with the lowest price
            best_ask = min(order_depth.sell_orders.keys())
            best_ask_volume = -1 * order_depth.sell_orders[best_ask]

            if best_ask < fair_price:
                quantity = min(best_ask_volume, self.limit - self.position)
                logger.print(f"Buying {quantity} {self.id} @ {best_ask}")
                orders.append(Order(self.id, best_ask, quantity))
            
        if len(order_depth.buy_orders) != 0:
            # Select buy order with the highest bid
            best_bid = max(order_depth.buy_orders.keys())
            best_bid_volume = order_depth.buy_orders[best_bid]

            if best_bid > fair_price:
                quantity = min(best_bid_volume, self.limit + self.position)
                logger.print(f"Selling {quantity} {self.id} @ {best_bid}")
                orders.append(Order(self.id, best_bid, -quantity))
        
        return orders

class Kelp(Product):
    def __init__(self) -> None:
        super().__init__(limit=50, id="KELP")

    def trade(self, state: TradingState) -> list[Order]:
        self.update(state)
        orders: list[Order] = []

        return orders
    

class Trader:
    products = {
        "RAINFOREST_RESIN": RainforestResin(),
        "KELP": Kelp(),
    }

    def run(self, state: TradingState) -> tuple[dict[Symbol, list[Order]], int, str]:
        result = {}
        
        for product in state.order_depths.keys():
            logger.print(f"Processing product: {product}")
            if product in self.products:
                result[product] = self.products[product].trade(state)
        
        conversions = 1
        trader_data = ""

        logger.flush(state, result, conversions, trader_data)
        return result, conversions, trader_data
