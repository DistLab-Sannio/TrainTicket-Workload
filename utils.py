import json
import random
import time

import api_user
import string
import api_admin
from datetime import datetime, timedelta
from locust import events
import config

spawning_complete = False


def get_random_string(length=10):
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str


@events.spawning_complete.add_listener
def on_spawning_complete(user_count, **kwargs):
    global spawning_complete
    spawning_complete = True


def get_json_from_response(response):
    try:
        response_as_text = response.content.decode('UTF-8')
        response_as_json = json.loads(response_as_text)
        return response_as_json
    except:
        return None


def next_weekday(d, weekday):
    days_ahead = weekday - d.weekday()
    if days_ahead <= 0:
        days_ahead += 7
    return d + timedelta(days_ahead)


def get_name_suffix(name):
    global spawning_complete

    if config.ADD_SPAWNING_SUFFIX and not spawning_complete:
        name = name + "_spawning"

    if config.LOG_STATISTICS_IN_HALF_MINUTE_CHUNKS:
        now = datetime.now()
        now = datetime(now.year, now.month, now.day, now.hour, now.minute, 0 if now.second < 30 else 30, 0)
        now_as_timestamp = int(now.timestamp())
        return f"{name}@{now_as_timestamp}"
    else:
        return name


def get_departure_date():
    tomorrow = datetime.now() + timedelta(1)
    next_monday = next_weekday(tomorrow, 0)
    departure_date = next_monday.strftime("%Y-%m-%d")
    return departure_date


def get_random_start_end_stations(hs=True):
    if hs:
        route = random.choice(config.HS_TRIP_LIST)
    else:
        route = random.choice(config.OTHER_TRIP_LIST)
    index = random.randint(0, len(route) - 2)
    start = route[index]
    end = route[random.randint(index + 1, len(route) - 1)]
    return start, end


def sleep_user():
    time.sleep(random.uniform(config.TT_USER_MIN, config.TT_USER_MAX))


def sleep_automatic():
    time.sleep(random.uniform(config.TT_AUTOMATIC_MIN, config.TT_AUTOMATIC_MAX))


def search_travels_roudtrip(client, hs):
    start, end = get_random_start_end_stations(hs=hs)
    sleep_user()
    a = api_user.search_travel(client, start, end, hs=hs, logged=False)
    sleep_user()
    b = api_user.search_travel(client, end, start, hs=hs, logged=False)


def search_travels_oneway(client, hs):
    start, end = get_random_start_end_stations(hs=hs)
    sleep_user()
    a = api_user.search_travel(client, start, end, hs=hs, logged=False)


def perform_login_user(client):
    api_user.home(client)
    sleep_user()
    api_user.client_login_page(client)
    sleep_user()
    user_id, token = api_user.login(client)
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json", "Accept": "application/json"}
    sleep_automatic()
    api_user.home(client)
    sleep_user()
    return user_id, headers


def perform_login_admin(client):
    api_admin.home(client)
    sleep_user()
    user_id, token = api_admin.login(client)
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json", "Accept": "application/json"}
    sleep_automatic()
    api_admin.home(client, headers=headers)
    sleep_automatic()
    orders = api_admin.get_all_orders(client, headers)
    sleep_user()
    return user_id, headers, orders


def search_and_preserve_travel(client, user_id, headers, hs, start, end):
    flag = False
    for i in range(1, 5):
        a = api_user.search_travel(client, start, end, hs=hs, headers=headers)
        if a is None:
            start, end = get_random_start_end_stations(hs=hs)
        else:
            flag = True
            break
    if flag:
        trip_id_a = f'{a["data"][0]["tripId"]["type"]}{a["data"][0]["tripId"]["number"]}'
        sleep_user()
        api_user.book(client, user_id, trip_id=trip_id_a, from_station=start, to_station=end, hs=hs,
                      headers=headers)
        sleep_user()
        api_user.pay(client, user_id, trip_id_a, hs=hs, headers=headers)
        return start, end
    return None, None
