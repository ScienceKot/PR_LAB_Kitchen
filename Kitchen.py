import json
from concurrent import futures
import time

class Kitchen:
    def __init__(self, cooks, n_ovens, n_stoves, menu_path):
        for i in range(len(cooks)):
            cook = cooks[i]
            cooks[i] = Cook(
                cook_id = cook['id'],
                rank=cook['rank'],
                proficiency=cook['proficiency'],
                name=cook['name'],
                catch_phrase=cook['catch_phrase']
            )
        self.cooks = cooks
        self.n_ovens = n_ovens
        self.n_stoves = n_stoves
        self.menu = json.load(open(menu_path, 'r'))
        self.order_list = []
        self.compute_workers()
        self.executed_orders = []
        self.n_cooks = sum(self.ranks_foods)

    def compute_workers(self):
        self.ranks_foods = [0, 0, 0]
        for cook in self.cooks:
            self.ranks_foods[cook.rank-1] += cook.proficiency

    def cooking(self, food_id):
        time.sleep(self.menu[food_id-1]['preparation-time'])

    def prepare_food(self, order):
        cooking_time = 0
        with futures.ThreadPoolExecutor(self.n_cooks) as executor:
            to_do = []
            for food in order['items']:
                for menu_item in self.menu:
                    if menu_item['id'] == food:
                        preparation_time = menu_item['preparation-time']
                        cooking_time += preparation_time
                future = executor.submit(self.cooking, food)
                to_do.append(future)
            for future in futures.as_completed(to_do):
                _ = future.result()
        cook_dish_pairs = []
        for dish_id in order['items']:
            for dish in self.menu:
                if dish['id'] == dish_id:
                    for cook in self.cooks:
                        if cook.proficiency >= dish['complexity']:
                            cook_dish_pairs.append((cook.id, dish['id']))
        to_add = {
            "cooking_time" : cooking_time,
            "cooking_details" : [{"food_id" : pair[1], "cook_id" : pair[0]} for pair in cook_dish_pairs]
        }
        for key in to_add:
            order[key] = to_add[key]
        return order

class Cook:
    def __init__(self, cook_id, rank, proficiency, name, catch_phrase):
        self.id = cook_id
        self.rank = rank
        self.proficiency = proficiency
        self.name = name
        self.catch_phrase = catch_phrase
