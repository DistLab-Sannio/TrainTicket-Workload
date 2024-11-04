import random
import utils
from datetime import datetime, timedelta
import config


def login(client):
    user_name = "fdse_microservice"
    password = "111111"
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    body = {"username": user_name, "password": password}
    response = client.post(url="/api/v1/users/login", headers=headers, context=body, json=body,
                           name=utils.get_name_suffix("login"))
    response_as_json = utils.get_json_from_response(response)
    data = response_as_json["data"]
    user_id = data["userId"]
    token = data["token"]
    return user_id, token


def home(client):
    client.get("/index.html", name=utils.get_name_suffix("home"))
    pass


def client_login_page(client):
    client.get("/client_login.html", name=utils.get_name_suffix("client_login_page"))


def search_travel(client, from_station, to_station, hs=True, logged=True, headers=None):
    body = {"startingPlace": from_station, "endPlace": to_station}
    if hs:
        url = "/api/v1/travelservice/trips/left"
        response = client.post(url=url, json=body, context=body, headers=headers,
                               name=utils.get_name_suffix(f"search_travel_hs_{'logged' if logged else 'external'}"))
    else:
        url = "/api/v1/travel2service/trips/left"
        response = client.post(url=url, json=body, context=body, headers=headers,
                               name=utils.get_name_suffix(f"search_travel_other_{'logged' if logged else 'external'}"))
    return utils.get_json_from_response(response)


def get_trip_information(client, from_station, to_station, hs=True):
    body = {"startingPlace": from_station, "endPlace": to_station}
    if hs:
        url = "/api/v1/travelservice/trips/left"
        response = client.post(url=url, json=body, context=body, name=utils.get_name_suffix("get_trip_information_hs"))
    else:
        url = "/api/v1/travel2service/trips/left"
        response = client.post(url=url, json=body, context=body,
                               name=utils.get_name_suffix("get_trip_information_other"))
    return utils.get_json_from_response(response)


def book(client, user_id, trip_id="D1345", from_station="Shang Hai", to_station="Su Zhou", hs=True, headers=None):
    tomorrow = datetime.now() + timedelta(1)
    next_monday = utils.next_weekday(tomorrow, 0)
    departure_date = next_monday.strftime("%Y-%m-%d")

    def api_call_insurance():
        response = client.get(url="/api/v1/assuranceservice/assurances/types", headers=headers,
                              name=utils.get_name_suffix("get_assurance_types"))
        return utils.get_json_from_response(response)

    def api_call_food():
        response = client.get(url=f"/api/v1/foodservice/foods/{departure_date}/{from_station}/{to_station}/{trip_id}",
                              headers=headers, name=utils.get_name_suffix("get_food_types"))
        return utils.get_json_from_response(response)

    def api_call_contacts():
        response = client.get(url=f"/api/v1/contactservice/contacts/account/{user_id}", headers=headers,
                              name=utils.get_name_suffix("query_contacts"))
        data = utils.get_json_from_response(response)["data"]
        contact_id = data[0]["id"]
        return contact_id

    def api_call_ticket(consign=False):
        body = {"accountId": user_id, "contactsId": contact_id, "tripId": trip_id, "seatType": "2",
                "date": departure_date, "from": from_station, "to": to_station,
                "assurance": random.choice(config.ASSURANCE_TYPES), "foodType": 1,
                "foodName": "Bone Soup", "foodPrice": 2.5, "stationName": "", "storeName": ""}
        if consign:
            body["consigneeName"] = utils.get_random_string(10)
            body["consigneePhone"] = utils.get_random_string(10)
            body["consigneeWeight"] = int(random.random() * 50)

        if hs:
            response = client.post(url="/api/v1/preserveservice/preserve", json=body, headers=headers, context=body,
                                   name=utils.get_name_suffix("preserve_ticket_hs"))
        else:
            response = client.post(url="/api/v1/preserveotherservice/preserveOther", json=body, headers=headers,
                                   context=body,
                                   name=utils.get_name_suffix("preserve_ticket_other"))
        return response

    contact_id = api_call_contacts()
    api_call_food()
    api_call_insurance()
    api_call_ticket(random.choice([True, False]))


def get_all_orders(client, user_id, hs=True, headers=None):
    body = {"loginId": user_id, "enableStateQuery": "false", "enableTravelDateQuery": "false",
            "enableBoughtDateQuery": "false", "travelDateStart": "null", "travelDateEnd": "null",
            "boughtDateStart": "null", "boughtDateEnd": "null"}
    if hs:
        response = client.post(url="/api/v1/orderservice/order/refresh", json=body, headers=headers, context=body,
                               name=utils.get_name_suffix("get_order_information_hs"))
    else:
        response = client.post(url="/api/v1/orderOtherService/orderOther/refresh", json=body, headers=headers,
                               context=body,
                               name=utils.get_name_suffix("get_order_information_other"))
    return utils.get_json_from_response(response)['data']


def get_last_order(client, user_id, expected_status, hs=True, headers=None):
    data = get_all_orders(client, user_id, hs, headers)
    for entry in data:
        if entry["status"] == expected_status:
            return entry
    return None


