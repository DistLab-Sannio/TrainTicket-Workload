import random
import time
from locust import FastHttpUser, task, between, events
import locust.stats

import api_user
import api_admin
import utils
import config

locust.stats.PERCENTILES_TO_REPORT = config.PERCENTILES_TO_REPORT

count = 0

test_log = open('test_log.csv', 'w')
test_log.write(f'request_type;name;response_time;error;start_time;url\n')

log_flush_timer = time.time()


@events.request.add_listener
def my_request_handler(request_type, name, response_time, response_length, response,
                       context, exception, start_time, url, **kwargs):
    global log_flush_timer

    if config.LOG_ALL_REQUESTS:
        test_log.write(f'{request_type};{name};{response_time};{1 if exception else 0};{start_time};{url}\n')
        t = time.time()
        if t - log_flush_timer > config.LOG_FLUSH_INTERVAL:
            log_flush_timer = t
            test_log.flush()

    if config.STOP_ON_REQUEST_COUNT:
        global count
        count += 1
        if count > config.REQUEST_NUMBER_TO_STOP:
            test_log.flush()
            exit(0)


def choice_train_type() -> bool:
    return random.choices([True, False], weights=[config.HS_PERCENTAGE, config.OTHER_PERCENTAGE], k=1)[0]


class External(FastHttpUser):
    wait_time = between(config.TT_USER_MIN, config.TT_USER_MAX)
    network_timeout = config.NETWORK_TIMEOUT
    connection_timeout = config.CONNECTION_TIMEOUT
    weight = config.EXTERNAL_PERCENTAGE
    hs = choice_train_type()

    def on_start(self):
        api_user.home(self.client)

    @task(config.BEHAVIOR_PROBABILITY)
    def external_search_roundtrip_hs(self):
        utils.search_travels_roudtrip(self.client, self.hs)

    @task(config.BEHAVIOR_PROBABILITY)
    def external_search_oneway_hs(self):
        utils.search_travels_oneway(self.client, self.hs)

    @task(config.BEHAVIOR_PROBABILITY)
    def get_travel_plan(self):
        start, end = utils.get_random_start_end_stations(self.hs)
        api_user.get_travel_plan(self.client, start, end)

    @task(config.RESET_PROBABILITY)
    def reset_cookie(self):
        self.client.cookiejar.clear()
        api_user.home(self.client)
        self.hs = choice_train_type()


class Logged(FastHttpUser):
    wait_time = between(config.TT_USER_MIN, config.TT_USER_MAX)
    network_timeout = config.NETWORK_TIMEOUT
    connection_timeout = config.CONNECTION_TIMEOUT
    weight = config.LOGGED_PERCENTAGE
    hs = choice_train_type()
    user_id = None
    headers = None

    def on_start(self):
        user_id, headers = utils.perform_login_user(self.client)
        self.user_id = user_id
        self.headers = headers

    @task(config.BEHAVIOR_PROBABILITY)
    def user_search_and_preserve_roundtrip(self):
        start, end = utils.get_random_start_end_stations(hs=self.hs)
        start, end = utils.search_and_preserve_travel(self.client, self.user_id, self.headers, self.hs, start, end)
        utils.sleep_user()
        try:
            utils.search_and_preserve_travel(self.client, self.user_id, self.headers, self.hs, end, start)
        except IndexError:
            pass

    @task(config.BEHAVIOR_PROBABILITY)
    def user_search_and_preserve_oneway(self):
        start, end = utils.get_random_start_end_stations(hs=self.hs)
        utils.search_and_preserve_travel(self.client, self.user_id, self.headers, self.hs, start, end)

    @task(int(config.BEHAVIOR_PROBABILITY / 5))
    def delete_ticket(self):
        api_user.get_all_orders(self.client, self.user_id, self.hs, self.headers)
        utils.sleep_user()
        api_user.cancel(self.client, self.user_id, self.hs, self.headers)

    @task(config.BEHAVIOR_PROBABILITY)
    def get_travel_plan(self):
        start, end = utils.get_random_start_end_stations(self.hs)
        api_user.get_travel_plan(self.client, start, end)

    @task(int(config.BEHAVIOR_PROBABILITY / 5))
    def collect_and_execute_ticket(self):
        orders_hs = api_user.get_all_orders(self.client, self.user_id, hs=True, headers=self.headers)
        orders_other = api_user.get_all_orders(self.client, self.user_id, hs=False, headers=self.headers)
        utils.sleep_user()
        orders = orders_hs + orders_other
        for o in orders:
            if o["status"] == 1:
                api_user.collect_ticket(self.client, self.headers, o)
                break
        utils.sleep_user()
        orders_hs = api_user.get_all_orders(self.client, self.user_id, hs=True, headers=self.headers)
        orders_other = api_user.get_all_orders(self.client, self.user_id, hs=False, headers=self.headers)
        utils.sleep_user()
        orders = orders_hs + orders_other
        for o in orders:
            if o["status"] == 2:
                api_user.execute_ticket(self.client, self.headers, o)
                break

    @task(config.RESET_PROBABILITY)
    def reset_cookie(self):
        self.client.cookiejar.clear()
        user_id, headers = utils.perform_login_user(self.client)
        self.user_id = user_id
        self.headers = headers
        self.hs = choice_train_type()


