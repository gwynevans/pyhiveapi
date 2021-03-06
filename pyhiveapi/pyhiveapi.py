import operator
from datetime import datetime
from datetime import timedelta
import requests
import colorsys

HIVE_NODE_UPDATE_INTERVAL_DEFAULT = 120
HIVE_WEATHER_UPDATE_INTERVAL_DEFAULT = 60  #### Update to 900 or 600
MINUTES_BETWEEN_LOGONS = 15

NODE_ATTRIBS = {"Header": "HeaderText"}


class HiveDevices:
    """Initiate Hive Devices Class."""

    hub = []
    thermostat = []
    boiler_module = []
    plug = []
    light = []
    sensors = []


class HiveProducts:
    """Initiate Hive Products Class."""

    heating = []
    hotwater = []
    light = []
    plug = []
    sensors = []


class HivePlatformData:
    """Initiate Hive PlatformData Class."""

    minmax = {}


class HiveTemperature:
    """Initiate Hive Temperature Class."""

    unit = ""
    value = 0.00


class HiveWeather:
    """Initiate Hive Weather Class."""

    last_update = datetime(2017, 1, 1, 12, 0, 0)
    nodeid = ""
    icon = ""
    description = ""
    temperature = HiveTemperature()


class HiveSession:
    """Initiate Hive Session Class."""

    session_id = ""
    session_logon_datetime = datetime(2017, 1, 1, 12, 0, 0)
    username = ""
    password = ""
    postcode = ""
    timezone = ""
    countrycode = ""
    locale = ""
    temperature_unit = ""
    devices = HiveDevices()
    products = HiveProducts()
    weather = HiveWeather()
    data = HivePlatformData()
#    holiday_mode = Hive_HolidayMode()
    update_node_interval_seconds = HIVE_NODE_UPDATE_INTERVAL_DEFAULT
    update_weather_interval_seconds = HIVE_WEATHER_UPDATE_INTERVAL_DEFAULT
    last_update = datetime(2017, 1, 1, 12, 0, 0)
    logging = False
    file = False


class HiveAPIURLS:
    """Initiate Hive API URLS Class."""

    global_login = ""
    base = ""
    weather = ""
    holiday_mode = ""
    devices = ""
    products = ""
    nodes = ""


class HiveAPIHeaders:
    """Initiate Hive API Headers Class."""

    accept_key = ""
    accept_value = ""
    content_type_key = ""
    content_type_value = ""
    session_id_key = ""
    session_id_value = ""


class HiveAPIDetails:
    """Initiate Hive API Details Class."""

    urls = HiveAPIURLS()
    headers = HiveAPIHeaders()
    platform_name = ""


HIVE_API = HiveAPIDetails()
HSC = HiveSession()


