from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List
import string
import jsonpickle
import numpy as np
import json
import sys
import json
from typing import Any

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
        lo, hi = 0, min(len(value), max_length)
        out = ""

        while lo <= hi:
            mid = (lo + hi) // 2

            candidate = value[:mid]
            if len(candidate) < len(value):
                candidate += "..."

            encoded_candidate = json.dumps(candidate)

            if len(encoded_candidate) <= max_length:
                out = candidate
                lo = mid + 1
            else:
                hi = mid - 1

        return out


logger = Logger()



class Trader():
    def __init__(self):
        self.POSITION_LIMITS = {
                "CROISSANTS": 250,
                "JAMS": 350,
                "DJEMBES": 60,
                "PICNIC_BASKET1": 60,
                "PICNIC_BASKET2": 100,
                "SQUID_INK" : 50,
                "KELP" : 50,
                "RAINFOREST_RESIN" : 50,
                "VOLCANIC_ROCK": 400,
                "VOLCANIC_ROCK_VOUCHER_9500": 200,
                "VOLCANIC_ROCK_VOUCHER_9750": 200,
                "VOLCANIC_ROCK_VOUCHER_10000" : 200,
                "VOLCANIC_ROCK_VOUCHER_10250":200,
                "VOLCANIC_ROCK_VOUCHER_10500" : 200,
                "MAGNIFICENT_MACARONS" : 75
        }
        self.cl = 50
        self.rp = {
                "CROISSANTS": [],
                "JAMS": [],
                "DJEMBES": [],
                "PICNIC_BASKET1": [],
                "PICNIC_BASKET2": [],
                "SQUID_INK" : [],
                "KELP" : [],
                "RAINFOREST_RESIN" : [],
                "VOLCANIC_ROCK": [],
                "VOLCANIC_ROCK_VOUCHER_9500": [],
                "VOLCANIC_ROCK_VOUCHER_9750": [],
                "VOLCANIC_ROCK_VOUCHER_10000" : [],
                "VOLCANIC_ROCK_VOUCHER_10250":[],
                "VOLCANIC_ROCK_VOUCHER_10500" : [],
                "MAGNIFICENT_MACARONS" : []
        }


        self.position = {
                "CROISSANTS": 0,
                "JAMS": 0,
                "DJEMBES": 0,
                "PICNIC_BASKET1": 0,
                "PICNIC_BASKET2": 0,
                "SQUID_INK" : 0,
                "KELP" : 0,
                "RAINFOREST_RESIN" : 0,
                "VOLCANIC_ROCK": 0,
                "VOLCANIC_ROCK_VOUCHER_9500": 0,
                "VOLCANIC_ROCK_VOUCHER_9750": 0,
                "VOLCANIC_ROCK_VOUCHER_10000" : 0,
                "VOLCANIC_ROCK_VOUCHER_10250":0,
                "VOLCANIC_ROCK_VOUCHER_10500" : 0,
                "MAGNIFICENT_MACARONS" : 0
        }

        self.moving_avg = {
                "CROISSANTS": 0,
                "JAMS": 0,
                "DJEMBES": 0,
                "PICNIC_BASKET1": 0,
                "PICNIC_BASKET2": 0,
                "SQUID_INK" : 0,
                "KELP" : 0,
                "RAINFOREST_RESIN" : 0,
                "VOLCANIC_ROCK": 0,
                "VOLCANIC_ROCK_VOUCHER_9500": 0,
                "VOLCANIC_ROCK_VOUCHER_9750": 0,
                "VOLCANIC_ROCK_VOUCHER_10000" : 0,
                "VOLCANIC_ROCK_VOUCHER_10250":0,
                "VOLCANIC_ROCK_VOUCHER_10500" : 0,
                "MAGNIFICENT_MACARONS" : 0
        }

        self.pnl = {
                "CROISSANTS": 0,
                "JAMS": 0,
                "DJEMBES": 0,
                "PICNIC_BASKET1": 0,
                "PICNIC_BASKET2": 0,
                "SQUID_INK" : 0,
                "KELP" : 0,
                "RAINFOREST_RESIN" : 0,
                "VOLCANIC_ROCK": 0,
                "VOLCANIC_ROCK_VOUCHER_9500": 0,
                "VOLCANIC_ROCK_VOUCHER_9750": 0,
                "VOLCANIC_ROCK_VOUCHER_10000" : 0,
                "VOLCANIC_ROCK_VOUCHER_10250":0,
                "VOLCANIC_ROCK_VOUCHER_10500" : 0,
                "MAGNIFICENT_MACARONS" : 0
        }
        

        self.volatility = {
                "CROISSANTS": 0,
                "JAMS": 0,
                "DJEMBES": 0,
                "PICNIC_BASKET1": 0,
                "PICNIC_BASKET2": 0,
                "SQUID_INK" : 0,
                "KELP" : 0,
                "RAINFOREST_RESIN" : 0,
                "VOLCANIC_ROCK": 0,
                "VOLCANIC_ROCK_VOUCHER_9500": 0,
                "VOLCANIC_ROCK_VOUCHER_9750": 0,
                "VOLCANIC_ROCK_VOUCHER_10000" : 0,
                "VOLCANIC_ROCK_VOUCHER_10250":0,
                "VOLCANIC_ROCK_VOUCHER_10500" : 0,
                "MAGNIFICENT_MACARONS" : 0
        }
        self.max_loss_percent = 0.05 
        
 
        self.consecutive_losses = {
                "CROISSANTS": 0,
                "JAMS": 0,
                "DJEMBES": 0,
                "PICNIC_BASKET1": 0,
                "PICNIC_BASKET2": 0,
                "SQUID_INK" : 0,
                "KELP" : 0,
                "RAINFOREST_RESIN" : 0,
                "VOLCANIC_ROCK": 0,
                "VOLCANIC_ROCK_VOUCHER_9500": 0,
                "VOLCANIC_ROCK_VOUCHER_9750": 0,
                "VOLCANIC_ROCK_VOUCHER_10000" : 0,
                "VOLCANIC_ROCK_VOUCHER_10250":0,
                "VOLCANIC_ROCK_VOUCHER_10500" : 0,
                "MAGNIFICENT_MACARONS" : 0
        }
        

        self.trading_enabled = {
                "CROISSANTS": True,
                "JAMS": True,
                "DJEMBES": True,
                "PICNIC_BASKET1": True,
                "PICNIC_BASKET2": True,
                "SQUID_INK" : True,
                "KELP" : True,
                "RAINFOREST_RESIN" : True,
                "VOLCANIC_ROCK": True,
                "VOLCANIC_ROCK_VOUCHER_9500": True,
                "VOLCANIC_ROCK_VOUCHER_9750": True,
                "VOLCANIC_ROCK_VOUCHER_10000" : True,
                "VOLCANIC_ROCK_VOUCHER_10250": True,
                "VOLCANIC_ROCK_VOUCHER_10500" : True,
                "MAGNIFICENT_MACARONS" : True
        }
        
    
        self.avg_position_price = {
                "CROISSANTS": 0,
                "JAMS": 0,
                "DJEMBES": 0,
                "PICNIC_BASKET1": 0,
                "PICNIC_BASKET2": 0,
                "SQUID_INK" : 0,
                "KELP" : 0,
                "RAINFOREST_RESIN" : 0,
                "VOLCANIC_ROCK": 0,
                "VOLCANIC_ROCK_VOUCHER_9500": 0,
                "VOLCANIC_ROCK_VOUCHER_9750": 0,
                "VOLCANIC_ROCK_VOUCHER_10000" : 0,
                "VOLCANIC_ROCK_VOUCHER_10250":0,
                "VOLCANIC_ROCK_VOUCHER_10500" : 0,
                "MAGNIFICENT_MACARONS" : 0
        }

        

        self.last_price = {
                "CROISSANTS": None,
                "JAMS": None,
                "DJEMBES": None,
                "PICNIC_BASKET1": None,
                "PICNIC_BASKET2": None,
                "SQUID_INK" : None,
                "KELP" : None,
                "RAINFOREST_RESIN" : None,
                "VOLCANIC_ROCK": None,
                "VOLCANIC_ROCK_VOUCHER_9500": None,
                "VOLCANIC_ROCK_VOUCHER_9750": None,
                "VOLCANIC_ROCK_VOUCHER_10000" : None,
                "VOLCANIC_ROCK_VOUCHER_10250": None,
                "VOLCANIC_ROCK_VOUCHER_10500" : None,
                "MAGNIFICENT_MACARONS" : None
        }
    def calculate_volatility(self, product):
        """Calculate the volatility of a product based on recent prices"""
        if len(self.rp[product]) < 5:
            return 0.02  
        
        price_changes = []
        for i in range(1, len(self.rp[product])):
            if self.rp[product][i-1] > 0:  
                pct_change = abs(self.rp[product][i] - self.rp[product][i-1]) / self.rp[product][i-1]
                price_changes.append(pct_change)
        
        if not price_changes:
            return 0.02
            
        
        return max(0.01, np.std(price_changes))
    

    def run(self , state):
        results = {}
        for product  in state.order_depths:
            orders=[]
            order_depth = state.order_depths[product]

            if len(order_depth.buy_orders) > 0 and len(order_depth.sell_orders) > 0:
                buy_vv=  0
                for i in list(order_depth.buy_orders.items()):
                    buy_vv += i[1]
                

                sell_vv = 0
                for i in list(order_depth.sell_orders.items()):
                    sell_vv += -i[1]

                

                best_bid = max(order_depth.buy_orders.keys())
                best_ask = min(order_depth.sell_orders.keys())
                mid_price = (best_bid + best_ask) / 2

            elif len(order_depth.buy_orders) > 0:
                sell_vv = 0
                buy_vv=  0
                for i in list(order_depth.buy_orders.items()):
                    buy_vv += i[1]
                best_bid = max(order_depth.buy_orders.keys())
                mid_price = best_bid
            elif len(order_depth.sell_orders) > 0:
                buy_vv = 0

                sell_vv = 0
                for i in list(order_depth.sell_orders.items()):
                    sell_vv += -i[1]
                best_ask = min(order_depth.sell_orders.keys())
                mid_price = best_ask
            
            if buy_vv + sell_vv != 0:
                order_imb = (sell_vv - buy_vv) / (buy_vv + sell_vv)
            else:
                order_imb = -20


            vol =self.calculate_volatility(product)

            logger.print(self.rp[product])

            if len(self.rp[product]) < self.cl:
                self.rp[product].append(mid_price)
            else:
                self.rp[product].append(mid_price)
                self.rp[product] = self.rp[product][1:]


            
            q=0
            
            if order_imb != -20:
                if order_imb > 1-0.2:

                    orders,q = self.place(product,state,self.position,1)
                if order_imb < -1 +0.2:
                    order,q = self.place(product,state,self.position,-1)
                self.position[product] += q 


            if product == "JAMS":
                orders,q = self.jams_strat(product,state,self.rp[product],self.position)

            if product == "CROISSANTS":
                orders,q = self.crs_strat(product,state,self.rp[product],self.position)

            if product == "PICNIC_BASKET2":
                orders = self.b2(self.rp,order_depth,product,self.position)

            if product == "VOLCANIC_ROCK":
                orders,q = self.volro(product,state)


            if product.startswith("VOLCANIC_ROCK_VOUCHER"):
                orders= self.opt_strat(product,state)

            logger.print(self.position[product])
            if product == "MAGNIFICENT_MACARONS":
                orders = []

            results[product] = orders

        conversions = 1
        traderData = "none"
        logger.flush(state, results, conversions, traderData)
        return results,conversions,traderData
            

    def place(self,product,state,pos,sig):
        order_depth = state.order_depths[product]
        q  = 0
        orders = []
        if sig == 1:
            if len(order_depth.sell_orders) != 0:
                best_ask, best_ask_amount = list(order_depth.sell_orders.items())[0]
                logger.print("BUY", str(-best_ask_amount) + "x", best_ask)
                orders.append(Order(product, best_ask, -best_ask_amount))
                q += -best_ask_amount
    

        else:
            if len(order_depth.buy_orders) != 0:
                best_bid, best_bid_amount = list(order_depth.buy_orders.items())[0]

                logger.print("SELL", str(best_bid_amount) + "x", best_bid)
                orders.append(Order(product, best_bid, -best_bid_amount))
                q -= best_bid_amount
        return orders , q



    def b2(self,rp,order_depth,product,position):
        orders= []
        forcast_jams = self.ewma_jams(rp["JAMS"],0.5)
        forecast_cr = self.ewma(rp["CROISSANTS"],0.3,1,True) + rp["CROISSANTS"][-1]
        forecast= 0.6 * forcast_jams* 2  + 0.4 * forecast_cr* 4 
        buy_orders = sorted(order_depth.buy_orders.items(), key=lambda x: x[0], reverse=True)  # Highest buy first
        sell_orders = sorted(order_depth.sell_orders.items(), key=lambda x: x[0])
        position_limit = self.POSITION_LIMITS.get(product, 10)
        price = rp["PICNIC_BASKET2"]
        buy_capacity = position_limit - position[product]
        sell_capacity = position_limit + position[product]
        for price, volume in sell_orders:
            if forecast > price:
                buy_volume = min(abs(volume), buy_capacity)
                if buy_volume > 0:
                    orders.append(Order(product,int(price),buy_volume))
                    buy_capacity -= buy_volume
        for price,volume in buy_orders:
            if forecast < price:
                sell_volume = min(volume, sell_capacity)
                if sell_volume > 0:
                    orders.append(Order(product, int(price)   , -sell_volume))
                    sell_capacity -= sell_volume
        return orders

    def execute_long_butt(self,state,order_depth):
            orders = []
            if len(order_depth.buy_orders) > 0 and len(order_depth.sell_orders) > 0:
                buy_vv=  0
                for i in list(order_depth.buy_orders.items()):
                    buy_vv += i[1]
                

                sell_vv = 0
                for i in list(order_depth.sell_orders.items()):
                    sell_vv += -i[1]

                

                best_bid = max(order_depth.buy_orders.keys())
                best_ask = min(order_depth.sell_orders.keys())
                mid_price = (best_bid + best_ask) / 2

            elif len(order_depth.buy_orders) > 0:
                sell_vv = 0
                buy_vv=  0
                for i in list(order_depth.buy_orders.items()):
                    buy_vv += i[1]
                best_bid = max(order_depth.buy_orders.keys())
                mid_price = best_bid
            elif len(order_depth.sell_orders) > 0:
                buy_vv = 0

                sell_vv = 0
                for i in list(order_depth.sell_orders.items()):
                    sell_vv += -i[1]
                best_ask = min(order_depth.sell_orders.keys())
                mid_price = best_ask

            

            strikes = [9500,9700,10000,10250,10500]
            sm = -1
            bn = -1
            for idx,i in enumerate(strikes):
                if i > mid_price:
                    if i == 9500 or i == 9700:
                        sm = -1
                        bn = -1
                        break
                    sm = strikes[idx-2]
                    bn = strikes[idx-1]
                    break
            if sm == -1 or bn == -1 or bn == 10500:
                return []
            logger.print(sm,bn)
            try:
                best_ask = min(state.order_depths["VOLCANIC_ROCK_VOUCHER_"+str(sm)].sell_orders.keys())
                orders.append(Order("VOLCANIC_ROCK_VOUCHER_"+str(sm),best_ask,1))
                best_bids = max(state.order_depths["VOLCANIC_ROCK_VOUCHER_"+str(bn)].buy_orders.keys())
                orders.append(Order("VOLCANIC_ROCK_VOUCHER_"+str(bn),best_bids,-2))

                best_ask = max(state.order_depths["VOLCANIC_ROCK_VOUCHER_"+str(strikes[strikes.index(bn)+1])].buy_orders.keys())
                orders.append(Order("VOLCANIC_ROCK_VOUCHER_"+str(strikes[strikes.index(bn)+1]),best_ask,1))

            except Exception as e:
                orders  = []
            return orders








    def opt_strat(self,product,state):

        orders=[]
        order_depth = state.order_depths["VOLCANIC_ROCK"]
        num_sell_orders = len(order_depth.sell_orders)
        num_buy_orders = len(order_depth.buy_orders)

        if abs(num_sell_orders-num_buy_orders) < 0.01:
            orders=self.execute_long_butt(state,order_depth)
        return orders

    def ewma(self ,prices: list[float], alpha: float = 0.5 , mode=1, d=False) -> float:
        if mode == 2:
            new_prices= [0]
            

            for i in range(1,len(prices)):
                new_prices.append(prices[i] - prices[i-1])
            if d == False:
                new_prices = prices

            ewma_value = new_prices[0]
            for price in new_prices[1:]:
                ewma_value = alpha * price + (1 - alpha) * ewma_value

            return ewma_value
        else:
            new_prices= [0]
            for i in range(1,len(prices)):
                new_prices.append(prices[i] - prices[i-1])

            if d == False:
                new_prices = prices
            



            ewma_value = [new_prices[0]]
            varpp = 0
            for price in new_prices[1:]:
                espc = 0
                for i in range(len(ewma_value)):
                    espc += (new_prices[i+1] - ewma_value[i]) ** 2
                espc = espc / len(ewma_value)
                espp= 0
                for i in range(len(ewma_value)):
                    espp += (new_prices[i+1] - ewma_value[i]) 
                espp = (espp/ len(ewma_value)) ** 2
                varpp = espc  - espp
                alpha = 1/ (1+np.exp(-0.2*varpp))
                ewma_value.append(alpha * price + (1 - alpha) * ewma_value[-1])
            #print(ewma_value)
            #print(varpp)
            return ewma_value[-1]
    def ewma_jams(self ,prices, alpha = 0.5) :
        new_prices= [0]
        for i in range(1,len(prices)):
            new_prices.append(prices[i] - prices[i-1])

        ewma_value = prices[0]
        for price in prices[1:]:
            ewma_value = alpha * price + (1 - alpha) * ewma_value
        return ewma_value
    

    def jams_strat(self,product,state,prices,pos):
        forecast = self.ewma_jams(prices,0.7)
        if forecast > prices[-1]:
            orders,q=self.place(product,state,pos,1)
        else:
            orders,q=self.place(product,state,pos,-1)
        return orders,q


    def crs_strat(self,product,state,prices,pos):
        forecast = self.ewma(prices,0.3,1,True) + prices[-1]
        if forecast > prices[-1]*0.02:
            orders,q=self.place(product,state,pos,1)
        else:
            orders,q=self.place(product,state,pos,-1)
        return orders,q

    def volro(self,product,state):
        forecast = self.ewma_jams(self.rp[product],0.7)
        pos  = self.position[product]
        prices  = self.rp[product]
        if forecast > prices[-1]*0.02:
            orders,q=self.place(product,state,pos,-1)
        else:
            orders,q=self.place(product,state,pos,1)
        return orders,q