import random
from datetime import datetime, timedelta
import pandas as pd
import utils
import config



def home(client, headers=None):
    client.get("/admin.html", name=utils.get_name_suffix("admin_home"), headers=headers)


''' --------- User --------- '''

def login(client):
    user_name = "admin"
    password = "222222"
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    body = {"username": user_name, "password": password}
    response = client.post(url="/api/v1/users/login", headers=headers, json=body, context=body,
                           name=utils.get_name_suffix("admin_login"))
    response_as_json = utils.get_json_from_response(response)
    data = response_as_json["data"]
    user_id = data["userId"]
    token = data["token"]
    return user_id, token

def api_call_admin_create_user(client, token, user_name, password):
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json", "Content-Type": "application/json"}
    body = {"documentNum": None, "documentType": 0, "email": "string", "gender": 0, "password": password,
            "userName": user_name}
    response = client.post(url="/api/v1/adminuserservice/users", headers=headers, json=body, context=body,
                           name=utils.get_name_suffix("admin_create_user"))
    response_as_json = utils.get_json_from_response(response)
    return response_as_json

def get_all_users(client, headers=None):
    response = client.get(url='/api/v1/adminuserservice/users', name='admin_get_all_users',
                          headers=headers)
    response_as_json = utils.get_json_from_response(response)
    return response_as_json


def create_random_user(client, headers):
    body = {"userName": utils.get_random_string(),
            "password": utils.get_random_string(),
            "gender": int(random.random()),
            "email": utils.get_random_string(),
            "documentType": int(random.random()),
            "documentNum": utils.get_random_string()}
    response = client.post(url='/api/v1/adminuserservice/users', name='admin_add_random_user',
                          headers=headers, json=body, context=body)
    response_as_json = utils.get_json_from_response(response)
    return response_as_json


''' --------- Travel --------- '''

def get_all_travels(client, headers=None):
    response = client.get(url="/api/v1/admintravelservice/admintravel", headers=headers,
                          name=utils.get_name_suffix("admin_get_all_travels"))
    response_as_json = utils.get_json_from_response(response)
    return response_as_json


def update_travel(client, trip, headers=None):
    trip_id = f'{trip["trip"]["tripId"]["type"]}{trip["trip"]["tripId"]["number"]}'
    x = pd.to_datetime(trip["trip"]["startingTime"])
    starting_time = x + timedelta(hours=random.choice([-1, +1]))

    body = {"tripId": trip_id, "trainTypeId": trip["trip"]["trainTypeId"], "routeId": trip["trip"]["routeId"],
            "startingTime": starting_time.isoformat(sep='T', timespec='milliseconds')}
    response = client.put(url="/api/v1/admintravelservice/admintravel", json=body, context=body, headers=headers,
                          name=utils.get_name_suffix("admin_uptdate_travel"))
    response_as_json = utils.get_json_from_response(response)
    return response_as_json


def create_travel(client, route, hs=True, headers=None):
    if hs:
        train_type_id = random.choice(config.HS_TRAIN_TYPE_ID)
    else:
        train_type_id = random.choice(config.OTHER_TRAIN_TYPE_ID)

    number = random.randint(2000, 4000)

    body = {"tripId": f'{train_type_id[0]}{number}', "trainTypeId": train_type_id, "routeId": route["id"],
            "startingTime": int(datetime.now().timestamp())}
    response = client.post(url="/api/v1/admintravelservice/admintravel", json=body, headers=headers, context=body,
                           name=utils.get_name_suffix("admin_create_travel"))
    response_as_json = utils.get_json_from_response(response)
    return response_as_json


def delete_travel(client, travel_id, headers=None):
    response = client.post(url=f"/api/v1/admintravelservice/admintravel/{travel_id}", headers=headers,
                           name=utils.get_name_suffix("admin_delete_travel"))
    response_as_json = utils.get_json_from_response(response)
    return response_as_json


def delete_random_travel(client, travels, hs=True, headers=None):
    travel = random.choice(travels)
    trip_id = travel["trip"]["tripId"]
    iteration = 0
    if hs:
        while not ((trip_id['type'] == 'D' or trip_id['type'] == 'G') and (int(trip_id['number']) >= 2000)):
            travel = random.choice(travels)
            trip_id = travel["trip"]["tripId"]
            if iteration >= 20:
                print("No trip to delete hs")
                return None
            iteration += 1
    else:
        while not (not (trip_id['type'] == 'D' or trip_id['type'] == 'G') and (int(trip_id['number']) >= 2000)):
            travel = random.choice(travels)
            trip_id = travel["trip"]["tripId"]
            if iteration >= 20:
                print("No trip to delete other")
                return None
            iteration += 1
    return delete_travel(client, f'{travel["trip"]["tripId"]}{travel["trip"]["number"]}', headers=headers)


