from concurrent import futures
from random import randint
import json
import time
import datetime

import requests


class DinningHall:
    def __init__(self, n_tables, n_waiters, max_no_of_items_per_order, menu_file_path):
        self.n_tables = n_tables
        self.n_waiters = n_waiters
        self.tables = []
        for i in range(self.n_tables):
            self.tables.append(
                Table(i, 'free', menu_file_path)
            )
        self.waiters = Waiters(self.n_waiters)
        self.current_order_id = 0
        self.max_no_of_items_per_order = max_no_of_items_per_order

    def distrubute_order(self, order):
        waiter_id = order['waiter_id']
        table_id = order['table_id']
        self.tables[table_id] = 'free'
        self.waiters.waiters[waiter_id]['status'] = 'free'
        now = datetime.datetime.now()
        now = time.mktime(now.timetuple())*1e3
        elasted_time = now - order['pick_up_time']
        return elasted_time

    def generate_orders(self, n_orders):
        for i in range(n_orders):
            self.waiters.take_order(self.tables, i, self.max_no_of_items_per_order)

class Table:
    def __init__(self, table_id, state, menu_file_path):
        self.table_id = table_id
        self.allowed_states = ['free', 'waiting_to_make_a_order', 'waiting_the_order']
        if state not in self.allowed_states:
            raise ValueError(f"{state} is not an allowed table status")
        else:
            self.state = state
        self.max_dish_index = 10
        self.min_priority = 1
        self.max_priority = 5
        self.menu = json.load(open(menu_file_path, 'r'))

    def __setattr__(self, key, value):
        if key == 'state':
            if value in self.allowed_states:
                self.__dict__[key] = value
            else:
                raise ValueError(f"{value} is not an allowed table status")
        else:
            self.__dict__[key] = value

    def generate_order(self, order_id, waiter_id, max_no_of_items):
        items = [randint(0, 9) for _ in range(randint(1, max_no_of_items))]
        priority = randint(self.min_priority, self.max_priority)
        max_wait = max([self.menu[i]['preparation-time'] for i in items]) * 1.3
        now = datetime.datetime.now()
        return {
            "order_id" : order_id,
            "table_id" : self.table_id,
            "waiter_id" : waiter_id,
            "items" : items,
            "priority" : priority,
            "max_wait" : int(max_wait),
            "pick_up_time": time.mktime(now.timetuple())*1e3
        }

class Waiters:
    def __init__(self, n_waiters):
        self.waiters = [{"waiter_id" : i, "status" : "free"} for i in range(n_waiters)]
        self.order_list = []

    @property
    def no_of_free_waiters(self):
        return len([waiter['waiter_id'] for waiter in self.waiters
             if waiter['status'] == 'free'])

    def send_order(self, order):
        time.sleep(order['time_await'])
        del order['time_await']
        requests.post('http://172.31.96.44:2000/order', json=order)

    def take_order(self, tables_list, order_id, item_no):
        for i in range(len(tables_list)):
            if tables_list[i].state == 'free':
                if self.no_of_free_waiters > 0:
                    first_free_waiter_index = min([waiter['waiter_id'] for waiter in self.waiters
                                                   if waiter['status'] == 'free'])
                    self.waiters[first_free_waiter_index]['status'] == 'not_free'
                    tables_list[i].state = 'waiting_the_order'
                    order = tables_list[i].generate_order(order_id, waiter_id=first_free_waiter_index, max_no_of_items=item_no)
                    order['time_await'] = randint(1, 3)
                    self.order_list.append(order)
                    break