def get_last_order_id(client, user_id, expected_status, hs=True, headers=None):
    order = get_last_order(client, user_id, expected_status, hs=hs, headers=headers)
    if order is not None:
        order_id = order["id"]
        return order_id

    return None


def pay(client, user_id, trip_id="D1345", hs=True, headers=None):
    order_id = get_last_order_id(client, user_id, config.TICKET_STATUS_BOOKED, hs=hs, headers=headers)
    if order_id == None:
        raise Exception("Weird... There is no order to pay.")

    def api_call_pay(headers):
        body = {"orderId": order_id, "tripId": trip_id}
        response = client.post(url="/api/v1/inside_pay_service/inside_payment", json=body, headers=headers,
                               context=body,
                               name=utils.get_name_suffix(f"pay_order_{'hs' if hs else 'other'}"))

        return utils.get_json_from_response(response)

    api_call_pay(headers=headers)


def cancel(client, user_id, hs=True, headers=None):
    order_id = get_last_order_id(client, user_id, config.TICKET_STATUS_BOOKED, hs, headers)
    if order_id is None:
        raise Exception("Weird... There is no order to cancel.")

    def api_call_cancel_refund():
        response = client.get(url=f"/api/v1/cancelservice/cancel/refound/{order_id}",
                              name=utils.get_name_suffix("cancel_refund_order"), headers=headers)
        return utils.get_json_from_response(response)

    def api_call_cancel():
        response = client.get(url=f"/api/v1/cancelservice/cancel/{order_id}/{user_id}",
                              name=utils.get_name_suffix("cancel_order"), headers=headers)
        return utils.get_json_from_response(response)

    api_call_cancel_refund()
    api_call_cancel()


def get_travel_plan(client, from_station, to_station):
    today_str = (datetime.now() + timedelta(days=1000)).strftime("%Y-%m-%d")
    body = {"startingPlace": from_station,
            "endPlace": to_station,
            "departureTime": today_str}
    response = client.post(url="/api/v1/travelplanservice/travelPlan/cheapest", json=body, context=body,
                           name=utils.get_name_suffix("get_travel_plan"))
    return utils.get_json_from_response(response)


def collect_ticket(client, headers, order):
    order_id = order["id"]
    response = client.get(url=f"/api/v1/executeservice/execute/collected/{order_id}",
                          name=utils.get_name_suffix("collect_ticket"), headers=headers)
    return utils.get_json_from_response(response)


def execute_ticket(client, headers, order):
    order_id = order["id"]
    response = client.get(url=f"/api/v1/executeservice/execute/execute/{order_id}",
                          name=utils.get_name_suffix("execute_ticket"), headers=headers)
    return utils.get_json_from_response(response)

# def collect_and_use(client, user_id):
#     order_id = get_last_order_id(client, user_id, STATUS_PAID)
#     if order_id == None:
#         raise Exception("Weird... There is no order to collect.")
#
#     def api_call_collect_ticket():
#         response = client.get(url=f"/api/v1/executeservice/execute/collected/{order_id}",
#                               name=utils.get_name_suffix("collect_ticket"))
#         return utils.get_json_from_response(response)
#
#     api_call_collect_ticket()
#
#     order_id = get_last_order_id(client, user_id, STATUS_COLLECTED)
#     if order_id == None:
#         raise Exception("Weird... There is no order to execute.")
#
#     def api_call_enter_station():
#         response = client.get(url=f"/api/v1/executeservice/execute/execute/{order_id}",
#                               name=utils.get_name_suffix("enter_station"))
#         return utils.get_json_from_response(response)
#
#     api_call_enter_station()
#
#
# def get_voucher(client, user_id):
#     order_id = get_last_order_id(client, user_id, STATUS_EXECUTED)
#     if order_id == None:
#         raise Exception("Weird... There is no order that was used.")
#
#     def api_call_get_voucher():
#         body = {"orderId": order_id, "type": 1}
#         response = client.post(url=f"/getVoucher", json=body, name=utils.get_name_suffix("get_voucher"))
#         return utils.get_json_from_response(response)
#
#     api_call_get_voucher()

# def search_departure(client, from_station="Shang Hai", to_station="Su Zhou", hs=True):
#     if hs:
#         url = "/api/v1/travelservice/trips/left"
#     else:
#         url = "/api/v1/travel2service/trips/left"
#     departure_date = utils.get_departure_date()
#
#     body = {"startingPlace": from_station, "endPlace": to_station, "departureTime": departure_date}
#     response = client.post(url="/api/v1/travelservice/trips/left", json=body, catch_response=True,
#                            name=utils.get_name_suffix("get_trip_information"))
#     return utils.get_json_from_response(response)
#
#
# def search_return(client, from_station="Su Zhou", to_station="Shang Hai"):
#     departure_date = utils.get_departure_date()
#
#     body = {"startingPlace": from_station, "endPlace": to_station, "departureTime": departure_date}
#     response = client.post(url="/api/v1/travel2service/trips/left", json=body, catch_response=True,
#                            name=utils.get_name_suffix("get_trip_information"))
#     return utils.get_json_from_response(response)