class Pyhiveapi:
    def __init__(self):
        """Initialise the base variable values."""

        HIVE_API.platform_name = ""

        HIVE_API.urls.global_login = "https://beekeeper.hivehome.com/1.0/global/login"
        HIVE_API.urls.base = ""
        HIVE_API.urls.weather = "https://weather-prod.bgchprod.info/weather"
        HIVE_API.urls.holiday_mode = "/holiday-mode"
        HIVE_API.urls.devices = "/devices"
        HIVE_API.urls.products = "/products"
        HIVE_API.urls.nodes = "/nodes"

        HIVE_API.headers.accept_key = "Accept"
        HIVE_API.headers.accept_value = "*/*"
        HIVE_API.headers.content_type_key = "content-type"
        HIVE_API.headers.content_type_value = "application/json"
        HIVE_API.headers.session_id_key = "authorization"
        HIVE_API.headers.session_id_value = None


    def hive_api_json_call(self, request_type, request_url, json_string_content, absolute_request_url):
        """Call the JSON Hive API and return any returned data."""
        api_headers = {HIVE_API.headers.content_type_key:
                       HIVE_API.headers.content_type_value,
                       HIVE_API.headers.accept_key:
                       HIVE_API.headers.accept_value,
                       HIVE_API.headers.session_id_key:
                       HIVE_API.headers.session_id_value}

        requests_timeout = 10
        json_return = {}
        full_request_url = ""

        if absolute_request_url:
            full_request_url = request_url
        else:
            full_request_url = HIVE_API.urls.base + request_url

        json_call_try_finished = False
        try:
            if request_type == "POST":
                json_response = requests.post(full_request_url,
                                              data=json_string_content,
                                              headers=api_headers,
                                              timeout=requests_timeout)
            elif request_type == "GET":
                json_response = requests.get(full_request_url,
                                             data=json_string_content,
                                             headers=api_headers,
                                             timeout=requests_timeout)
            elif request_type == "PUT":
                json_response = requests.put(full_request_url,
                                             data=json_string_content,
                                             headers=api_headers,
                                             timeout=requests_timeout)
            else:
                json_response = ""

            json_call_try_finished = True
        except (IOError, RuntimeError, ZeroDivisionError):
            json_call_try_finished = False
        finally:
            if not json_call_try_finished:
                json_return['original'] = "No response to JSON Hive API request"
                json_return['parsed'] = "No response to JSON Hive API request"

        if json_call_try_finished:
            parse_json_try_finished = False
            try:
                json_return['original'] = json_response
                json_return['parsed'] = json_response.json()

                parse_json_try_finished = True
            except (IOError, RuntimeError, ZeroDivisionError):
                parse_json_try_finished = False
            finally:
                if not parse_json_try_finished:
                    json_return['original'] = "Error parsing JSON data"
                    json_return['parsed'] = "Error parsing JSON data"

        return json_return


    def hive_api_logon(self):
        """Log in to the Hive API and get the Session ID."""
        login_details_found = True
        HSC.session_id = None

        try_finished = False
        try:
            api_resp_d = {}
            api_resp_p = None

            json_string_content = '{"username": "' + HSC.username + '","password": "' + HSC.password + '"}'

            api_resp_d = Pyhiveapi.hive_api_json_call(self, "POST", HIVE_API.urls.global_login, json_string_content, True)
            api_resp_p = api_resp_d['parsed']

            if ('token' in api_resp_p and
                    'user' in api_resp_p and
                    'platform' in api_resp_p):
                HIVE_API.headers.session_id_value = api_resp_p["token"]
                HSC.session_id = HIVE_API.headers.session_id_value
                HSC.session_logon_datetime = datetime.now()

                if 'endpoint' in api_resp_p['platform']:
                    HIVE_API.urls.base = api_resp_p['platform']['endpoint']
                else:
                    login_details_found = False

                if 'name' in api_resp_p['platform']:
                    HIVE_API.platform_name = api_resp_p['platform']['name']
                else:
                    login_details_found = False

                if 'locale' in api_resp_p['user']:
                    HSC.locale = api_resp_p['user']['locale']
                else:
                    login_details_found = False

                if 'countryCode' in api_resp_p['user']:
                    HSC.countrycode = api_resp_p['user']['countryCode']
                else:
                    login_details_found = False

                if 'timezone' in api_resp_p['user']:
                    HSC.timezone = api_resp_p['user']['timezone']
                else:
                    login_details_found = False

                if 'postcode' in api_resp_p['user']:
                    HSC.postcode = api_resp_p['user']['postcode']
                else:
                    login_details_found = False

                if 'temperatureUnit' in api_resp_p['user']:
                    HSC.temperature_unit = api_resp_p['user']['temperatureUnit']
                else:
                    login_details_found = False
            else:
                login_details_found = False

            try_finished = True

        except (IOError, RuntimeError, ZeroDivisionError):
            try_finished = False
        finally:
            if not try_finished:
                login_details_found = False

        if not login_details_found:
            HSC.session_id = None


    def check_hive_api_logon(self):
        """Check if currently logged in with a valid Session ID."""
        current_time = datetime.now()
        l_logon_secs = (current_time - HSC.session_logon_datetime).total_seconds()
        l_logon_mins = int(round(l_logon_secs / 60))

        if l_logon_mins >= MINUTES_BETWEEN_LOGONS or HSC.session_id is None:
            Pyhiveapi.hive_api_logon(self)

        if HSC.file == True:
            HSC.session_id = "Test"



    def update_data(self, node_id):
        """Get latest data for Hive nodes - rate limiting."""
        nodes_updated = False
        current_time = datetime.now()
        last_update_secs = (current_time - HSC.last_update).total_seconds()
        if last_update_secs >= HSC.update_node_interval_seconds:
            nodes_updated = Pyhiveapi.hive_api_get_nodes(self, node_id)
        return nodes_updated


    def hive_api_get_nodes_nl(self):
        """Get latest data for Hive nodes - not rate limiting."""
        Pyhiveapi.hive_api_get_nodes(self, "NoID")


    def hive_api_get_nodes(self, node_id):
        """Get latest data for Hive nodes."""
        get_nodes_successful = True

        Pyhiveapi.check_hive_api_logon(self)

        if HSC.session_id is not None:
            tmp_devices_hub = []
            tmp_devices_thermostat = []
            tmp_devices_boiler_module = []
            tmp_devices_plug = []
            tmp_devices_light = []
            tmp_devices_sensors = []

            tmp_products_heating = []
            tmp_products_hotwater = []
            tmp_products_light = []
            tmp_products_plug = []
            tmp_products_sensors = []

            try_finished = False
            try:
                api_resp_d = {}
                api_resp_p = None
                api_resp_d = Pyhiveapi.hive_api_json_call(self, "GET", HIVE_API.urls.devices, "", False)

                api_resp_p = api_resp_d['parsed']

                for a_device in api_resp_p:
                    if "type" in a_device:
                        if a_device["type"] == "hub":
                            tmp_devices_hub.append(a_device)
                        if a_device["type"] == "thermostatui":
                            tmp_devices_thermostat.append(a_device)
                        if a_device["type"] == "boilermodule":
                            tmp_devices_boiler_module.append(a_device)
                        if a_device["type"] == "activeplug":
                            tmp_devices_plug.append(a_device)
                        if (a_device["type"] == "warmwhitelight" or
                                a_device["type"] == "tuneablelight" or
                                a_device["type"] == "colourtuneablelight"):
                            tmp_devices_light.append(a_device)
                        if (a_device["type"] == "motionsensor" or
                                a_device["type"] == "contactsensor"):
                            tmp_devices_sensors.append(a_device)

                try_finished = True
            except (IOError, RuntimeError, ZeroDivisionError):
                try_finished = False
            finally:
                if not try_finished:
                    try_finished = False

            try_finished = False
            try:
                api_resp_d = {}
                api_resp_p = None
                api_resp_d = Pyhiveapi.hive_api_json_call(self, "GET", HIVE_API.urls.products, "", False)

                api_resp_p = api_resp_d['parsed']

                for a_product in api_resp_p:
                    if "type" in a_product:
                        if a_product["type"] == "heating":
                            tmp_products_heating.append(a_product)
                        if a_product["type"] == "hotwater":
                            tmp_products_hotwater.append(a_product)
                        if a_product["type"] == "activeplug":
                            tmp_products_plug.append(a_product)
                        if (a_product["type"] == "warmwhitelight" or
                                a_product["type"] == "tuneablelight" or
                                a_product["type"] == "colourtuneablelight"):
                            tmp_products_light.append(a_product)
                        if (a_product["type"] == "motionsensor" or
                                a_product["type"] == "contactsensor"):
                            tmp_products_sensors.append(a_product)
                try_finished = True
            except (IOError, RuntimeError, ZeroDivisionError):
                try_finished = False
            finally:
                if not try_finished:
                    try_finished = False

            try_finished = False
            try:
                if len(tmp_devices_hub) > 0:
                    HSC.devices.hub = tmp_devices_hub
                if len(tmp_devices_thermostat) > 0:
                    HSC.devices.thermostat = tmp_devices_thermostat
                if len(tmp_devices_boiler_module) > 0:
                    HSC.devices.boiler_module = tmp_devices_boiler_module
                if len(tmp_devices_plug) > 0:
                    HSC.devices.plug = tmp_devices_plug
                if len(tmp_devices_light) > 0:
                    HSC.devices.light = tmp_devices_light
                if len(tmp_devices_sensors) > 0:
                    HSC.devices.sensors = tmp_devices_sensors

                if len(tmp_products_heating) > 0:
                    HSC.products.heating = tmp_products_heating
                if len(tmp_products_hotwater) > 0:
                    HSC.products.hotwater = tmp_products_hotwater
                if len(tmp_products_plug) > 0:
                    HSC.products.plug = tmp_products_plug
                if len(tmp_products_light) > 0:
                    HSC.products.light = tmp_products_light
                if len(tmp_products_sensors) > 0:
                    HSC.products.sensors = tmp_products_sensors

                try_finished = True
            except (IOError, RuntimeError, ZeroDivisionError):
                try_finished = False
            finally:
                if not try_finished:
                    get_nodes_successful = False
        else:
            get_nodes_successful = False

        if get_nodes_successful:
            HSC.last_update = datetime.now()

        return get_nodes_successful


    def hive_api_get_weather(self):
        """Get latest weather data from Hive."""
        get_weather_successful = True

        current_time = datetime.now()
        last_update_secs = (current_time - HSC.weather.last_update).total_seconds()
        if last_update_secs >= HSC.update_weather_interval_seconds:
            Pyhiveapi.check_hive_api_logon(self)

            if HSC.session_id is not None:
                try_finished = False
                try:
                    api_resp_d = {}
                    api_resp_p = None
                    weather_url = HIVE_API.urls.weather + "?postcode=" + HSC.postcode + "&country=" + HSC.countrycode
                    weather_url = weather_url.replace(" ", "%20")

                    api_resp_d = Pyhiveapi.hive_api_json_call(self, "GET", weather_url, "", True)
                    api_resp_p = api_resp_d['parsed']

                    if "weather" in api_resp_p:
                        if "icon" in api_resp_p["weather"]:
                            HSC.weather.icon = api_resp_p["weather"]["icon"]
                        if "description" in api_resp_p["weather"]:
                            HSC.weather.description = api_resp_p["weather"]["icon"]
                        if "temperature" in api_resp_p["weather"]:
                            if "unit" in api_resp_p["weather"]["temperature"]:
                                HSC.weather.temperature.unit = api_resp_p["weather"]["temperature"]["unit"]
                            if "unit" in api_resp_p["weather"]["temperature"]:
                                HSC.weather.temperature.value = api_resp_p["weather"]["temperature"]["value"]
                        HSC.weather.nodeid = "HiveWeather"
                    else:
                        get_weather_successful = False

                    HSC.weather.last_update = current_time
                    try_finished = True
                except (IOError, RuntimeError, ZeroDivisionError):
                    try_finished = False
                finally:
                    if not try_finished:
                        try_finished = False
            else:
                get_weather_successful = False

        return get_weather_successful


    def p_minutes_to_time(self, minutes_to_convert):
        """Convert minutes string to datetime."""
        hours_converted, minutes_converted = divmod(minutes_to_convert, 60)
        converted_time = datetime.strptime(str(hours_converted)
                                           + ":"
                                           + str(minutes_converted),
                                           "%H:%M")
        converted_time_string = converted_time.strftime("%H:%M")
        return converted_time_string


    def p_get_schedule_now_next_later(self, hive_api_schedule):
        """Get the schedule now, next and later of a given nodes schedule."""
        schedule_now_and_next = {}
        date_time_now = datetime.now()
        date_time_now_day_int = date_time_now.today().weekday()

        days_t = ('monday',
                  'tuesday',
                  'wednesday',
                  'thursday',
                  'friday',
                  'saturday',
                  'sunday')

        days_rolling_list = list(days_t[date_time_now_day_int:] + days_t)[:7]

        full_schedule_list = []

        for day_index in range(0, len(days_rolling_list)):
            current_day_schedule = hive_api_schedule[days_rolling_list[day_index]]
            current_day_schedule_sorted = sorted(current_day_schedule,
                                                 key=operator.itemgetter('start'),
                                                 reverse=False)

            for current_slot in range(0, len(current_day_schedule_sorted)):
                current_slot_custom = current_day_schedule_sorted[current_slot]

                slot_date = datetime.now() + timedelta(days=day_index)
                slot_time = Pyhiveapi.p_minutes_to_time(self, current_slot_custom["start"])
                slot_time_date_s = (slot_date.strftime("%d-%m-%Y")
                                    + " "
                                    + slot_time)
                slot_time_date_dt = datetime.strptime(slot_time_date_s,
                                                      "%d-%m-%Y %H:%M")
                if slot_time_date_dt <= date_time_now:
                    slot_time_date_dt = slot_time_date_dt + timedelta(days=7)

                current_slot_custom['Start_DateTime'] = slot_time_date_dt
                full_schedule_list.append(current_slot_custom)

        fsl_sorted = sorted(full_schedule_list,
                            key=operator.itemgetter('Start_DateTime'),
                            reverse=False)

        schedule_now = fsl_sorted[-1]
        schedule_next = fsl_sorted[0]
        schedule_later = fsl_sorted[1]

        schedule_now['Start_DateTime'] = (schedule_now['Start_DateTime']
                                          - timedelta(days=7))

        schedule_now['End_DateTime'] = schedule_next['Start_DateTime']
        schedule_next['End_DateTime'] = schedule_later['Start_DateTime']
        schedule_later['End_DateTime'] = fsl_sorted[2]['Start_DateTime']

        schedule_now_and_next['now'] = schedule_now
        schedule_now_and_next['next'] = schedule_next
        schedule_now_and_next['later'] = schedule_later

        return schedule_now_and_next


    def initialise_api(self, username, password, mins_between_updates):
        """Setup the Hive platform."""
        HSC.username = username
        HSC.password = password

        if mins_between_updates <= 0:
            mins_between_updates = 2

        hive_node_update_interval = mins_between_updates * 60

        if HSC.username is None or HSC.password is None:
            return None
        else:
            Pyhiveapi.hive_api_logon(self)
            if HSC.session_id is not None:
                HSC.update_node_interval_seconds = hive_node_update_interval
                Pyhiveapi.hive_api_get_nodes_nl(self)
