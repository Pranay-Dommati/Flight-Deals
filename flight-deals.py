import requests
from datetime import datetime, timedelta
from twilio.rest import Client
import smtplib
from email.mime.text import MIMEText
from email.header import Header
account_sid = "AC3eeb1bbcd63b613dc89ce26cbf9cda10"
auth_token = "13ef7044edbc12b3f61aee2e3c925f14"
client = Client(account_sid, auth_token)

FROM_DATE = (datetime.now()+timedelta(days=1)).strftime("%d/%m/%Y")
TO_DATE = (datetime.now()+timedelta(days=6*30)).strftime("%d/%m/%Y")
RETURN_FROM = (datetime.now()+timedelta(days=6*30+7)).strftime("%d/%m/%Y")
RETURN_TO = (datetime.now()+timedelta(days=6*30+28)).strftime("%d/%m/%Y")
flight_search_url = "https://api.tequila.kiwi.com/locations/query"
flight_search_api_key = "Rzqzmue5DPoeUU8MtGNhG85B9InF7ak7"
flight_get_price_url = "https://api.tequila.kiwi.com/v2/search"
flight_search_headers = {
    "apikey":flight_search_api_key
}
sheety_endpoint = "https://api.sheety.co/1f3d76c7bff772b31243b79f12780634/flightDeals/prices"
sheety_users_endpoint = "https://api.sheety.co/1f3d76c7bff772b31243b79f12780634/flightDeals/users"
sheety_token = "Bearer BunnyDommatiGoud"
sheety_headers = {
    "Authorization":sheety_token
}

def get_emails():
    emails = []
    user_sheety_response = requests.get(url=sheety_users_endpoint, headers=sheety_headers)
    for i in user_sheety_response.json()['users']:
        emails.append(i['email'])
    return emails
#class FlightSearch:
def return_city_params(city_name):
    params = {
        'term':city_name,
        'location_types':'city'
    }
    return params


response_sheety = requests.get(url=sheety_endpoint, headers=sheety_headers)
CITY_NAMES = []
for _ in response_sheety.json()['prices']:
    CITY_NAMES.append(_['city'])

CITY_CODES = []
for _ in CITY_NAMES:
    response_flight_search = requests.get(url=flight_search_url,headers=flight_search_headers,params=return_city_params(_))
    CITY_CODES.append(response_flight_search.json()['locations'][0]['code'])

#print(response_sheety.json()['prices'])
# for id in range(len(CITY_CODES)):
#     sheety_update_params = {
#         "price":{
#             "iataCodes":CITY_CODES[id]
#         }
#     }
#     response_sheety_update = requests.put(url=f"{sheety_endpoint}/{id+2}",headers=sheety_headers,json=sheety_update_params)
#





check_atleast_oneflight = 0
low_price_cities={}
for _ in response_sheety.json()['prices']:
    params = {
        "fly_from":"LON",
        "fly_to":_['iataCodes'],
        "date_from": f"{FROM_DATE}",
        "date_to": f"{TO_DATE}",
        "return_from":f"{RETURN_FROM}",
        "return_to":f"{RETURN_TO}",
        "price_from":1,
        "price_to": int(_['lowestPrice']),
        "curr":"GBP",
        "max_stopovers":0,
        "one_for_city":1
    }
    response_get_price = requests.get(url=flight_get_price_url,headers=flight_search_headers,params=params)
    try:
        path = response_get_price.json()['data'][0]
        low_price_cities[_['city']] = {'price':path['price'],
                                       'starting_city':path['cityFrom'],
                                       'starting_airport_code':path['flyFrom'],
                                       'going_city':path['cityTo'],
                                       'going_airport_code':path['flyTo'],
                                       'outbound_date':(path['local_departure'])[:10],
                                       'inbound_date':(path['route'][1]['local_departure'])[:10]
                                       }
        check_atleast_oneflight = 1
    except (KeyError,IndexError):
        pass


# if check_atleast_oneflight == 1:
#     for _ in low_price_cities:
#         body = f"""Low price alert! Only £{low_price_cities[_]['price']} to fly from
#  {low_price_cities[_]['starting_city']}-{low_price_cities[_]['starting_airport_code']}
#  to {low_price_cities[_]['going_city']}-{low_price_cities[_]['going_airport_code']},from
#  {low_price_cities[_]['outbound_date']} to {low_price_cities[_]['inbound_date']}"""
#
#         message = client.messages.create(
#           from_='+16107560774',
#           to='+917569897932',
#           body=body
#         )
# else:
#     pass
if check_atleast_oneflight ==1:
    for _ in low_price_cities:

        body = f"""Only {low_price_cities[_]['price']} pounds to fly from
         {low_price_cities[_]['starting_city']}-{low_price_cities[_]['starting_airport_code']}
         to {low_price_cities[_]['going_city']}-{low_price_cities[_]['going_airport_code']},from
         {low_price_cities[_]['outbound_date']} to {low_price_cities[_]['inbound_date']}"""
        for _ in get_emails():
            with smtplib.SMTP("smtp.gmail.com") as connection:
                connection.starttls()
                connection.login(user="cseiot12345@gmail.com", password="frvkjodhojvaopwr")
                connection.sendmail(from_addr="cseiot12345@gmail.com", to_addrs=_, msg=f"Subject:Low price alert!!\n\n{body}")