''' --------- Order --------- '''

def get_all_orders(client, headers=None):
    response = client.get(url="/api/v1/adminorderservice/adminorder", headers=headers,
                          name=utils.get_name_suffix("admin_get_all_orders"))
    response_as_json = utils.get_json_from_response(response)
    return response_as_json


def create_order(client, hs=True, headers=None):
    start, end = utils.get_random_start_end_stations(hs)
    body = {"boughtDate": f"{str(datetime.now()).replace(' ', 'T')[:-3]}Z",
            "travelDate": 1,
            "travelTime": 2,
            "accountId": "4d2a46c7-71cb-4cf1-b5bb-b68406d9da6f",
            "contactsName": f"Contact_{random.randint(1, 10)}",
            "documentType": 1,
            "contactsDocumentNumber": f"DocumentNumber_{random.randint(1, 10)}",
            "trainNumber": f"{'G' if hs else 'K'}{random.randint(2000, 4000)}",
            "coachNumber": 5,
            "seatClass": 2,
            "seatNumber": f"FirstClass-{random.randint(1, 30)}",
            "from": start,
            "to": end,
            "status": 0,
            "price": str(round(random.random() * 100, 2))}
    response = client.post(url="/api/v1/adminorderservice/adminorder", json=body, headers=headers, context=body,
                           name=utils.get_name_suffix("admin_create_order"))

    response_as_json = utils.get_json_from_response(response)
    return response_as_json


def get_all_prices(client, headers=None):
    response = client.get(url='/api/v1/adminbasicservice/adminbasic/prices', name='admin_get_all_prices',
                          headers=headers)
    response_as_json = utils.get_json_from_response(response)
    return response_as_json


def modify_price(client, headers=None, price=None):
    body = {"id": price["id"],
            "trainType": price["trainType"],
            "routeId": price["routeId"],
            "basicPriceRate": random.random(),
            "firstClassPriceRate": random.random()}
    response = client.put(url='/api/v1/adminbasicservice/adminbasic/prices', name='admin_modify_price', headers=headers,
                          context=body, json=body)
    response_as_json = utils.get_json_from_response(response)
    return response_as_json


def update_order(client, order, headers=None):
    new_price = float(order['price']) + (random.random() * 20 - 10)
    order['price'] = str(round(new_price, 2))
    response = client.put(url='/api/v1/adminorderservice/adminorder', name='admin_update_order', headers=headers,
                          context=order, json=order)
    response_as_json = utils.get_json_from_response(response)
    return response_as_json


def delete_order(client, order_id, train_number, headers=None):
    response = client.post(url=f"/api/v1/admintravelservice/admintravel/{order_id}/{train_number}", headers=headers,
                           name=utils.get_name_suffix("admin_delete_order"))
    response_as_json = utils.get_json_from_response(response)
    return response_as_json


def delete_random_order(client, orders, hs=True, headers=None):
    order = random.choice(orders['data'])
    train_number = order['trainNumber']
    iteration = 0
    if hs:
        while not ((train_number[0] == 'D' or train_number[0] == 'G') and (int(train_number[1:]) >= 2000)):
            order = random.choice(orders)
            train_number = order['trainNumber']
            if iteration >= 20:
                print("No trip to delete hs")
                return None
            iteration += 1
    else:
        while not (not (train_number[0] == 'D' or train_number[0] == 'G') and (int(train_number[1:]) >= 2000)):
            order = random.choice(orders)
            train_number = order['trainNumber']
            if iteration >= 20:
                print("No trip to delete other")
                return None
            iteration += 1
    return delete_order(client, order['id'], train_number, headers=headers)


''' --------- Route --------- '''

def get_all_routes(client, headers=None):
    response = client.get(url="/api/v1/adminrouteservice/adminroute", headers=headers,
                          name=utils.get_name_suffix("admin_get_all_routes"))
    response_as_json = utils.get_json_from_response(response)
    return response_as_json


''' --------- Basic --------- '''

def get_all_contacts(client, headers=None):
    response = client.get(url='/api/v1/adminbasicservice/adminbasic/contacts', name='admin_get_all_contacts',
                          headers=headers)
    response_as_json = utils.get_json_from_response(response)
    return response_as_json


def modify_contact(client, headers=None, contact=None):
    body = {"id": contact["id"],
            "name": contact["name"],
            "documentType": int(random.random() * 5),
            "documentNumber": contact["documentNumber"],
            "phoneNumber": f'{contact["phoneNumber"][:-1]}{int(random.random() * 9)}'}
    response = client.put(url='/api/v1/adminbasicservice/adminbasic/contacts', name='admin_modify_contact',
                          headers=headers, context=body, json=body)
    response_as_json = utils.get_json_from_response(response)
    return response_as_json