#                Pyhiveapi.hive_api_get_weather(self)


        device_list_all = {}
        device_list_sensor = []
        device_list_binary_sensor = []
        device_list_climate = []
        device_list_light = []
        device_list_plug = []

        if len(HSC.devices.hub) > 0:
            for a_device in HSC.devices.hub:
                if ("id" in a_device and "state" in a_device and "name" in a_device["state"]):
                    device_list_sensor.append({'HA_DeviceType': 'Hub_OnlineStatus', 'Hive_NodeID': a_device["id"], 'Hive_NodeName': a_device["state"]["name"], "Hive_DeviceType": "Hub"})


        if len(HSC.products.heating) > 0:
            for product in HSC.products.heating:
                if ("id" in product and "state" in product and "name" in product["state"]):
                    node_name = product["state"]["name"]
                    if len(HSC.products.heating) == 1:
                        node_name = None
                    device_list_climate.append({'HA_DeviceType': 'Heating', 'Hive_NodeID': product["id"], 'Hive_NodeName': node_name, "Hive_DeviceType": "Heating"})
                    device_list_sensor.append({'HA_DeviceType': 'Heating_CurrentTemperature', 'Hive_NodeID': product["id"], 'Hive_NodeName': node_name, "Hive_DeviceType": "Heating"})
                    device_list_sensor.append({'HA_DeviceType': 'Heating_TargetTemperature', 'Hive_NodeID': product["id"], 'Hive_NodeName': node_name, "Hive_DeviceType": "Heating"})
                    device_list_sensor.append({'HA_DeviceType': 'Heating_State', 'Hive_NodeID': product["id"], 'Hive_NodeName': node_name, "Hive_DeviceType": "Heating"})
                    device_list_sensor.append({'HA_DeviceType': 'Heating_Mode', 'Hive_NodeID': product["id"], 'Hive_NodeName': node_name, "Hive_DeviceType": "Heating"})
                    device_list_sensor.append({'HA_DeviceType': 'Heating_Boost', 'Hive_NodeID': product["id"], 'Hive_NodeName': node_name, "Hive_DeviceType": "Heating"})


        if len(HSC.products.hotwater) > 0:
            for product in HSC.products.hotwater:
                if ("id" in product and "state" in product and "name" in product["state"]):
                    node_name = product["state"]["name"]
                    if len(HSC.products.hotwater) == 1:
                        node_name = None
                    device_list_climate.append({'HA_DeviceType': 'HotWater', 'Hive_NodeID': product["id"], 'Hive_NodeName': node_name, "Hive_DeviceType": "HotWater"})
                    device_list_sensor.append({'HA_DeviceType': 'HotWater_State', 'Hive_NodeID': product["id"], 'Hive_NodeName': node_name, "Hive_DeviceType": "HotWater"})
                    device_list_sensor.append({'HA_DeviceType': 'HotWater_Mode', 'Hive_NodeID': product["id"], 'Hive_NodeName': node_name, "Hive_DeviceType": "HotWater"})
                    device_list_sensor.append({'HA_DeviceType': 'HotWater_Boost', 'Hive_NodeID': product["id"], 'Hive_NodeName': node_name, "Hive_DeviceType": "HotWater"})


        if len(HSC.devices.thermostat) > 0 or len(HSC.devices.sensors) > 0:
            all_devices = HSC.devices.thermostat + HSC.devices.sensors
            for a_device in all_devices:
                if ("id" in a_device and "state" in a_device and "name" in a_device["state"]):
                    node_name = a_device["state"]["name"]
                    if (a_device["type"] == "thermostatui" and len(HSC.devices.thermostat) == 1):
                        node_name = None
                    if "type" in a_device:
                        hive_device_type = a_device["type"]
                        device_list_sensor.append({'HA_DeviceType': 'Hive_Device_BatteryLevel', 'Hive_NodeID': a_device["id"], 'Hive_NodeName': node_name, "Hive_DeviceType": hive_device_type})


        if len(HSC.products.light) > 0:
            for product in HSC.products.light:
                if ("id" in product and "state" in product and "name" in product["state"]):
                    if "type" in product:
                        light_device_type = product["type"]
                        device_list_light.append({'HA_DeviceType': 'Hive_Device_Light', 'Hive_Light_DeviceType': light_device_type, 'Hive_NodeID': product["id"], 'Hive_NodeName': product["state"]["name"], "Hive_DeviceType": "Light"})
                        device_list_sensor.append({'HA_DeviceType': 'Hive_Device_Light_Mode', 'Hive_NodeID': product["id"], 'Hive_NodeName': product["state"]["name"], "Hive_DeviceType": light_device_type})


        if len(HSC.products.plug) > 0:
            for product in HSC.products.plug:
                if ("id" in product and "state" in product and "name" in product["state"]):
                    if "type" in product:
                        plug_device_type = product["type"]
                        device_list_plug.append({'HA_DeviceType': 'Hive_Device_Plug', 'Hive_Plug_DeviceType': plug_device_type, 'Hive_NodeID': product["id"], 'Hive_NodeName': product["state"]["name"], "Hive_DeviceType": "Switch"})
                        device_list_sensor.append({'HA_DeviceType': 'Hive_Device_Plug_Mode', 'Hive_NodeID': product["id"], 'Hive_NodeName': product["state"]["name"], "Hive_DeviceType": plug_device_type})

        if len(HSC.products.sensors) > 0:
            for product in HSC.products.sensors:
                if ("id" in product and "state" in product and "name" in product["state"]):
                    if "type" in product:
                        hive_sensor_device_type = product["type"]
                        device_list_binary_sensor.append({'HA_DeviceType': 'Hive_Device_Binary_Sensor', 'Hive_NodeID': product["id"], 'Hive_NodeName': product["state"]["name"], "Hive_DeviceType": hive_sensor_device_type})