class Admin(FastHttpUser):
    wait_time = between(config.TT_USER_MIN, config.TT_USER_MAX)
    network_timeout = 120.0
    connection_timeout = 120.0
    weight = config.ADMIN_PERCENTAGE
    user_id = None
    headers = None
    orders = None

    def on_start(self):
        user_id, headers, orders = utils.perform_login_admin(self.client)
        self.user_id = user_id
        self.headers = headers
        self.orders = orders

    @task(config.BEHAVIOR_PROBABILITY)
    def admin_create_travel(self):
        routes = api_admin.get_all_routes(self.client, headers=self.headers)["data"]
        route = random.choice(routes)
        utils.sleep_user()
        travels = api_admin.get_all_travels(self.client, headers=self.headers)["data"]
        utils.sleep_user()
        api_admin.create_travel(self.client, route, hs=random.choice([True, False]), headers=self.headers)

    @task(config.BEHAVIOR_PROBABILITY)
    def admin_modify_travel(self):
        travels = api_admin.get_all_travels(self.client, headers=self.headers)["data"]
        utils.sleep_user()
        travel = random.choice(travels)
        api_admin.update_travel(self.client, travel, headers=self.headers)

    # @task(int(config.BEHAVIOR_PROBABILITY / 5))
    # def admin_delete_travel(self):
    #     travels = api_admin.get_all_travels(self.client, headers=self.headers)["data"]
    #     utils.sleep_user()
    #     api_admin.delete_random_travel(self.client, travels, hs=random.choice([True, False]), headers=self.headers)

    @task(config.BEHAVIOR_PROBABILITY)
    def admin_update_order(self):
        order = random.choice(self.orders['data'])
        utils.sleep_user()
        api_admin.update_order(self.client, order, headers=self.headers)

    @task(config.BEHAVIOR_PROBABILITY)
    def admin_crate_order(self):
        api_admin.create_order(self.client, hs=random.choice([True, False]), headers=self.headers)

    @task(config.BEHAVIOR_PROBABILITY)
    def admin_modify_price(self):
        prices = api_admin.get_all_prices(self.client, headers=self.headers)
        price = random.choice(prices['data'])
        utils.sleep_user()
        api_admin.modify_price(self.client, headers=self.headers, price=price)

    @task(config.BEHAVIOR_PROBABILITY)
    def admin_modify_contact(self):
        contacts = api_admin.get_all_contacts(self.client, headers=self.headers)
        contact = random.choice(contacts['data'])
        utils.sleep_user()
        api_admin.modify_contact(self.client, headers=self.headers, contact=contact)

    @task(config.BEHAVIOR_PROBABILITY)
    def admin_add_user(self):
        api_admin.get_all_users(self.client, self.headers)
        utils.sleep_user()
        api_admin.create_random_user(self.client, self.headers)

    # @task(int(config.BEHAVIOR_PROBABILITY / 5))
    # def admin_delete_order(self):
    #     api_admin.delete_random_order(self.client, self.orders, hs=True)

    @task(config.RESET_PROBABILITY)
    def reset_cookie(self):
        self.client.cookiejar.clear()
        user_id, headers, orders = utils.perform_login_admin(self.client)
        self.user_id = user_id
        self.headers = headers
        self.orders = orders