#        if HSC.weather.nodeid == "HiveWeather":
#        device_list_sensor.append({'HA_DeviceType': 'Weather_OutsideTemperature', 'Hive_NodeID': HSC.weather.nodeid, 'Hive_NodeName': "Hive Weather"})

        device_list_all['device_list_sensor'] = device_list_sensor
        device_list_all['device_list_binary_sensor'] = device_list_binary_sensor
        device_list_all['device_list_climate'] = device_list_climate
        device_list_all['device_list_light'] = device_list_light
        device_list_all['device_list_plug'] = device_list_plug

        return device_list_all

    def test_use_file(self, devices, products):
        """Get latest data for Hive nodes."""
        get_nodes_successful = True

        UseFile = True
        if UseFile == True:
            HSC.file = True
            HSC.session_id = 'Test'



        tmp_devices_hub = []
        tmp_devices_thermostat = []
        tmp_devices_boiler_module = []
        tmp_devices_plug = []
        tmp_devices_light = []
        tmp_devices_sensors = []

        tmp_products_heating = []
        tmp_products_hotwater = []
        tmp_products_light = []
        tmp_products_plug = []
        tmp_products_sensors = []

        if devices != None:
            try_finished = False
            try:
                api_resp_d = {}
                api_resp_p = None
                api_resp_d = devices

                api_resp_p = api_resp_d

                for a_device in api_resp_p:
                    if "type" in a_device:
                        if a_device["type"] == "hub":
                            tmp_devices_hub.append(a_device)
                        if a_device["type"] == "thermostatui":
                            tmp_devices_thermostat.append(a_device)
                        if a_device["type"] == "boilermodule":
                            tmp_devices_boiler_module.append(a_device)
                        if a_device["type"] == "activeplug":
                            tmp_devices_plug.append(a_device)
                        if (a_device["type"] == "warmwhitelight" or
                                a_device["type"] == "tuneablelight" or
                                a_device["type"] == "colourtuneablelight"):
                            tmp_devices_light.append(a_device)
                        if (a_device["type"] == "motionsensor" or
                                a_device["type"] == "contactsensor"):
                            tmp_devices_sensors.append(a_device)

                try_finished = True
            except (IOError, RuntimeError, ZeroDivisionError):
                try_finished = False
            finally:
                if not try_finished:
                    try_finished = False

        if products != None:

            try_finished = False
            try:
                api_resp_d = {}
                api_resp_p = None
                api_resp_d = products

                api_resp_p = api_resp_d
                for a_product in api_resp_p:
                    if "type" in a_product:
                        if a_product["type"] == "heating":
                            tmp_products_heating.append(a_product)
                        if a_product["type"] == "hotwater":
                            tmp_products_hotwater.append(a_product)
                        if a_product["type"] == "activeplug":
                            tmp_products_plug.append(a_product)
                        if (a_product["type"] == "warmwhitelight" or
                                a_product["type"] == "tuneablelight" or
                                a_product["type"] == "colourtuneablelight"):
                            tmp_products_light.append(a_product)
                        if (a_product["type"] == "motionsensor" or
                                a_product["type"] == "contactsensor"):
                            tmp_products_sensors.append(a_product)
                try_finished = True
            except (IOError, RuntimeError, ZeroDivisionError):
                try_finished = False
            finally:
                if not try_finished:
                    try_finished = False

        try_finished = False
        try:
            if len(tmp_devices_hub) > 0:
                HSC.devices.hub = tmp_devices_hub
            if len(tmp_devices_thermostat) > 0:
                HSC.devices.thermostat = tmp_devices_thermostat
            if len(tmp_devices_boiler_module) > 0:
                HSC.devices.boiler_module = tmp_devices_boiler_module
            if len(tmp_devices_plug) > 0:
                HSC.devices.plug = tmp_devices_plug
            if len(tmp_devices_light) > 0:
                HSC.devices.light = tmp_devices_light
            if len(tmp_devices_sensors) > 0:
                HSC.devices.sensors = tmp_devices_sensors

            if len(tmp_products_heating) > 0:
                HSC.products.heating = tmp_products_heating
            if len(tmp_products_hotwater) > 0:
                HSC.products.hotwater = tmp_products_hotwater
            if len(tmp_products_plug) > 0:
                HSC.products.plug = tmp_products_plug
            if len(tmp_products_light) > 0:
                HSC.products.light = tmp_products_light
            if len(tmp_products_sensors) > 0:
                HSC.products.sensors = tmp_products_sensors

            try_finished = True
        except (IOError, RuntimeError, ZeroDivisionError):
                try_finished = False
        finally:
            if not try_finished:
                get_nodes_successful = False

        return get_nodes_successful


    class Heating():
        """Hive Switches."""
        def min_temperature(self, node_id):
            """Get heating minimum target temperature."""
            heating_min_temp_default = 5
            heating_min_temp_return = 0
            heating_min_temp_tmp = 0
            heating_min_temp_found = False

            heating_min_temp_tmp = heating_min_temp_default

            current_node_attribute = "Heating_Min_Temperature_" + node_id

            if heating_min_temp_found:
                NODE_ATTRIBS[current_node_attribute] = heating_min_temp_tmp
                heating_min_temp_return = heating_min_temp_tmp
            else:
                if current_node_attribute in NODE_ATTRIBS:
                    heating_min_temp_return = NODE_ATTRIBS.get(current_node_attribute)
                else:
                    heating_min_temp_return = heating_min_temp_default

            return heating_min_temp_return


        def max_temperature(self, node_id):
            """Get heating maximum target temperature."""
            heating_max_temp_default = 32
            heating_max_temp_return = 0
            heating_max_temp_tmp = 0
            heating_max_temp_found = False

            heating_max_temp_tmp = heating_max_temp_default

            current_node_attribute = "Heating_Max_Temperature_" + node_id

            if heating_max_temp_found:
                NODE_ATTRIBS[current_node_attribute] = heating_max_temp_tmp
                heating_max_temp_return = heating_max_temp_tmp
            else:
                if current_node_attribute in NODE_ATTRIBS:
                    heating_max_temp_return = NODE_ATTRIBS.get(current_node_attribute)
                else:
                    heating_max_temp_return = heating_max_temp_default

            return heating_max_temp_return


        def current_temperature(self, node_id):
            """Get heating current temperature."""
            node_index = -1

            current_temp_return = 0
            current_temp_tmp = 0
            current_temp_found = False

            current_node_attribute = "Heating_CurrentTemp_" + node_id

            if len(HSC.products.heating) > 0:
                for current_node_index in range(0, len(HSC.products.heating)):
                    if "id" in HSC.products.heating[current_node_index]:
                        if HSC.products.heating[current_node_index]["id"] == node_id:
                            node_index = current_node_index
                            break

                if node_index != -1:
                    if "props" in HSC.products.heating[node_index]:
                        if "temperature" in HSC.products.heating[node_index]["props"]:
                            current_temp_tmp = (HSC.products.heating[node_index]
                                                ["props"]["temperature"])
                            current_temp_found = True

            if current_temp_found:
                NODE_ATTRIBS[current_node_attribute] = current_temp_tmp
                current_temp_return = current_temp_tmp
            else:
                if current_node_attribute in NODE_ATTRIBS:
                    current_temp_return = NODE_ATTRIBS.get(current_node_attribute)
                else:
                    current_temp_return = -1000

            if current_temp_return != -1000:
                if node_id in HSC.data.minmax:
                    if (HSC.data.minmax[node_id]['TodayDate'] != datetime.date(datetime.now())):
                        HSC.data.minmax[node_id]['TodayMin'] = 1000
                        HSC.data.minmax[node_id]['TodayMax'] = -1000
                        HSC.data.minmax[node_id]['TodayDate'] = datetime.date(datetime.now())

                    if (current_temp_return < HSC.data.minmax[node_id]['TodayMin']):
                        HSC.data.minmax[node_id]['TodayMin'] = current_temp_return

                    if (current_temp_return > HSC.data.minmax[node_id]['TodayMax']):
                        HSC.data.minmax[node_id]['TodayMax'] = current_temp_return

                    if (current_temp_return < HSC.data.minmax[node_id]['RestartMin']):
                        HSC.data.minmax[node_id]['RestartMin'] = current_temp_return

                    if (current_temp_return > HSC.data.minmax[node_id]['RestartMax']):
                        HSC.data.minmax[node_id]['RestartMax'] = current_temp_return
                else:
                    current_node_max_min_data = {}
                    current_node_max_min_data['TodayMin'] = current_temp_return
                    current_node_max_min_data['TodayMax'] = current_temp_return
                    current_node_max_min_data['TodayDate'] = datetime.date(datetime.now())
                    current_node_max_min_data['RestartMin'] = current_temp_return
                    current_node_max_min_data['RestartMax'] = current_temp_return
                    HSC.data.minmax[node_id] = current_node_max_min_data
            else:
                current_temp_return = 0

            return current_temp_return

        def minmax_temperatures(self, node_id):
            if node_id in HSC.data.minmax:
                return HSC.data.minmax[node_id]
            else:
                return None

        def get_target_temperature(self, node_id):
            """Get heating target temperature."""
            node_index = -1

            heating_target_temp_return = 0
            heating_target_temp_tmp = 0
            heating_target_temp_found = False

            current_node_attribute = "Heating_TargetTemp_" + node_id

            if len(HSC.products.heating) > 0:
                for current_node_index in range(0, len(HSC.products.heating)):
                    if "id" in HSC.products.heating[current_node_index]:
                        if HSC.products.heating[current_node_index]["id"] == node_id:
                            node_index = current_node_index
                            break

                if node_index != -1:
                    heating_mode_current = Pyhiveapi.Heating.get_mode(self, node_id)
                    if heating_mode_current == "SCHEDULE":
                        if ('props' in HSC.products.heating[node_index] and
                                'scheduleOverride' in
                                HSC.products.heating[node_index]["props"]):
                            if (HSC.products.heating[node_index]
                                    ["props"]["scheduleOverride"]):
                                if ("state" in HSC.products.heating[node_index] and
                                        "target" in HSC.products.heating[node_index]
                                        ["state"]):
                                    heating_target_temp_tmp = (HSC.products.heating
                                                               [node_index]["state"]
                                                               ["target"])
                                    heating_target_temp_found = True
                            else:
                                snan = (
                                    Pyhiveapi.p_get_schedule_now_next_later(self, HSC.products.heating[node_index]["state"]["schedule"]))
                                if 'now' in snan:
                                    if ('value' in snan["now"] and
                                            'target' in snan["now"]
                                            ["value"]):
                                        heating_target_temp_tmp = (snan["now"]
                                                                   ["value"]
                                                                   ["target"])
                                        heating_target_temp_found = True
                    else:
                        if ("state" in HSC.products.heating[node_index] and "target"
                                in HSC.products.heating[node_index]["state"]):
                            heating_target_temp_tmp = \
                                HSC.products.heating[node_index]["state"]["target"]
                            heating_target_temp_found = True

            if heating_target_temp_found:
                NODE_ATTRIBS[current_node_attribute] = heating_target_temp_tmp
                heating_target_temp_return = heating_target_temp_tmp
            else:
                if current_node_attribute in NODE_ATTRIBS:
                    heating_target_temp_return = \
                        NODE_ATTRIBS.get(current_node_attribute)
                else:
                    heating_target_temp_return = 0

            return heating_target_temp_return


        def get_mode(self, node_id):
            """Get heating current mode."""
            node_index = -1

            mode_return = "UNKNOWN"
            mode_tmp = "UNKNOWN"
            mode_found = False

            current_node_attribute = "Heating_Mode_" + node_id

            if len(HSC.products.heating) > 0:
                for current_node_index in range(0, len(HSC.products.heating)):
                    if "id" in HSC.products.heating[current_node_index]:
                        if HSC.products.heating[current_node_index]["id"] == node_id:
                            node_index = current_node_index
                            break

                if node_index != -1:
                    if ("state" in HSC.products.heating[node_index] and
                            "mode" in HSC.products.heating[node_index]["state"]):
                        mode_tmp = HSC.products.heating[node_index]["state"]["mode"]
                        if mode_tmp == "BOOST":
                            if ("props" in HSC.products.heating[node_index] and
                                    "previous" in
                                    HSC.products.heating[node_index]["props"] and
                                    "mode" in
                                    HSC.products.heating[node_index]
                                    ["props"]["previous"]):
                                mode_tmp = (HSC.products.heating[node_index]
                                            ["props"]["previous"]["mode"])
                        mode_found = True

            if mode_found:
                NODE_ATTRIBS[current_node_attribute] = mode_tmp
                mode_return = mode_tmp
            else:
                if current_node_attribute in NODE_ATTRIBS:
                    mode_return = NODE_ATTRIBS.get(current_node_attribute)
                else:
                    mode_return = "UNKNOWN"

            return mode_return


        def get_state(self, node_id):
            """Get heating current state."""
            heating_state_return = "OFF"
            heating_state_tmp = "OFF"
            heating_state_found = False

            current_node_attribute = "Heating_State_" + node_id

            if len(HSC.products.heating) > 0:
                temperature_current = Pyhiveapi.Heating.current_temperature(self, node_id)
                temperature_target = Pyhiveapi.Heating.get_target_temperature(self, node_id)
                heating_boost = Pyhiveapi.Heating.get_boost(self, node_id)
                heating_mode = Pyhiveapi.Heating.get_mode(self, node_id)

                if (heating_mode == "SCHEDULE" or
                        heating_mode == "MANUAL" or
                        heating_boost == "ON"):
                    if temperature_current < temperature_target:
                        heating_state_tmp = "ON"
                        heating_state_found = True
                    else:
                        heating_state_tmp = "OFF"
                        heating_state_found = True
                else:
                    heating_state_tmp = "OFF"
                    heating_state_found = True

            if heating_state_found:
                NODE_ATTRIBS[current_node_attribute] = heating_state_tmp
                heating_state_return = heating_state_tmp
            else:
                if current_node_attribute in NODE_ATTRIBS:
                    heating_state_return = NODE_ATTRIBS.get(current_node_attribute)
                else:
                    heating_state_return = "UNKNOWN"

            return heating_state_return


        def get_boost(self, node_id):
            """Get heating boost current status."""
            node_index = -1

            heating_boost_return = "UNKNOWN"
            heating_boost_tmp = "UNKNOWN"
            heating_boost_found = False

            current_node_attribute = "Heating_Boost_" + node_id

            if len(HSC.products.heating) > 0:
                for current_node_index in range(0, len(HSC.products.heating)):
                    if "id" in HSC.products.heating[current_node_index]:
                        if HSC.products.heating[current_node_index]["id"] == node_id:
                            node_index = current_node_index
                            break

                if node_index != -1:
                    if ("state" in HSC.products.heating[node_index] and
                            "boost" in HSC.products.heating[node_index]["state"]):
                        heating_boost_tmp = (HSC.products.heating[node_index]
                                             ["state"]["boost"])
                        if heating_boost_tmp is None:
                            heating_boost_tmp = "OFF"
                        else:
                            heating_boost_tmp = "ON"
                        heating_boost_found = True

            if heating_boost_found:
                NODE_ATTRIBS[current_node_attribute] = heating_boost_tmp
                heating_boost_return = heating_boost_tmp
            else:
                if current_node_attribute in NODE_ATTRIBS:
                    heating_boost_return = NODE_ATTRIBS.get(current_node_attribute)
                else:
                    heating_boost_return = "UNKNOWN"

            return heating_boost_return


        def get_boost_time(self, node_id):
            """Get heating boost time remaining."""
            heating_boost = "UNKNOWN"

            if Pyhiveapi.Heating.get_boost(self, node_id) == "ON":
                node_index = -1

                heating_boost_tmp = "UNKNOWN"
                heating_boost_found = False

                if len(HSC.products.heating) > 0:
                    for current_node_index in range(0, len(HSC.products.heating)):
                        if "id" in HSC.products.heating[current_node_index]:
                            if (HSC.products.heating[current_node_index]["id"] == node_id):
                                node_index = current_node_index
                                break

                    if node_index != -1:
                        if ("state" in HSC.products.heating[node_index] and "boost" in HSC.products.heating[node_index]["state"]):
                            heating_boost_tmp = (HSC.products.heating[node_index]["state"]["boost"])
                            heating_boost_found = True

                if heating_boost_found:
                    heating_boost = heating_boost_tmp

            return heating_boost


        def get_operation_modes(self, node_id):
            """Get heating list of possible modes."""
            heating_operation_list = ["SCHEDULE", "MANUAL", "OFF"]
            return heating_operation_list


        def get_schedule_now_next_later(self, node_id):
            """Hive get heating schedule now, next and later."""
            heating_mode_current = Pyhiveapi.Heating.get_mode(self, node_id)

            snan = None

            if heating_mode_current == "SCHEDULE":
                node_index = -1

                if len(HSC.products.heating) > 0:
                    for current_node_index in range(0, len(HSC.products.heating)):
                        if "id" in HSC.products.heating[current_node_index]:
                            if HSC.products.heating[current_node_index]["id"] == node_id:
                                node_index = current_node_index
                                break

                if node_index != -1:
                    snan = Pyhiveapi.p_get_schedule_now_next_later(self, HSC.products.heating[node_index]["state"]["schedule"])
                else:
                    snan = None
            else:
                snan = None

            return snan


        def set_target_temperature(self, node_id, new_temperature):
            """Set heating target temperature."""
            Pyhiveapi.check_hive_api_logon(self)

            set_temperature_success = False
            api_resp_d = {}
            api_resp = ""

            if HSC.session_id is not None:
                node_index = -1
                if len(HSC.products.heating) > 0:
                    for current_node_index in range(0, len(HSC.products.heating)):
                        if "id" in HSC.products.heating[current_node_index]:
                            if (HSC.products.heating[current_node_index]["id"] == node_id):
                                node_index = current_node_index
                                break

                    if node_index != -1:
                        if "id" in HSC.products.heating[node_index]:
                            json_string_content = ('{"target":' + str(new_temperature) + '}')

                            hive_api_url = (HIVE_API.urls.nodes + "/heating/" + HSC.products.heating[node_index]["id"])
                            api_resp_d = Pyhiveapi.hive_api_json_call(self, "POST", hive_api_url, json_string_content, False)

                            api_resp = api_resp_d['original']

                            if str(api_resp) == "<Response [200]>":
                                Pyhiveapi.hive_api_get_nodes(self, node_id)
                                set_temperature_success = True

            return set_temperature_success


        def set_mode(self, node_id, new_mode):
            """Set heating mode."""
            Pyhiveapi.check_hive_api_logon(self)

            set_mode_success = False
            api_resp_d = {}
            api_resp = ""

            if HSC.session_id is not None:
                node_index = -1
                if len(HSC.products.heating) > 0:
                    for current_node_index in range(0, len(HSC.products.heating)):
                        if "id" in HSC.products.heating[current_node_index]:
                            if (HSC.products.heating[current_node_index]["id"] == node_id):
                                node_index = current_node_index
                                break

                    if node_index != -1:
                        if "id" in HSC.products.heating[node_index]:
                            if new_mode == "SCHEDULE":
                                json_string_content = '{"mode": "SCHEDULE"}'
                            elif new_mode == "MANUAL":
                                json_string_content = '{"mode": "MANUAL"}'
                            elif new_mode == "OFF":
                                json_string_content = '{"mode": "OFF"}'

                            if (new_mode == "SCHEDULE" or new_mode == "MANUAL" or new_mode == "OFF"):
                                hive_api_url = (HIVE_API.urls.nodes + "/heating/" + HSC.products.heating[node_index]["id"])
                                api_resp_d = Pyhiveapi.hive_api_json_call(self, "POST", hive_api_url, json_string_content, False)

                                api_resp = api_resp_d['original']

                                if str(api_resp) == "<Response [200]>":
                                    Pyhiveapi.hive_api_get_nodes(self, node_id)
                                    set_mode_success = True

            return set_mode_success


        def turn_boost_on(self, node_id, length_minutes, target_temperature):
            """Turn heating boost on."""
            set_boost_success = False
            heating_node_found = False
            api_resp_d = {}
            api_resp = ""

            if length_minutes > 0 and target_temperature >= self.min_temperature(node_id) and target_temperature <= self.max_temperature(node_id):
                heating_node_found = False
            else:
                return False

            for a_heating in HSC.products.heating:
                if "id" in a_heating:
                    if a_heating["id"] == node_id:
                        heating_node_found = True
                        break

            Pyhiveapi.check_hive_api_logon(self)

            if heating_node_found:
                json_string_content = '{"mode": "BOOST", "boost": ' + str(length_minutes) + ', "target": ' + str(target_temperature) + '}'
                hive_api_url = (HIVE_API.urls.nodes + "/heating/" + node_id)
                api_resp_d = Pyhiveapi.hive_api_json_call(self, "POST", hive_api_url, json_string_content, False)

                api_resp = api_resp_d['original']

                if str(api_resp) == "<Response [200]>":
                    Pyhiveapi.hive_api_get_nodes(self, node_id)
                    set_boost_success = True

            return set_boost_success


        def turn_boost_off(self, node_id):
            """Turn heating boost off."""
            set_boost_success = False
            heating_node_found = False
            api_resp_d = {}
            api_resp = ""

            for a_heating in HSC.products.heating:
                if "id" in a_heating:
                    if a_heating["id"] == node_id:
                        heating_node_found = True
                        break

            Pyhiveapi.check_hive_api_logon(self)

            if heating_node_found:
                Pyhiveapi.hive_api_get_nodes(self, node_id)
                boost_state = self.get_boost(node_id)

                node_index = -1
                for current_node_index in range(0, len(HSC.products.heating)):
                    if "id" in HSC.products.heating[current_node_index]:
                        if (HSC.products.heating[current_node_index]["id"] == node_id):
                            node_index = current_node_index
                            break

                if node_index != -1 and boost_state == "ON":
                    send_previous_mode = ''
                    send_previous_temperature = ''

                    if ("props" in HSC.products.heating[node_index] and "previous" in HSC.products.heating[node_index]["props"] and "mode" in HSC.products.heating[node_index]["props"]["previous"]):
                        previous_mode = HSC.products.heating[node_index]["props"]["previous"]["mode"]
                        send_previous_mode = '"mode": "' + str(previous_mode) + '"'
                        if previous_mode == "MANUAL":
                            previous_temperature = HSC.products.heating[node_index]["props"]["previous"]["target"]
                            send_previous_temperature  = ', "target": ' + str(previous_temperature)

                        json_string_content = '{' + send_previous_mode + send_previous_temperature + '}'
                        hive_api_url = (HIVE_API.urls.nodes + "/heating/" + node_id)
                        api_resp_d = Pyhiveapi.hive_api_json_call(self, "POST", hive_api_url, json_string_content, False)

                        api_resp = api_resp_d['original']

                    if str(api_resp) == "<Response [200]>":
                        Pyhiveapi.hive_api_get_nodes(self, node_id)
                        set_boost_success = True

            return set_boost_success


    class Hotwater():
        """Hive Hotwater."""
        def get_mode(self, node_id):
            """Get hot water current mode."""
            node_index = -1

            hotwater_mode_return = "UNKNOWN"
            hotwater_mode_tmp = "UNKNOWN"
            hotwater_mode_found = False

            current_node_attribute = "HotWater_Mode_" + node_id

            if len(HSC.products.hotwater) > 0:
                for current_node_index in range(0, len(HSC.products.hotwater)):
                    if "id" in HSC.products.hotwater[current_node_index]:
                        if HSC.products.hotwater[current_node_index]["id"] == node_id:
                            node_index = current_node_index
                            break

                if node_index != -1:
                    if ("state" in HSC.products.hotwater[node_index] and
                            "mode" in HSC.products.hotwater[node_index]["state"]):
                        hotwater_mode_tmp = (HSC.products.hotwater[node_index]
                                             ["state"]["mode"])
                        if hotwater_mode_tmp == "BOOST":
                            if ("props" in HSC.products.hotwater[node_index] and
                                    "previous" in
                                    HSC.products.hotwater[node_index]["props"] and
                                    "mode" in
                                    HSC.products.hotwater[node_index]
                                    ["props"]["previous"]):
                                hotwater_mode_tmp = (HSC.products.hotwater[node_index]
                                                     ["props"]["previous"]["mode"])
                        elif hotwater_mode_tmp == "MANUAL":
                            hotwater_mode_tmp = "ON"
                        hotwater_mode_found = True

            if hotwater_mode_found:
                NODE_ATTRIBS[current_node_attribute] = hotwater_mode_tmp
                hotwater_mode_return = hotwater_mode_tmp
            else:
                if current_node_attribute in NODE_ATTRIBS:
                    hotwater_mode_return = NODE_ATTRIBS.get(current_node_attribute)
                else:
                    hotwater_mode_return = "UNKNOWN"

            return hotwater_mode_return


        def get_operation_modes(self, node_id):
            """Get heating list of possible modes."""
            hotwater_operation_list = ["SCHEDULE", "ON", "OFF"]
            return hotwater_operation_list


        def get_boost(self, node_id):
            """Get hot water current boost status."""
            node_index = -1

            hotwater_boost_return = "UNKNOWN"
            hotwater_boost_tmp = "UNKNOWN"
            hotwater_boost_found = False

            current_node_attribute = "HotWater_Boost_" + node_id

            if len(HSC.products.hotwater) > 0:
                for current_node_index in range(0, len(HSC.products.hotwater)):
                    if "id" in HSC.products.hotwater[current_node_index]:
                        if HSC.products.hotwater[current_node_index]["id"] == node_id:
                            node_index = current_node_index
                            break

                if node_index != -1:
                    if ("state" in HSC.products.hotwater[node_index] and
                            "boost" in HSC.products.hotwater[node_index]["state"]):
                        hotwater_boost_tmp = (HSC.products.hotwater[node_index]
                                              ["state"]["boost"])
                        if hotwater_boost_tmp is None:
                            hotwater_boost_tmp = "OFF"
                        else:
                            hotwater_boost_tmp = "ON"
                        hotwater_boost_found = True

            if hotwater_boost_found:
                NODE_ATTRIBS[current_node_attribute] = hotwater_boost_tmp
                hotwater_boost_return = hotwater_boost_tmp
            else:
                if current_node_attribute in NODE_ATTRIBS:
                    hotwater_boost_return = NODE_ATTRIBS.get(current_node_attribute)
                else:
                    hotwater_boost_return = "UNKNOWN"

            return hotwater_boost_return


        def get_boost_time(self, node_id):
            """Get hotwater boost time remaining."""
            hotwater_boost = "UNKNOWN"

            if Pyhiveapi.Hotwater.get_boost(self, node_id) == "ON":
                node_index = -1

                hotwater_boost_tmp = "UNKNOWN"
                hotwater_boost_found = False

                if len(HSC.products.hotwater) > 0:
                    for current_node_index in range(0, len(HSC.products.hotwater)):
                        if "id" in HSC.products.hotwater[current_node_index]:
                            if (HSC.products.hotwater[current_node_index]["id"] == node_id):
                                node_index = current_node_index
                                break

                    if node_index != -1:
                        if ("state" in HSC.products.hotwater[node_index] and "boost" in HSC.products.hotwater[node_index]["state"]):
                            hotwater_boost_tmp = (HSC.products.hotwater[node_index]["state"]["boost"])
                            hotwater_boost_found = True

                if hotwater_boost_found:
                    hotwater_boost = hotwater_boost_tmp

            return hotwater_boost


        def get_state(self, node_id):
            """Get hot water current state."""
            node_index = -1

            state_return = "OFF"
            state_tmp = "OFF"
            state_found = False
            mode_current = Pyhiveapi.Hotwater.get_mode(self, node_id)

            current_node_attribute = "HotWater_State_" + node_id

            if len(HSC.products.hotwater) > 0:
                for current_node_index in range(0, len(HSC.products.hotwater)):
                    if "id" in HSC.products.hotwater[current_node_index]:
                        if HSC.products.hotwater[current_node_index]["id"] == node_id:
                            node_index = current_node_index
                            break

                if node_index != -1:
                    if ("state" in HSC.products.hotwater[node_index] and
                            "status" in HSC.products.hotwater[node_index]["state"]):
                        state_tmp = (HSC.products.hotwater[node_index]
                                     ["state"]["status"])
                        if state_tmp is None:
                            state_tmp = "OFF"
                        else:
                            if mode_current == "SCHEDULE":
                                if Pyhiveapi.Hotwater.get_boost(self, node_id) == "ON":
                                    state_tmp = "ON"
                                    state_found = True
                                else:
                                    if ("state" in
                                            HSC.products.hotwater[node_index] and
                                            "schedule" in
                                            HSC.products.hotwater[node_index]
                                            ["state"]):
                                        snan = Pyhiveapi.p_get_schedule_now_next_later(self, HSC.products.hotwater[node_index]["state"]["schedule"])
                                        if 'now' in snan:
                                            if ('value' in snan["now"] and
                                                    'status' in snan["now"]["value"]):
                                                state_tmp = (snan["now"]["value"]
                                                             ["status"])
                                                state_found = True
                            else:
                                state_found = True

            if state_found:
                NODE_ATTRIBS[current_node_attribute] = state_tmp
                state_return = state_tmp
            else:
                if current_node_attribute in NODE_ATTRIBS:
                    state_return = NODE_ATTRIBS.get(current_node_attribute)
                else:
                    state_return = "UNKNOWN"

            return state_return


        def get_schedule_now_next_later(self, node_id):
            """Hive get hotwater schedule now, next and later."""
            hotwater_mode_current = Pyhiveapi.Hotwater.get_mode(self, node_id)

            snan = None

            if hotwater_mode_current == "SCHEDULE":
                node_index = -1

                if len(HSC.products.hotwater) > 0:
                    for current_node_index in range(0, len(HSC.products.hotwater)):
                        if "id" in HSC.products.hotwater[current_node_index]:
                            if HSC.products.hotwater[current_node_index]["id"] == node_id:
                                node_index = current_node_index
                                break

                if node_index != -1:
                    snan = Pyhiveapi.p_get_schedule_now_next_later(self, HSC.products.hotwater[node_index]["state"]["schedule"])
                else:
                    snan = None
            else:
                snan = None

            return snan


        def set_mode(self, node_id, new_mode):
            """Set hot water mode."""
            Pyhiveapi.check_hive_api_logon(self)

            set_mode_success = False
            api_resp_d = {}
            api_resp = ""

            if HSC.session_id is not None:
                node_index = -1
                if len(HSC.products.hotwater) > 0:
                    for current_node_index in range(0, len(HSC.products.hotwater)):
                        if "id" in HSC.products.hotwater[current_node_index]:
                            if (HSC.products.hotwater[current_node_index]["id"] == node_id):
                                node_index = current_node_index
                                break

                    if node_index != -1:
                        if "id" in HSC.products.hotwater[node_index]:
                            if new_mode == "SCHEDULE":
                                json_string_content = '{"mode": "SCHEDULE"}'
                            elif new_mode == "ON":
                                json_string_content = '{"mode": "MANUAL"}'
                            elif new_mode == "OFF":
                                json_string_content = '{"mode": "OFF"}'

                            if (new_mode == "SCHEDULE" or new_mode == "ON" or new_mode == "OFF"):
                                hive_api_url = (HIVE_API.urls.nodes + "/hotwater/" + HSC.products.hotwater[node_index]["id"])
                                api_resp_d = Pyhiveapi.hive_api_json_call(self, "POST", hive_api_url, json_string_content, False)

                                api_resp = api_resp_d['original']

                                if str(api_resp) == "<Response [200]>":
                                    Pyhiveapi.hive_api_get_nodes(self, node_id)
                                    set_mode_success = True

            return set_mode_success


        def turn_boost_on(self, node_id, length_minutes):
            """Turn hot water boost on."""
            set_boost_success = False
            hotwater_node_found = False
            api_resp_d = {}
            api_resp = ""

            if length_minutes > 0:
                hotwater_node_found = False
            else:
                return False

            for a_hotwater in HSC.products.hotwater:
                if "id" in a_hotwater:
                    if a_hotwater["id"] == node_id:
                        hotwater_node_found = True
                        break

            Pyhiveapi.check_hive_api_logon(self)

            if hotwater_node_found:
                json_string_content = '{"mode": "BOOST", "boost": ' + str(length_minutes) + '}'
                hive_api_url = (HIVE_API.urls.nodes + "/hotwater/" + node_id)
                api_resp_d = Pyhiveapi.hive_api_json_call(self, "POST", hive_api_url, json_string_content, False)

                api_resp = api_resp_d['original']

                if str(api_resp) == "<Response [200]>":
                    Pyhiveapi.hive_api_get_nodes(self, node_id)
                    set_boost_success = True

            return set_boost_success


        def turn_boost_off(self, node_id):
            """Turn hot water boost off."""
            set_boost_success = False
            hotwater_node_found = False
            api_resp_d = {}
            api_resp = ""

            for a_hotwater in HSC.products.hotwater:
                if "id" in a_hotwater:
                    if a_hotwater["id"] == node_id:
                        hotwater_node_found = True
                        break

            Pyhiveapi.check_hive_api_logon(self)

            if hotwater_node_found:
                Pyhiveapi.hive_api_get_nodes(self, node_id)
                boost_state = self.get_boost(node_id)

                node_index = -1
                for current_node_index in range(0, len(HSC.products.hotwater)):
                    if "id" in HSC.products.hotwater[current_node_index]:
                        if (HSC.products.hotwater[current_node_index]["id"] == node_id):
                            node_index = current_node_index
                            break

                if node_index != -1 and boost_state == "ON":
                    send_previous_mode = ''

                    if ("props" in HSC.products.hotwater[node_index] and "previous" in HSC.products.hotwater[node_index]["props"] and "mode" in HSC.products.hotwater[node_index]["props"]["previous"]):
                        previous_mode = HSC.products.hotwater[node_index]["props"]["previous"]["mode"]
                        send_previous_mode = '"mode": "' + str(previous_mode) + '"'

                        json_string_content = '{' + send_previous_mode + '}'
                        hive_api_url = (HIVE_API.urls.nodes + "/hotwater/" + node_id)
                        api_resp_d = Pyhiveapi.hive_api_json_call(self, "POST", hive_api_url, json_string_content, False)

                        api_resp = api_resp_d['original']

                    if str(api_resp) == "<Response [200]>":
                        Pyhiveapi.hive_api_get_nodes(self, node_id)
                        set_boost_success = True

            return set_boost_success


    class Light():
        """Hive Lights."""
        def get_state(self, node_id):
            """Get light current state."""
            node_index = -1

            light_state_return = "UNKNOWN"
            light_state_tmp = "UNKNOWN"
            light_state_found = False

            current_node_attribute = "Light_State_" + node_id

            if len(HSC.products.light) > 0:
                for current_node_index in range(0, len(HSC.products.light)):
                    if "id" in HSC.products.light[current_node_index]:
                        if HSC.products.light[current_node_index][
                            "id"] == node_id:
                            node_index = current_node_index
                            break

                if node_index != -1:
                    if ("state" in HSC.products.light[
                        node_index] and "status" in
                        HSC.products.light[node_index]["state"]):
                        light_state_tmp = (HSC.products.light[node_index]
                                           ["state"]["status"])
                        light_state_found = True

            if light_state_found:
                NODE_ATTRIBS[current_node_attribute] = light_state_tmp
                light_state_return = light_state_tmp
            else:
                if current_node_attribute in NODE_ATTRIBS:
                    light_state_return = NODE_ATTRIBS.get(
                        current_node_attribute)
                else:
                    light_state_return = "UNKNOWN"

            light_state_return_b = False

            if light_state_return == "ON":
                light_state_return_b = True

            return light_state_return_b

        def get_brightness(self, node_id):
            """Get light current brightness."""
            node_index = -1

            tmp_brightness_return = 0
            light_brightness_return = 0
            light_brightness_tmp = 0
            light_brightness_found = False

            current_node_attribute = "Light_Brightness_" + node_id

            if len(HSC.products.light) > 0:
                for current_node_index in range(0, len(HSC.products.light)):
                    if "id" in HSC.products.light[current_node_index]:
                        if HSC.products.light[current_node_index][
                            "id"] == node_id:
                            node_index = current_node_index
                            break

                if node_index != -1:
                    if ("state" in HSC.products.light[
                        node_index] and "brightness" in
                        HSC.products.light[node_index]["state"]):
                        light_brightness_tmp = (HSC.products.light[node_index]
                                                ["state"]["brightness"])
                        light_brightness_found = True

            if light_brightness_found:
                NODE_ATTRIBS[current_node_attribute] = light_brightness_tmp
                tmp_brightness_return = light_brightness_tmp
                light_brightness_return = ((tmp_brightness_return / 100) * 255)
            else:
                if current_node_attribute in NODE_ATTRIBS:
                    tmp_brightness_return = NODE_ATTRIBS.get(
                        current_node_attribute)
                    light_brightness_return = (
                    (tmp_brightness_return / 100) * 255)
                else:
                    light_brightness_return = 0

            return light_brightness_return

        def get_min_color_temp(self, node_id):
            """Get light minimum color temperature."""
            node_index = -1

            light_min_color_temp_tmp = 0
            light_min_color_temp_return = 0
            light_min_color_temp_found = False

            node_attrib = "Light_Min_color_Temp_" + node_id

            if len(HSC.products.light) > 0:
                for current_node_index in range(0, len(HSC.products.light)):
                    if "id" in HSC.products.light[current_node_index]:
                        if HSC.products.light[current_node_index][
                            "id"] == node_id:
                            node_index = current_node_index
                            break

                if node_index != -1:
                    if ("props" in HSC.products.light[node_index] and
                                "colourTemperature" in
                                HSC.products.light[node_index][
                                    "props"] and "max" in
                        HSC.products.light[node_index]
                        ["props"]["colourTemperature"]):
                        light_min_color_temp_tmp = (
                        HSC.products.light[node_index]
                        ["props"]
                        ["colourTemperature"]["max"])
                        light_min_color_temp_found = True

            if light_min_color_temp_found:
                NODE_ATTRIBS[node_attrib] = light_min_color_temp_tmp
                light_min_color_temp_return = round(
                    (1 / light_min_color_temp_tmp)
                    * 1000000)
            else:
                if node_attrib in NODE_ATTRIBS:
                    light_min_color_temp_return = (
                    NODE_ATTRIBS.get(node_attrib))
                else:
                    light_min_color_temp_return = 0

            return light_min_color_temp_return

        def get_max_color_temp(self, node_id):
            """Get light maximum color temperature."""
            node_index = -1

            light_max_color_temp_tmp = 0
            light_max_color_temp_return = 0
            light_max_color_temp_found = False

            node_attrib = "Light_Max_color_Temp_" + node_id

            if len(HSC.products.light) > 0:
                for current_node_index in range(0, len(HSC.products.light)):
                    if "id" in HSC.products.light[current_node_index]:
                        if HSC.products.light[current_node_index][
                            "id"] == node_id:
                            node_index = current_node_index
                            break

                if node_index != -1:
                    if ("props" in HSC.products.light[node_index] and
                                "colourTemperature" in
                                HSC.products.light[node_index]["props"] and
                                "min" in
                                HSC.products.light[node_index]["props"]
                                ["colourTemperature"]):
                        light_max_color_temp_tmp = (
                        HSC.products.light[node_index]
                        ["props"]["colourTemperature"]
                        ["min"])
                        light_max_color_temp_found = True

            if light_max_color_temp_found:
                NODE_ATTRIBS[node_attrib] = light_max_color_temp_tmp
                light_max_color_temp_return = round(
                    (1 / light_max_color_temp_tmp)
                    * 1000000)
            else:
                if node_attrib in NODE_ATTRIBS:
                    light_max_color_temp_return = NODE_ATTRIBS.get(node_attrib)
                else:
                    light_max_color_temp_return = 0

            return light_max_color_temp_return

        def get_color_temp(self, node_id):
            """Get light current color temperature."""
            node_index = -1

            light_color_temp_tmp = 0
            light_color_temp_return = 0
            light_color_temp_found = False

            current_node_attribute = "Light_Color_Temp_" + node_id

            if len(HSC.products.light) > 0:
                for current_node_index in range(0, len(HSC.products.light)):
                    if "id" in HSC.products.light[current_node_index]:
                        if HSC.products.light[current_node_index][
                            "id"] == node_id:
                            node_index = current_node_index
                            break

                if node_index != -1:
                    if ("state" in HSC.products.light[node_index] and
                                "colourTemperature" in
                                HSC.products.light[node_index]["state"]):
                        light_color_temp_tmp = (HSC.products.light[node_index]
                                                ["state"]["colourTemperature"])
                        light_color_temp_found = True

            if light_color_temp_found:
                NODE_ATTRIBS[current_node_attribute] = light_color_temp_tmp
                light_color_temp_return = round(
                    (1 / light_color_temp_tmp) * 1000000)
            else:
                if current_node_attribute in NODE_ATTRIBS:
                    light_color_temp_return = NODE_ATTRIBS.get(
                        current_node_attribute)
                else:
                    light_color_temp_return = 0

            return light_color_temp_return

        def get_color(self,node_id):
            """Get color"""
            node_index = -1

            light_color_hue_tmp = 0
            light_color_saturation_tmp = 0
            light_color_value_tmp = 0
            rgb = 0
            light_color_return = 0
            light_color_found = False

            current_node_attribute = "Light_Color_" + node_id

            if len(HSC.products.light) > 0:
                for current_node_index in range(0, len(HSC.products.light)):
                    if "id" in HSC.products.light[current_node_index]:
                        if HSC.products.light[current_node_index][
                            "id"] == node_id:
                            node_index = current_node_index
                            break

                if node_index != -1:
                    light_color_hue_tmp = (HSC.products.light[node_index]["state"]["hue"])
                    light_color_saturation_tmp = (HSC.products.light[node_index]["state"]["saturation"])
                    light_color_value_tmp = (HSC.products.light[node_index]["state"]["value"])
                    light_color_found = True

            if light_color_found:
                h = light_color_hue_tmp / 360
                s = light_color_saturation_tmp / 100
                v = light_color_value_tmp / 100
                rgb = tuple(int(i * 255) for i in colorsys.hsv_to_rgb(h, s, v))
                NODE_ATTRIBS[current_node_attribute] = rgb
                light_color_return = rgb
            else:
                if current_node_attribute in NODE_ATTRIBS:
                    light_color_return = NODE_ATTRIBS.get(
                        current_node_attribute)
                else:
                    light_color_return = 0

            return light_color_return

        def turn_off(self, node_id):
            """Set light to turn off."""
            Pyhiveapi.check_hive_api_logon(self)

            node_index = -1

            set_mode_success = False
            api_resp_d = {}
            api_resp = ""

            if HSC.session_id is not None:
                if len(HSC.products.light) > 0:
                    for current_node_index in range(0,
                                                    len(HSC.products.light)):
                        if "id" in HSC.products.light[current_node_index]:
                            if (HSC.products.light[current_node_index]
                                ["id"] == node_id):
                                node_index = current_node_index
                                break
                    if node_index != -1:
                        json_string_content = '{"status": "OFF"}'
                        hive_api_url = (HIVE_API.urls.nodes
                                        + '/'
                                        + HSC.products.light[node_index]["type"]
                                        + '/'
                                        + HSC.products.light[node_index]["id"])
                        api_resp_d = Pyhiveapi.hive_api_json_call(self, "POST",
                                                        hive_api_url,
                                                        json_string_content,
                                                        False)

                        api_resp = api_resp_d['original']

                        if str(api_resp) == "<Response [200]>":
                            Pyhiveapi.hive_api_get_nodes(self, node_id)
                            set_mode_success = True

            return set_mode_success

        def turn_on(self, node_id, nodedevicetype, new_brightness,
                    new_color_temp, new_color):
            """Set light to turn on."""
            Pyhiveapi.check_hive_api_logon(self, )

            if new_brightness is not None:
                Pyhiveapi.Light.set_brightness(self, node_id, new_brightness)
            if new_color_temp is not None:
                Pyhiveapi.Light.set_color_temp(self, node_id, nodedevicetype,
                                               new_color_temp)
            if new_color is not None:
                Pyhiveapi.Light.set_color(self, node_id, new_color)

            node_index = -1

            set_mode_success = False
            api_resp_d = {}
            api_resp = ""

            if HSC.session_id is not None:
                if len(HSC.products.light) > 0:
                    for cni in range(0, len(HSC.products.light)):
                        if "id" in HSC.products.light[cni]:
                            if HSC.products.light[cni]["id"] == node_id:
                                node_index = cni
                                break
                    if node_index != -1:
                        json_string_content = '{"status": "ON"}'
                        hive_api_url = (HIVE_API.urls.nodes
                                        + '/' + HSC.products.light[node_index][
                                            "type"]
                                        + '/' + HSC.products.light[node_index][
                                            "id"])
                        api_resp_d = Pyhiveapi.hive_api_json_call(self, "POST",
                                                        hive_api_url,
                                                        json_string_content,
                                                        False)

                        api_resp = api_resp_d['original']

                    if str(api_resp) == "<Response [200]>":
                        Pyhiveapi.hive_api_get_nodes(self, node_id)
                        set_mode_success = True

            return set_mode_success

        def set_brightness(self, node_id, new_brightness):
            """Set light to turn on."""
            Pyhiveapi.check_hive_api_logon(self)

            node_index = -1

            set_mode_success = False
            api_resp_d = {}
            api_resp = ""

            if HSC.session_id is not None:
                if len(HSC.products.light) > 0:
                    for cni in range(0, len(HSC.products.light)):
                        if "id" in HSC.products.light[cni]:
                            if HSC.products.light[cni]["id"] == node_id:
                                node_index = cni
                                break
                    if node_index != -1:
                        json_string_content = \
                            ('{"status": "ON", "brightness": '
                            + str(new_brightness)
                            + '}')
                        hive_api_url = (HIVE_API.urls.nodes
                                        + '/' + HSC.products.light[node_index][
                                            "type"]
                                        + '/' + HSC.products.light[node_index][
                                            "id"])
                        api_resp_d = Pyhiveapi.hive_api_json_call(self, "POST",
                                                        hive_api_url,
                                                        json_string_content,
                                                        False)

                        api_resp = api_resp_d['original']

                    if str(api_resp) == "<Response [200]>":
                        Pyhiveapi.hive_api_get_nodes(self, node_id)
                        set_mode_success = True

            return set_mode_success

        def set_color_temp(self, node_id, nodedevicetype, new_color_temp):
            """Set light to turn on."""
            Pyhiveapi.check_hive_api_logon(self)

            node_index = -1

            set_mode_success = False
            api_resp_d = {}
            api_resp = ""

            if HSC.session_id is not None:
                if len(HSC.products.light) > 0:
                    for cni in range(0, len(HSC.products.light)):
                        if "id" in HSC.products.light[cni]:
                            if HSC.products.light[cni]["id"] == node_id:
                                node_index = cni
                                break
                    if node_index != -1:
                        if nodedevicetype == "tuneablelight":
                            json_string_content = '{"colourTemperature": ' + str(new_color_temp) + '}'
                        else:
                            json_string_content = '{"colourMode": "WHITE", "colourTemperature": ' + str(new_color_temp) + '}'
                        hive_api_url = (HIVE_API.urls.nodes
                                        + '/' + HSC.products.light[node_index][
                                            "type"]
                                        + '/' + HSC.products.light[node_index][
                                            "id"])
                        api_resp_d = Pyhiveapi.hive_api_json_call(self, "POST",
                                                        hive_api_url,
                                                        json_string_content,
                                                        False)

                        api_resp = api_resp_d['original']

                    if str(api_resp) == "<Response [200]>":
                        Pyhiveapi.hive_api_get_nodes(self, node_id)
                        set_mode_success = True

            return set_mode_success

        def set_color(self, node_id, new_color):
            """Set light to turn on."""
            Pyhiveapi.check_hive_api_logon(self)

            node_index = -1

            set_mode_success = False
            api_resp_d = {}
            api_resp = ""
            new_hue = None
            new_saturation = None
            new_value = None

            if HSC.session_id is not None:
                if len(HSC.products.light) > 0:
                    for cni in range(0, len(HSC.products.light)):
                        if "id" in HSC.products.light[cni]:
                            if HSC.products.light[cni]["id"] == node_id:
                                node_index = cni
                                break
                    if node_index != -1:
                        new_hue = new_color[0]
                        new_saturation = new_color[1]
                        new_value = new_color[2]
                        json_string_content = '{"colourMode": "COLOUR", "hue": ' + str(
                            new_hue) + ', "saturation": ' + str(
                            new_saturation) + ', "value": ' + str(
                            new_value) + '}'
                        hive_api_url = (HIVE_API.urls.nodes
                                        + '/' + HSC.products.light[node_index][
                                            "type"]
                                        + '/' + HSC.products.light[node_index][
                                            "id"])
                        api_resp_d = Pyhiveapi.hive_api_json_call(self, "POST",
                                                        hive_api_url,
                                                        json_string_content,
                                                        False)

                        api_resp = api_resp_d['original']

                    if str(api_resp) == "<Response [200]>":
                        Pyhiveapi.hive_api_get_nodes(self, node_id)
                        set_mode_success = True

            return set_mode_success

    class Sensor():
        """Hive Sensors."""
        def hub_online_status(self, node_id):
            """Get the online status of the Hive hub."""
            return_status = "Offline"

            for a_hub in HSC.devices.hub:
                if "id" in a_hub:
                    if a_hub["id"] == node_id:
                        if "props" in a_hub and "online" in a_hub["props"]:
                            if a_hub["props"]["online"]:
                                return "Online"
                            else:
                                return "Offline"

            return return_status


        def battery_level(self, node_id):
            """Get device battery level."""
            node_index = -1

            battery_level_return = 0
            battery_level_tmp = 0
            battery_level_found = False
            all_devices = HSC.devices.thermostat + HSC.devices.sensors

            current_node_attribute = "BatteryLevel_" + node_id

            if len(HSC.devices.thermostat) > 0 or len(HSC.devices.sensors) > 0:
                for current_node_index in range(0, len(all_devices)):
                    if "id" in all_devices[current_node_index]:
                        if all_devices[current_node_index]["id"] == node_id:
                            node_index = current_node_index
                            break

                if node_index != -1:
                    if ("props" in all_devices[node_index] and "battery" in all_devices[node_index]["props"]):
                        battery_level_tmp = (all_devices[node_index]["props"]["battery"])
                        battery_level_found = True

            if battery_level_found:
                NODE_ATTRIBS[current_node_attribute] = battery_level_tmp
                battery_level_return = battery_level_tmp
            else:
                if current_node_attribute in NODE_ATTRIBS:
                    battery_level_return = NODE_ATTRIBS.get(current_node_attribute)
                else:
                    battery_level_return = 0

            return battery_level_return

        def get_state(self, node_id, node_device_type):
            """Get sensor state."""
            node_index = -1

            sensor_state_tmp = False
            sensor_state_return = False
            sensor_found = False

            current_node_attribute = "Sensor_State_" + node_id

            if len(HSC.products.sensors) > 0:
                for current_node_index in range(0, len(HSC.products.sensors)):
                    if "id" in HSC.products.sensors[current_node_index]:
                        if HSC.products.sensors[current_node_index]["id"] == node_id:
                            node_index = current_node_index
                            break

                if node_index != -1:
                    if node_device_type == "contactsensor":
                        state = (HSC.products.sensors[node_index]["props"]["status"])
                        if state == 'OPEN':
                            sensor_state_tmp = True
                    elif node_device_type == "motionsensor":
                        sensor_state_tmp = (HSC.products.sensors[node_index]["props"]["motion"]["status"])
                if sensor_state_tmp != None:
                    sensor_found = True

            if sensor_found:
                NODE_ATTRIBS[current_node_attribute] = sensor_state_tmp
                sensor_state_return = sensor_state_tmp
            else:
                if current_node_attribute in NODE_ATTRIBS:
                    sensor_state_return = NODE_ATTRIBS.get(current_node_attribute)
                else:
                    sensor_state_return = False

            return sensor_state_return

        def get_mode(self, node_id):
            """Get sensor mode."""

            node_index = -1

            hive_device_mode_tmp = ""
            hive_device_mode_return = ""
            hive_device_mode_found = False
            all_devices = HSC.products.light + HSC.products.plug

            current_node_attribute = "Device_Mode_" + node_id

            if len(HSC.products.light) > 0 or len(HSC.products.plug) > 0:
                for current_node_index in range(0, len(all_devices)):
                    if "id" in all_devices[current_node_index]:
                        if all_devices[current_node_index]["id"] == node_id:
                            node_index = current_node_index
                            break

                if node_index != -1:
                    if ("state" in all_devices[node_index] and
                            "mode" in all_devices[node_index]["state"]):
                        hive_device_mode_tmp = (all_devices[node_index]
                                                ["state"]["mode"])
                        hive_device_mode_found = True

            if hive_device_mode_found:
                NODE_ATTRIBS[current_node_attribute] = hive_device_mode_tmp
                hive_device_mode_return = hive_device_mode_tmp
            else:
                if current_node_attribute in NODE_ATTRIBS:
                    hive_device_mode_return = NODE_ATTRIBS.get(current_node_attribute)
                else:
                    hive_device_mode_return = "UNKNOWN"

            return hive_device_mode_return

    class Switch():
        """Hive Switches."""
        def get_state(self, node_id):
            """Get smart plug current state."""
            node_index = -1

            smartplug_state_tmp = "UNKNOWN"
            smartplug_state_return = "UNKNOWN"
            smartplug_state_found = False

            current_node_attribute = "Smartplug_State_" + node_id

            if len(HSC.products.plug) > 0:
                for current_node_index in range(0, len(HSC.products.plug)):
                    if "id" in HSC.products.plug[current_node_index]:
                        if HSC.products.plug[current_node_index]["id"] == node_id:
                            node_index = current_node_index
                            break

                if node_index != -1:
                    if ("state" in HSC.products.plug[
                        node_index] and "status" in
                        HSC.products.plug[node_index]["state"]):
                        smartplug_state_tmp = (HSC.products.plug[node_index]
                                               ["state"]["status"])
                        smartplug_state_found = True

            if smartplug_state_found:
                NODE_ATTRIBS[current_node_attribute] = smartplug_state_tmp
                smartplug_state_return = smartplug_state_tmp
            else:
                if current_node_attribute in NODE_ATTRIBS:
                    smartplug_state_return = NODE_ATTRIBS.get(
                        current_node_attribute)
                else:
                    smartplug_state_return = "UNKNOWN"

            smartplug_state_return_b = False

            if smartplug_state_return == "ON":
                smartplug_state_return_b = True

            return smartplug_state_return_b

        def get_power_usage(self, node_id):
            """Get smart plug current power usage."""
            node_index = -1

            current_power_tmp = 0
            current_power_return = 0
            current_power_found = False

            current_node_attribute = "Smartplug_Current_Power_" + node_id

            if len(HSC.products.plug) > 0:
                for current_node_index in range(0, len(HSC.products.plug)):
                    if "id" in HSC.products.plug[current_node_index]:
                        if HSC.products.plug[current_node_index]["id"] == node_id:
                            node_index = current_node_index
                            break

                if node_index != -1:
                    if ("props" in HSC.products.plug[node_index]
                        and "powerConsumption"
                        in HSC.products.plug[node_index]["props"]):
                        current_power_tmp = (HSC.products.plug[node_index]
                                             ["props"]["powerConsumption"])
                        current_power_found = True

            if current_power_found:
                NODE_ATTRIBS[current_node_attribute] = current_power_tmp
                current_power_return = current_power_tmp
            else:
                if current_node_attribute in NODE_ATTRIBS:
                    current_power_return = NODE_ATTRIBS.get(
                        current_node_attribute)
                else:
                    current_power_return = 0

            return current_power_return

        def turn_on(self, node_id):
            """Set smart plug to turn on."""
            Pyhiveapi.check_hive_api_logon(self)

            node_index = -1

            set_mode_success = False
            api_resp_d = {}
            api_resp = ""

            if HSC.session_id is not None:
                if len(HSC.products.plug) > 0:
                    for current_node_index in range(0, len(HSC.products.plug)):
                        if "id" in HSC.products.plug[current_node_index]:
                            if HSC.products.plug[current_node_index][
                                "id"] == node_id:
                                node_index = current_node_index
                                break
                    if node_index != -1:
                        json_string_content = '{"status": "ON"}'
                        hive_api_url = (HIVE_API.urls.nodes
                                        + '/'
                                        + HSC.products.plug[node_index]["type"]
                                        + '/'
                                        + HSC.products.plug[node_index]["id"])
                        api_resp_d = Pyhiveapi.hive_api_json_call(self, "POST",
                                                        hive_api_url,
                                                        json_string_content,
                                                        False)

                        api_resp = api_resp_d['original']

                        if str(api_resp) == "<Response [200]>":
                            Pyhiveapi.hive_api_get_nodes(self, node_id)
                            set_mode_success = True

            return set_mode_success

        def turn_off(self, node_id, ):
            """Set smart plug to turn off."""
            Pyhiveapi.check_hive_api_logon(self)

            node_index = -1

            set_mode_success = False
            api_resp_d = {}
            api_resp = ""

            if HSC.session_id is not None:
                if len(HSC.products.plug) > 0:
                    for current_node_index in range(0, len(HSC.products.plug)):
                        if "id" in HSC.products.plug[current_node_index]:
                            if HSC.products.plug[current_node_index][
                                "id"] == node_id:
                                node_index = current_node_index
                                break
                    if node_index != -1:
                        json_string_content = '{"status": "OFF"}'
                        hive_api_url = (HIVE_API.urls.nodes
                                        + '/'
                                        + HSC.products.plug[node_index]["type"]
                                        + '/'
                                        + HSC.products.plug[node_index]["id"])
                        api_resp_d = Pyhiveapi.hive_api_json_call(self, "POST",
                                                        hive_api_url,
                                                        json_string_content,
                                                        False)

                        api_resp = api_resp_d['original']

                        if str(api_resp) == "<Response [200]>":
                            Pyhiveapi.hive_api_get_nodes(self, node_id)
                            set_mode_success = True

            return set_mode_success


    class Weather():
        """Hive Weather."""
        def temperature(self):
            """Get Hive Weather temperature."""
            return HSC.weather.temperature.value
