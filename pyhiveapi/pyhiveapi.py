"""
    Usage:

        from pyhiveapi import Pyhiveapi

        session = HiveSession()

        username = config[DOMAIN][CONF_USERNAME]
        password = config[DOMAIN][CONF_PASSWORD]
        update_interval = config[DOMAIN][CONF_SCAN_INTERVAL]

        hive_api = Pyhiveapi()
        devicelist = hive_api.initialise_api(username, password, update_interval)

        if devicelist is None:
            _LOGGER.error("Hive API initialization failed")
            return False

        session.core = hive_api
        session.sensor = hive_api.factory(Pyhiveapi.Device.Sensor)
        session.heating = hive_api.factory(Pyhiveapi.Device.Heating)
        session.hotwater = hive_api.factory(Pyhiveapi.Device.Hotwater)
        session.light = hive_api.factory(Pyhiveapi.Device.Light)
        session.switch = hive_api.factory(Pyhiveapi.Device.Switch)

"""
import operator
from datetime import datetime
from datetime import timedelta
import requests
from enum import Enum
import logging

HIVE_NODE_UPDATE_INTERVAL_DEFAULT = 120
HIVE_WEATHER_UPDATE_INTERVAL_DEFAULT = 60  # Update to 900 or 600
MINUTES_BETWEEN_LOGONS = 15

NODE_ATTRIBS = {"Header": "HeaderText"}

_LOGGER = logging.getLogger(__name__)


class HiveDevices:
    """Initiate Hive Devices Class."""

    def __init__(self) -> None:
        super().__init__()
        self.hub = []
        self.thermostat = []
        self.boiler_module = []
        self.plug = []
        self.light = []
        self.sensors = []


class HiveProducts:
    """Initiate Hive Products Class."""

    def __init__(self) -> None:
        super().__init__()
        self.heating = []
        self.hotwater = []
        self.light = []
        self.plug = []
        self.sensors = []


class HivePlatformData:
    """Initiate Hive PlatformData Class."""

    def __init__(self) -> None:
        super().__init__()
        self.minmax = {}


class HiveTemperature:
    """Initiate Hive Temperature Class."""

    def __init__(self) -> None:
        super().__init__()
        self.unit = ""
        self.value = 0.00


class HiveWeather:
    """Initiate Hive Weather Class."""

    def __init__(self) -> None:
        super().__init__()
        self.last_update = datetime(2017, 1, 1, 12, 0, 0)
        self.nodeid = ""
        self.icon = ""
        self.description = ""
        self.temperature = HiveTemperature()


class HiveSession:
    """Initiate Hive Session Class."""

    def __init__(self) -> None:
        super().__init__()
        self.session_id = ""
        self.session_logon_datetime = datetime(2017, 1, 1, 12, 0, 0)
        self.username = ""
        self.password = ""
        self.postcode = ""
        self.timezone = ""
        self.countrycode = ""
        self.locale = ""
        self.temperature_unit = ""
        self.devices = HiveDevices()
        self.products = HiveProducts()
        self.weather = HiveWeather()
        self.data = HivePlatformData()
        #    self.holiday_mode = Hive_HolidayMode()
        self.update_node_interval_seconds = HIVE_NODE_UPDATE_INTERVAL_DEFAULT
        self.update_weather_interval_seconds = HIVE_WEATHER_UPDATE_INTERVAL_DEFAULT
        self.last_update = datetime(2017, 1, 1, 12, 0, 0)
        self.logging = False


class HiveAPIURLS:
    """Initiate Hive API URLS Class."""

    def __init__(self) -> None:
        super().__init__()
        self.global_login = ""
        self.base = ""
        self.weather = ""
        self.holiday_mode = ""
        self.devices = ""
        self.products = ""
        self.nodes = ""


class HiveAPIHeaders:
    """Initiate Hive API Headers Class."""

    def __init__(self) -> None:
        super().__init__()
        self.accept_key = ""
        self.accept_value = ""
        self.content_type_key = ""
        self.content_type_value = ""
        self.session_id_key = ""
        self.session_id_value = ""


class HiveAPIDetails:
    """Initiate Hive API Details Class."""

    def __init__(self) -> None:
        super().__init__()
        self.urls = HiveAPIURLS()
        self.headers = HiveAPIHeaders()
        self.platform_name = ""


class HiveAPI:
    def __init__(self):
        self.details = HiveAPIDetails()
        self.session = HiveSession()

        """Initialise the base variable values."""

        self.details.platform_name = ""

        self.details.urls.global_login = "https://beekeeper.hivehome.com/1.0/global/login"
        self.details.urls.base = ""
        self.details.urls.weather = "https://weather-prod.bgchprod.info/weather"
        self.details.urls.holiday_mode = "/holiday-mode"
        self.details.urls.devices = "/devices"
        self.details.urls.products = "/products"
        self.details.urls.nodes = "/nodes"

        self.details.headers.accept_key = "Accept"
        self.details.headers.accept_value = "*/*"
        self.details.headers.content_type_key = "content-type"
        self.details.headers.content_type_value = "application/json"
        self.details.headers.session_id_key = "authorization"
        self.details.headers.session_id_value = None

    def json_call(self, request_type, request_url, json_string_content, absolute_request_url):
        """Call the JSON Hive API and return any returned data."""
        api_headers = {self.details.headers.content_type_key: self.details.headers.content_type_value,
                       self.details.headers.accept_key: self.details.headers.accept_value,
                       self.details.headers.session_id_key: self.details.headers.session_id_value}

        json_return = {}
        json_response = ""

        if absolute_request_url:
            full_request_url = request_url
        else:
            full_request_url = self.details.urls.base + request_url

        json_call_try_finished = False
        try:
            if request_type == "POST":
                json_response = requests.post(full_request_url, data=json_string_content, headers=api_headers)
            elif request_type == "GET":
                json_response = requests.get(full_request_url, data=json_string_content, headers=api_headers)
            elif request_type == "PUT":
                json_response = requests.put(full_request_url, data=json_string_content, headers=api_headers)
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

    def logon(self):
        """Log in to the Hive API and get the Session ID."""
        login_details_found = True
        self.session.session_id = None

        try_finished = False
        try:
            json_string_content = '{"username": "' + self.session.username + \
                                  '","password": "' + self.session.password + '"}'

            api_resp_d = self.json_call("POST", self.details.urls.global_login, json_string_content, True)
            api_resp_p = api_resp_d['parsed']

            if ('token' in api_resp_p and
                        'user' in api_resp_p and
                        'platform' in api_resp_p):
                self.details.headers.session_id_value = api_resp_p["token"]
                self.session.session_id = self.details.headers.session_id_value
                self.session.session_logon_datetime = datetime.now()

                if 'endpoint' in api_resp_p['platform']:
                    self.details.urls.base = api_resp_p['platform']['endpoint']
                else:
                    login_details_found = False

                if 'name' in api_resp_p['platform']:
                    self.details.platform_name = api_resp_p['platform']['name']
                else:
                    login_details_found = False

                if 'locale' in api_resp_p['user']:
                    self.session.locale = api_resp_p['user']['locale']
                else:
                    login_details_found = False

                if 'countryCode' in api_resp_p['user']:
                    self.session.countrycode = api_resp_p['user']['countryCode']
                else:
                    login_details_found = False

                if 'timezone' in api_resp_p['user']:
                    self.session.timezone = api_resp_p['user']['timezone']
                else:
                    login_details_found = False

                if 'postcode' in api_resp_p['user']:
                    self.session.postcode = api_resp_p['user']['postcode']
                else:
                    login_details_found = False

                if 'temperatureUnit' in api_resp_p['user']:
                    self.session.temperature_unit = api_resp_p['user']['temperatureUnit']
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
            self.session.session_id = None

    def check_hive_api_logon(self):
        """Check if currently logged in with a valid Session ID."""
        current_time = datetime.now()
        l_logon_secs = (current_time - self.session.session_logon_datetime).total_seconds()
        l_logon_mins = int(round(l_logon_secs / 60))

        if l_logon_mins >= MINUTES_BETWEEN_LOGONS or self.session.session_id is None:
            self.logon()

    def update_data(self, node_id):
        """Get latest data for Hive nodes - rate limiting."""
        nodes_updated = False
        current_time = datetime.now()
        last_update_secs = (current_time - self.session.last_update).total_seconds()
        if last_update_secs >= self.session.update_node_interval_seconds:
            self.session.last_update = current_time
            nodes_updated = self.get_nodes(node_id)
        return nodes_updated

    def get_nodes(self, node_id="NoID"):
        """Get latest data for Hive nodes."""
        get_nodes_successful = True

        self.check_hive_api_logon()

        if self.session.session_id is not None:
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
                api_resp_d = self.json_call("GET", self.details.urls.devices, "", False)

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
                api_resp_d = self.json_call("GET", self.details.urls.products, "", False)

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
                    self.session.devices.hub = tmp_devices_hub
                if len(tmp_devices_thermostat) > 0:
                    self.session.devices.thermostat = tmp_devices_thermostat
                if len(tmp_devices_boiler_module) > 0:
                    self.session.devices.boiler_module = tmp_devices_boiler_module
                if len(tmp_devices_plug) > 0:
                    self.session.devices.plug = tmp_devices_plug
                if len(tmp_devices_light) > 0:
                    self.session.devices.light = tmp_devices_light
                if len(tmp_devices_sensors) > 0:
                    self.session.devices.sensors = tmp_devices_sensors

                if len(tmp_products_heating) > 0:
                    self.session.products.heating = tmp_products_heating
                if len(tmp_products_hotwater) > 0:
                    self.session.products.hotwater = tmp_products_hotwater
                if len(tmp_products_plug) > 0:
                    self.session.products.plug = tmp_products_plug
                if len(tmp_products_light) > 0:
                    self.session.products.light = tmp_products_light
                if len(tmp_products_sensors) > 0:
                    self.session.products.sensors = tmp_products_sensors

                try_finished = True
            except (IOError, RuntimeError, ZeroDivisionError):
                try_finished = False
            finally:
                if not try_finished:
                    get_nodes_successful = False
        else:
            get_nodes_successful = False

        return get_nodes_successful

    def hive_api_get_weather(self):
        """Get latest weather data from Hive."""
        get_weather_successful = True

        current_time = datetime.now()
        last_update_secs = (current_time - self.session.weather.last_update).total_seconds()
        if last_update_secs >= self.session.update_weather_interval_seconds:
            self.check_hive_api_logon()

            if self.session.session_id is not None:
                try_finished = False
                try:
                    weather_url = self.details.urls.weather + "?postcode=" + self.session.postcode + \
                                  "&country=" + self.session.countrycode
                    weather_url = weather_url.replace(" ", "%20")

                    api_resp_d = self.json_call("GET", weather_url, "", True)
                    api_resp_p = api_resp_d['parsed']

                    if "weather" in api_resp_p:
                        if "icon" in api_resp_p["weather"]:
                            self.session.weather.icon = api_resp_p["weather"]["icon"]
                        if "description" in api_resp_p["weather"]:
                            self.session.weather.description = api_resp_p["weather"]["icon"]
                        if "temperature" in api_resp_p["weather"]:
                            if "unit" in api_resp_p["weather"]["temperature"]:
                                self.session.weather.temperature.unit = api_resp_p["weather"]["temperature"]["unit"]
                            if "unit" in api_resp_p["weather"]["temperature"]:
                                self.session.weather.temperature.value = api_resp_p["weather"]["temperature"]["value"]
                        self.session.weather.nodeid = "HiveWeather"
                    else:
                        get_weather_successful = False

                    self.session.weather.last_update = current_time
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
                slot_time = self.p_minutes_to_time(current_slot_custom["start"])
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
        self.session.username = username
        self.session.password = password

        if mins_between_updates <= 0:
            mins_between_updates = 2

        hive_node_update_interval = mins_between_updates * 60

        if self.session.username is None or self.session.password is None:
            return None
        else:
            self.logon()
            if self.session.session_id is not None:
                self.session.update_node_interval_seconds = hive_node_update_interval
                self.get_nodes()  # Get latest data for Hive nodes - not rate limiting
                #  HiveBase.hive_api_get_weather(self)

        device_list_all = {}
        device_list_sensor = []
        device_list_binary_sensor = []
        device_list_climate = []
        device_list_light = []
        device_list_plug = []

        if len(self.session.devices.hub) > 0:
            for a_device in self.session.devices.hub:
                if "id" in a_device and "state" in a_device and "name" in a_device["state"]:
                    device_list_sensor.append({'HA_DeviceType': 'Hub_OnlineStatus', 'Hive_NodeID': a_device["id"],
                                               'Hive_NodeName': a_device["state"]["name"], "Hive_DeviceType": "Hub"})

        if len(self.session.products.heating) > 0:
            for product in self.session.products.heating:
                if "id" in product and "state" in product and "name" in product["state"]:
                    node_name = product["state"]["name"]
                    if len(self.session.products.heating) == 1:
                        node_name = None
                    device_list_climate.append(
                        {'HA_DeviceType': 'Heating', 'Hive_NodeID': product["id"], 'Hive_NodeName': node_name,
                         "Hive_DeviceType": "Heating"})
                    device_list_sensor.append(
                        {'HA_DeviceType': 'Heating_CurrentTemperature', 'Hive_NodeID': product["id"],
                         'Hive_NodeName': node_name, "Hive_DeviceType": "Heating"})
                    device_list_sensor.append(
                        {'HA_DeviceType': 'Heating_TargetTemperature', 'Hive_NodeID': product["id"],
                         'Hive_NodeName': node_name, "Hive_DeviceType": "Heating"})
                    device_list_sensor.append(
                        {'HA_DeviceType': 'Heating_State', 'Hive_NodeID': product["id"], 'Hive_NodeName': node_name,
                         "Hive_DeviceType": "Heating"})
                    device_list_sensor.append(
                        {'HA_DeviceType': 'Heating_Mode', 'Hive_NodeID': product["id"], 'Hive_NodeName': node_name,
                         "Hive_DeviceType": "Heating"})
                    device_list_sensor.append(
                        {'HA_DeviceType': 'Heating_Boost', 'Hive_NodeID': product["id"], 'Hive_NodeName': node_name,
                         "Hive_DeviceType": "Heating"})

        if len(self.session.products.hotwater) > 0:
            for product in self.session.products.hotwater:
                if "id" in product and "state" in product and "name" in product["state"]:
                    node_name = product["state"]["name"]
                    if len(self.session.products.hotwater) == 1:
                        node_name = None
                    device_list_climate.append(
                        {'HA_DeviceType': 'HotWater', 'Hive_NodeID': product["id"], 'Hive_NodeName': node_name,
                         "Hive_DeviceType": "HotWater"})
                    device_list_sensor.append(
                        {'HA_DeviceType': 'HotWater_State', 'Hive_NodeID': product["id"], 'Hive_NodeName': node_name,
                         "Hive_DeviceType": "HotWater"})
                    device_list_sensor.append(
                        {'HA_DeviceType': 'HotWater_Mode', 'Hive_NodeID': product["id"], 'Hive_NodeName': node_name,
                         "Hive_DeviceType": "HotWater"})
                    device_list_sensor.append(
                        {'HA_DeviceType': 'HotWater_Boost', 'Hive_NodeID': product["id"], 'Hive_NodeName': node_name,
                         "Hive_DeviceType": "HotWater"})

        if len(self.session.devices.thermostat) > 0 or len(self.session.devices.sensors) > 0:
            all_devices = self.session.devices.thermostat + self.session.devices.sensors
            for a_device in all_devices:
                if "id" in a_device and "state" in a_device and "name" in a_device["state"]:
                    node_name = a_device["state"]["name"]
                    if a_device["type"] == "thermostatui" and len(self.session.devices.thermostat) == 1:
                        node_name = None
                    if "type" in a_device:
                        hive_device_type = a_device["type"]
                        device_list_sensor.append(
                            {'HA_DeviceType': 'Hive_Device_BatteryLevel', 'Hive_NodeID': a_device["id"],
                             'Hive_NodeName': node_name, "Hive_DeviceType": hive_device_type})

        if len(self.session.products.light) > 0:
            for product in self.session.products.light:
                if "id" in product and "state" in product and "name" in product["state"]:
                    if "type" in product:
                        light_device_type = product["type"]
                        device_list_light.append(
                            {'HA_DeviceType': 'Hive_Device_Light', 'Hive_Light_DeviceType': light_device_type,
                             'Hive_NodeID': product["id"], 'Hive_NodeName': product["state"]["name"],
                             "Hive_DeviceType": "Light"})
                        device_list_sensor.append(
                            {'HA_DeviceType': 'Hive_Device_Light_Mode', 'Hive_NodeID': product["id"],
                             'Hive_NodeName': product["state"]["name"], "Hive_DeviceType": light_device_type})

        if len(self.session.products.plug) > 0:
            for product in self.session.products.plug:
                if "id" in product and "state" in product and "name" in product["state"]:
                    if "type" in product:
                        plug_device_type = product["type"]
                        device_list_plug.append(
                            {'HA_DeviceType': 'Hive_Device_Plug', 'Hive_Plug_DeviceType': plug_device_type,
                             'Hive_NodeID': product["id"], 'Hive_NodeName': product["state"]["name"],
                             "Hive_DeviceType": "Switch"})
                        device_list_sensor.append(
                            {'HA_DeviceType': 'Hive_Device_Plug_Mode', 'Hive_NodeID': product["id"],
                             'Hive_NodeName': product["state"]["name"], "Hive_DeviceType": plug_device_type})

        if len(self.session.products.sensors) > 0:
            for product in self.session.products.sensors:
                if "id" in product and "state" in product and "name" in product["state"]:
                    if "type" in product:
                        hive_sensor_device_type = product["type"]
                        device_list_binary_sensor.append(
                            {'HA_DeviceType': 'Hive_Device_Binary_Sensor', 'Hive_NodeID': product["id"],
                             'Hive_NodeName': product["state"]["name"], "Hive_DeviceType": hive_sensor_device_type})

                        #        if self.session.weather.nodeid == "HiveWeather":
                        #        device_list_sensor.append({'HA_DeviceType': 'Weather_OutsideTemperature', 'Hive_NodeID': self.session.weather.nodeid, 'Hive_NodeName': "Hive Weather"})

        device_list_all['device_list_sensor'] = device_list_sensor
        device_list_all['device_list_binary_sensor'] = device_list_binary_sensor
        device_list_all['device_list_climate'] = device_list_climate
        device_list_all['device_list_light'] = device_list_light
        device_list_all['device_list_plug'] = device_list_plug

        return device_list_all


class Pyhiveapi:
    class Device(Enum):
        Heating = 1
        Hotwater = 2
        Light = 3
        Sensor = 4
        Switch = 5
        Weather = 6

    def __init__(self) -> None:
        self.hive_api = HiveAPI()
        super().__init__()

    def initialise_api(self, username, password, mins_between_updates):
        return self.hive_api.initialise_api(username, password, mins_between_updates)

    def update_data(self, node_id):
        self.hive_api.update_data(node_id)

    def factory(self, device):

        class Heating:
            """Hive Switches."""

            def __init__(self, hive_api) -> None:
                self.hive_api = hive_api
                self.hive_session = hive_api.session
                super().__init__()

            def min_temperature(self, node_id):
                """Get heating minimum target temperature."""
                heating_min_temp_default = 5
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

                if len(self.hive_session.products.heating) > 0:
                    for current_node_index in range(0, len(self.hive_session.products.heating)):
                        if "id" in self.hive_session.products.heating[current_node_index]:
                            if self.hive_session.products.heating[current_node_index]["id"] == node_id:
                                node_index = current_node_index
                                break

                    if node_index != -1:
                        if "props" in self.hive_session.products.heating[node_index]:
                            if "temperature" in self.hive_session.products.heating[node_index]["props"]:
                                current_temp_tmp = (self.hive_session.products.heating[node_index]
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
                    if node_id in self.hive_session.data.minmax:
                        if self.hive_session.data.minmax[node_id]['TodayDate'] != datetime.date(datetime.now()):
                            self.hive_session.data.minmax[node_id]['TodayMin'] = 1000
                            self.hive_session.data.minmax[node_id]['TodayMax'] = -1000
                            self.hive_session.data.minmax[node_id]['TodayDate'] = datetime.date(datetime.now())

                        if current_temp_return < self.hive_session.data.minmax[node_id]['TodayMin']:
                            self.hive_session.data.minmax[node_id]['TodayMin'] = current_temp_return

                        if current_temp_return > self.hive_session.data.minmax[node_id]['TodayMax']:
                            self.hive_session.data.minmax[node_id]['TodayMax'] = current_temp_return

                        if current_temp_return < self.hive_session.data.minmax[node_id]['RestartMin']:
                            self.hive_session.data.minmax[node_id]['RestartMin'] = current_temp_return

                        if current_temp_return > self.hive_session.data.minmax[node_id]['RestartMax']:
                            self.hive_session.data.minmax[node_id]['RestartMax'] = current_temp_return
                    else:
                        current_node_max_min_data = {'TodayMin': current_temp_return,
                                                     'TodayMax': current_temp_return,
                                                     'TodayDate': datetime.date(datetime.now()),
                                                     'RestartMin': current_temp_return,
                                                     'RestartMax': current_temp_return}
                        self.hive_session.data.minmax[node_id] = current_node_max_min_data
                else:
                    current_temp_return = 0

                return current_temp_return

            def minmax_temperatures(self, node_id):
                if node_id in self.hive_session.data.minmax:
                    return self.hive_session.data.minmax[node_id]
                else:
                    return None

            def get_target_temperature(self, node_id):
                """Get heating target temperature."""
                node_index = -1

                heating_target_temp_return = 0
                heating_target_temp_tmp = 0
                heating_target_temp_found = False

                current_node_attribute = "Heating_TargetTemp_" + node_id

                # pylint: disable=too-many-nested-blocks
                if len(self.hive_session.products.heating) > 0:
                    for current_node_index in range(0, len(self.hive_session.products.heating)):
                        if "id" in self.hive_session.products.heating[current_node_index]:
                            if self.hive_session.products.heating[current_node_index]["id"] == node_id:
                                node_index = current_node_index
                                break

                    if node_index != -1:
                        heating_mode_current = self.get_mode(node_id)
                        if heating_mode_current == "SCHEDULE":
                            if ('props' in self.hive_session.products.heating[node_index] and
                                        'scheduleOverride' in
                                        self.hive_session.products.heating[node_index]["props"]):
                                if self.hive_session.products.heating[node_index]["props"]["scheduleOverride"]:
                                    if ("state" in self.hive_session.products.heating[node_index] and
                                                "target" in self.hive_session.products.heating[node_index]
                                            ["state"]):
                                        heating_target_temp_tmp = (
                                            self.hive_session.products.heating[node_index]["state"]["target"])
                                        heating_target_temp_found = True
                                else:
                                    snan = (
                                        self.hive_api.p_get_schedule_now_next_later(
                                            self.hive_session.products.heating[node_index]["state"]["schedule"]))
                                    if 'now' in snan:
                                        if 'value' in snan["now"] and 'target' in snan["now"]["value"]:
                                            heating_target_temp_tmp = (snan["now"]["value"]["target"])
                                            heating_target_temp_found = True
                        else:
                            if ("state" in self.hive_session.products.heating[node_index] and
                                        "target" in self.hive_session.products.heating[node_index]["state"]):
                                heating_target_temp_tmp = \
                                    self.hive_session.products.heating[node_index]["state"]["target"]
                                heating_target_temp_found = True

                if heating_target_temp_found:
                    NODE_ATTRIBS[current_node_attribute] = heating_target_temp_tmp
                    heating_target_temp_return = heating_target_temp_tmp
                else:
                    if current_node_attribute in NODE_ATTRIBS:
                        heating_target_temp_return = NODE_ATTRIBS.get(current_node_attribute)
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

                heating = self.hive_session.products.heating
                if len(heating) > 0:
                    for current_node_index in range(0, len(heating)):
                        if "id" in heating[current_node_index]:
                            if heating[current_node_index]["id"] == node_id:
                                node_index = current_node_index
                                break

                    if node_index != -1:
                        if "state" in heating[node_index] and "mode" in heating[node_index]["state"]:
                            mode_tmp = heating[node_index]["state"]["mode"]
                            if mode_tmp == "BOOST":
                                if ("props" in heating[node_index] and
                                            "previous" in heating[node_index]["props"] and
                                            "mode" in heating[node_index]["props"]["previous"]):
                                    mode_tmp = (heating[node_index]["props"]["previous"]["mode"])
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
                heating_state_tmp = "OFF"
                heating_state_found = False

                current_node_attribute = "Heating_State_" + node_id

                if len(self.hive_session.products.heating) > 0:
                    temperature_current = self.current_temperature(node_id)
                    temperature_target = self.get_target_temperature(node_id)
                    heating_boost = self.get_boost(node_id)
                    heating_mode = self.get_mode(node_id)

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

                heating_boost_tmp = "UNKNOWN"
                heating_boost_found = False

                current_node_attribute = "Heating_Boost_" + node_id

                heating = self.hive_session.products.heating
                if len(heating) > 0:
                    for current_node_index in range(0, len(heating)):
                        if "id" in heating[current_node_index]:
                            if heating[current_node_index]["id"] == node_id:
                                node_index = current_node_index
                                break

                    if node_index != -1:
                        if ("state" in heating[node_index] and
                                    "boost" in heating[node_index]["state"]):
                            heating_boost_tmp = (heating[node_index]
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

                if self.get_boost(node_id) == "ON":
                    node_index = -1

                    heating_boost_tmp = "UNKNOWN"
                    heating_boost_found = False

                    heating = self.hive_session.products.heating
                    if len(heating) > 0:
                        for current_node_index in range(0, len(heating)):
                            if "id" in heating[current_node_index]:
                                if heating[current_node_index]["id"] == node_id:
                                    node_index = current_node_index
                                    break

                        if node_index != -1:
                            if "state" in heating[node_index] and "boost" in heating[node_index]["state"]:
                                heating_boost_tmp = (heating[node_index]["state"]["boost"])
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
                heating_mode_current = self.get_mode(node_id)

                snan = None

                if heating_mode_current == "SCHEDULE":
                    node_index = -1

                    heating = self.hive_session.products.heating
                    if len(heating) > 0:
                        for current_node_index in range(0, len(heating)):
                            if "id" in heating[current_node_index]:
                                if heating[current_node_index]["id"] == node_id:
                                    node_index = current_node_index
                                    break

                    if node_index != -1:
                        snan = self.hive_api.p_get_schedule_now_next_later(
                            heating[node_index]["state"]["schedule"])
                    else:
                        snan = None
                else:
                    snan = None

                return snan

            def set_target_temperature(self, node_id, new_temperature):
                """Set heating target temperature."""
                self.hive_api.check_hive_api_logon()

                set_temperature_success = False

                if self.hive_session.session_id is not None:
                    node_index = -1
                    heating = self.hive_session.products.heating
                    if len(heating) > 0:
                        for current_node_index in range(0, len(heating)):
                            if "id" in heating[current_node_index]:
                                if heating[current_node_index]["id"] == node_id:
                                    node_index = current_node_index
                                    break

                        if node_index != -1:
                            if "id" in heating[node_index]:
                                json_string_content = ('{"target":' + str(new_temperature) + '}')

                                hive_api_url = (
                                    self.hive_api.details.urls.nodes + "/heating/" + heating[node_index]["id"])
                                api_resp_d = self.hive_api.json_call("POST", hive_api_url, json_string_content, False)

                                api_resp = api_resp_d['original']

                                if str(api_resp) == "<Response [200]>":
                                    self.hive_api.get_nodes(node_id)
                                    #                                fire_bus_event(node_id, device_type)
                                    set_temperature_success = True

                return set_temperature_success

            def set_mode(self, node_id, new_mode):
                """Set heating mode."""
                self.hive_api.check_hive_api_logon()

                set_mode_success = False

                if self.hive_session.session_id is not None:
                    node_index = -1
                    heating = self.hive_session.products.heating
                    if len(heating) > 0:
                        for current_node_index in range(0, len(heating)):
                            if "id" in heating[current_node_index]:
                                if heating[current_node_index]["id"] == node_id:
                                    node_index = current_node_index
                                    break

                        if node_index != -1:
                            if "id" in heating[node_index]:
                                json_string_content = ""
                                if new_mode == "SCHEDULE":
                                    json_string_content = '{"mode": "SCHEDULE"}'
                                elif new_mode == "MANUAL":
                                    json_string_content = '{"mode": "MANUAL"}'
                                elif new_mode == "OFF":
                                    json_string_content = '{"mode": "OFF"}'

                                if new_mode == "SCHEDULE" or new_mode == "MANUAL" or new_mode == "OFF":
                                    hive_api_url = (self.hive_api.details.urls.nodes + "/heating/" +
                                                    heating[node_index]["id"])
                                    api_resp_d = self.hive_api.json_call("POST", hive_api_url, json_string_content,
                                                                         False)

                                    api_resp = api_resp_d['original']

                                    if str(api_resp) == "<Response [200]>":
                                        self.hive_api.get_nodes(node_id)
                                        set_mode_success = True

                return set_mode_success

        class Hotwater:
            """Hive Hotwater."""

            def __init__(self, hive_api) -> None:
                self.hive_api = hive_api
                self.hive_session = hive_api.session
                super().__init__()

            def get_mode(self, node_id):
                """Get hot water current mode."""
                node_index = -1

                hotwater_mode_tmp = "UNKNOWN"
                hotwater_mode_found = False

                current_node_attribute = "HotWater_Mode_" + node_id

                hotwater = self.hive_session.products.hotwater
                if len(hotwater) > 0:
                    for current_node_index in range(0, len(hotwater)):
                        if "id" in hotwater[current_node_index]:
                            if hotwater[current_node_index]["id"] == node_id:
                                node_index = current_node_index
                                break

                    if node_index != -1:
                        if ("state" in hotwater[node_index] and
                                    "mode" in hotwater[node_index]["state"]):
                            hotwater_mode_tmp = (hotwater[node_index]
                                                 ["state"]["mode"])
                            if hotwater_mode_tmp == "BOOST":
                                if ("props" in hotwater[node_index] and
                                            "previous" in
                                            hotwater[node_index]["props"] and
                                            "mode" in
                                            hotwater[node_index]
                                            ["props"]["previous"]):
                                    hotwater_mode_tmp = (hotwater[node_index]
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

                hotwater_boost_tmp = "UNKNOWN"
                hotwater_boost_found = False

                current_node_attribute = "HotWater_Boost_" + node_id

                hotwater = self.hive_session.products.hotwater
                if len(hotwater) > 0:
                    for current_node_index in range(0, len(hotwater)):
                        if "id" in hotwater[current_node_index]:
                            if hotwater[current_node_index]["id"] == node_id:
                                node_index = current_node_index
                                break

                    if node_index != -1:
                        if ("state" in hotwater[node_index] and
                                    "boost" in hotwater[node_index]["state"]):
                            hotwater_boost_tmp = (hotwater[node_index]
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

                if self.get_boost(node_id) == "ON":
                    node_index = -1

                    hotwater_boost_tmp = "UNKNOWN"
                    hotwater_boost_found = False

                    hotwater = self.hive_session.products.hotwater
                    if len(hotwater) > 0:
                        for current_node_index in range(0, len(hotwater)):
                            if "id" in hotwater[current_node_index]:
                                if hotwater[current_node_index]["id"] == node_id:
                                    node_index = current_node_index
                                    break

                        if node_index != -1:
                            if "state" in hotwater[node_index] and "boost" in hotwater[node_index]["state"]:
                                hotwater_boost_tmp = (hotwater[node_index]["state"]["boost"])
                                hotwater_boost_found = True

                    if hotwater_boost_found:
                        hotwater_boost = hotwater_boost_tmp

                return hotwater_boost

            def get_state(self, node_id):
                """Get hot water current state."""
                node_index = -1

                state_tmp = "OFF"
                state_found = False
                mode_current = self.get_mode(node_id)

                current_node_attribute = "HotWater_State_" + node_id

                hotwater = self.hive_session.products.hotwater
                if len(hotwater) > 0:
                    for current_node_index in range(0, len(hotwater)):
                        if "id" in hotwater[current_node_index]:
                            if hotwater[current_node_index]["id"] == node_id:
                                node_index = current_node_index
                                break

                    if node_index != -1:
                        if "state" in hotwater[node_index] and "status" in hotwater[node_index]["state"]:
                            state_tmp = (hotwater[node_index]["state"]["status"])
                            if state_tmp is None:
                                state_tmp = "OFF"
                            else:
                                if mode_current == "SCHEDULE":
                                    if self.get_boost(node_id) == "ON":
                                        state_tmp = "ON"
                                        state_found = True
                                    else:
                                        if ("state" in
                                                hotwater[node_index] and
                                                    "schedule" in
                                                    hotwater[node_index]
                                                    ["state"]):
                                            snan = self.hive_api.p_get_schedule_now_next_later(
                                                hotwater[node_index]["state"]["schedule"])
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
                hotwater_mode_current = self.get_mode(node_id)

                if hotwater_mode_current == "SCHEDULE":
                    node_index = -1

                    hotwater = self.hive_session.products.hotwater
                    if len(hotwater) > 0:
                        for current_node_index in range(0, len(hotwater)):
                            if "id" in hotwater[current_node_index]:
                                if hotwater[current_node_index]["id"] == node_id:
                                    node_index = current_node_index
                                    break

                    if node_index != -1:
                        snan = self.hive_api.p_get_schedule_now_next_later(
                            hotwater[node_index]["state"]["schedule"])
                    else:
                        snan = None
                else:
                    snan = None

                return snan

            def set_mode(self, node_id, new_mode):
                """Set hot water mode."""
                self.hive_api.check_hive_api_logon()

                set_mode_success = False

                if self.hive_session.session_id is not None:
                    node_index = -1
                    hotwater = self.hive_session.products.hotwater
                    if len(hotwater) > 0:
                        for current_node_index in range(0, len(hotwater)):
                            if "id" in hotwater[current_node_index]:
                                if hotwater[current_node_index]["id"] == node_id:
                                    node_index = current_node_index
                                    break

                        if node_index != -1:
                            if "id" in hotwater[node_index]:
                                json_string_content = ""
                                if new_mode == "SCHEDULE":
                                    json_string_content = '{"mode": "SCHEDULE"}'
                                elif new_mode == "ON":
                                    json_string_content = '{"mode": "MANUAL"}'
                                elif new_mode == "OFF":
                                    json_string_content = '{"mode": "OFF"}'

                                if new_mode == "SCHEDULE" or new_mode == "ON" or new_mode == "OFF":
                                    hive_api_url = (self.hive_api.details.urls.nodes + "/hotwater/" +
                                                    hotwater[node_index]["id"])
                                    api_resp_d = self.hive_api.json_call("POST", hive_api_url, json_string_content,
                                                                         False)

                                    api_resp = api_resp_d['original']

                                    if str(api_resp) == "<Response [200]>":
                                        self.hive_api.get_nodes(node_id)
                                        #                                    fire_bus_event(node_id, device_type)
                                        set_mode_success = True

                return set_mode_success

        class Light:
            """Hive Lights."""

            def __init__(self, hive_api) -> None:
                self.hive_api = hive_api
                self.hive_session = hive_api.session
                super().__init__()

            def get_state(self, node_id):
                """Get light current state."""
                node_index = -1

                light_state_tmp = "UNKNOWN"
                light_state_found = False

                current_node_attribute = "Light_State_" + node_id

                light = self.hive_session.products.light
                if len(light) > 0:
                    for current_node_index in range(0, len(light)):
                        if "id" in light[current_node_index]:
                            if light[current_node_index]["id"] == node_id:
                                node_index = current_node_index
                                break

                    if node_index != -1:
                        if "state" in light[node_index] and "status" in light[node_index]["state"]:
                            light_state_tmp = (light[node_index]
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

                light_brightness_tmp = 0
                light_brightness_found = False

                current_node_attribute = "Light_Brightness_" + node_id

                lights = self.hive_session.products.light
                if len(lights) > 0:
                    for current_node_index in range(0, len(lights)):
                        if "id" in lights[current_node_index]:
                            if lights[current_node_index]["id"] == node_id:
                                node_index = current_node_index
                                break

                    if node_index != -1:
                        if "state" in lights[node_index] and "brightness" in lights[node_index]["state"]:
                            light_brightness_tmp = (lights[node_index]["state"]["brightness"])
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

            def get_min_colour_temp(self, node_id):
                """Get light minimum colour temperature."""
                node_index = -1

                light_min_color_temp_tmp = 0
                light_min_color_temp_found = False

                node_attrib = "Light_Min_Color_Temp_" + node_id

                lights = self.hive_session.products.light
                if len(lights) > 0:
                    for current_node_index in range(0, len(lights)):
                        if "id" in lights[current_node_index]:
                            if lights[current_node_index]["id"] == node_id:
                                node_index = current_node_index
                                break

                    if node_index != -1:
                        if ("props" in lights[node_index] and
                                "colourTemperature" in lights[node_index]["props"] and
                                "max" in lights[node_index]["props"]["colourTemperature"]):
                            light_min_color_temp_tmp = (lights[node_index]["props"]["colourTemperature"]["max"])
                            light_min_color_temp_found = True

                if light_min_color_temp_found:
                    NODE_ATTRIBS[node_attrib] = light_min_color_temp_tmp
                    light_min_color_temp_return = round((1 / light_min_color_temp_tmp) * 1000000)
                else:
                    if node_attrib in NODE_ATTRIBS:
                        light_min_color_temp_return = (NODE_ATTRIBS.get(node_attrib))
                    else:
                        light_min_color_temp_return = 0

                return light_min_color_temp_return

            def get_max_colour_temp(self, node_id):
                """Get light maximum colour temperature."""
                node_index = -1

                light_max_color_temp_tmp = 0
                light_max_color_temp_found = False

                node_attrib = "Light_Max_Color_Temp_" + node_id

                lights = self.hive_session.products.light
                if len(lights) > 0:
                    for current_node_index in range(0, len(lights)):
                        if "id" in lights[current_node_index]:
                            if lights[current_node_index]["id"] == node_id:
                                node_index = current_node_index
                                break

                    if node_index != -1:
                        if ("props" in lights[node_index] and
                                    "colourTemperature" in lights[node_index]["props"] and
                                    "min" in lights[node_index]["props"]["colourTemperature"]):
                            light_max_color_temp_tmp = (lights[node_index]["props"]["colourTemperature"]["min"])
                            light_max_color_temp_found = True

                if light_max_color_temp_found:
                    NODE_ATTRIBS[node_attrib] = light_max_color_temp_tmp
                    light_max_color_temp_return = round((1 / light_max_color_temp_tmp) * 1000000)
                else:
                    if node_attrib in NODE_ATTRIBS:
                        light_max_color_temp_return = NODE_ATTRIBS.get(node_attrib)
                    else:
                        light_max_color_temp_return = 0

                return light_max_color_temp_return

            def get_color_temp(self, node_id):
                """Get light current colour temperature."""
                node_index = -1

                light_color_temp_tmp = 0
                light_color_temp_found = False

                current_node_attribute = "Light_Color_Temp_" + node_id

                lights = self.hive_session.products.light
                if len(lights) > 0:
                    for current_node_index in range(0, len(lights)):
                        if "id" in lights[current_node_index]:
                            if lights[current_node_index]["id"] == node_id:
                                node_index = current_node_index
                                break

                    if node_index != -1:
                        if ("state" in lights[node_index] and
                                    "colourTemperature" in lights[node_index]["state"]):
                            light_color_temp_tmp = (lights[node_index]["state"]["colourTemperature"])
                            light_color_temp_found = True

                if light_color_temp_found:
                    NODE_ATTRIBS[current_node_attribute] = light_color_temp_tmp
                    light_color_temp_return = round((1 / light_color_temp_tmp) * 1000000)
                else:
                    if current_node_attribute in NODE_ATTRIBS:
                        light_color_temp_return = NODE_ATTRIBS.get(current_node_attribute)
                    else:
                        light_color_temp_return = 0

                return light_color_temp_return

            def turn_off(self, node_id):
                """Set light to turn off."""
                self.hive_api.check_hive_api_logon()

                node_index = -1

                set_mode_success = False

                if self.hive_session.session_id is not None:
                    lights = self.hive_session.products.light
                    if len(lights) > 0:
                        for current_node_index in range(0, len(lights)):
                            if "id" in lights[current_node_index]:
                                if lights[current_node_index]["id"] == node_id:
                                    node_index = current_node_index
                                    break
                        if node_index != -1:
                            json_string_content = '{"status": "OFF"}'
                            hive_api_url = (self.hive_api.details.urls.nodes
                                            + '/'
                                            + lights[node_index]["type"]
                                            + '/'
                                            + lights[node_index]["id"])
                            api_resp_d = self.hive_api.json_call("POST", hive_api_url, json_string_content, False)

                            api_resp = api_resp_d['original']

                            if str(api_resp) == "<Response [200]>":
                                self.hive_api.get_nodes(node_id)
                                set_mode_success = True

                return set_mode_success

            def turn_on(self, node_id):
                """Set light to turn on."""
                self.hive_api.check_hive_api_logon()

                node_index = -1

                set_mode_success = False
                api_resp = ""

                if self.hive_session.session_id is not None:
                    if len(self.hive_session.products.light) > 0:
                        for cni in range(0, len(self.hive_session.products.light)):
                            if "id" in self.hive_session.products.light[cni]:
                                if self.hive_session.products.light[cni]["id"] == node_id:
                                    node_index = cni
                                    break
                        if node_index != -1:
                            json_string_content = '{"status": "ON"}'
                            hive_api_url = (self.hive_api.details.urls.nodes
                                            + '/' + self.hive_session.products.light[node_index][
                                                "type"]
                                            + '/' + self.hive_session.products.light[node_index][
                                                "id"])
                            api_resp_d = self.hive_api.json_call("POST", hive_api_url, json_string_content, False)

                            api_resp = api_resp_d['original']

                        if str(api_resp) == "<Response [200]>":
                            self.hive_api.get_nodes(node_id)
                            set_mode_success = True

                return set_mode_success

            def set_brightness(self, node_id, new_brightness):
                """Set light to turn on."""
                self.hive_api.check_hive_api_logon()

                node_index = -1

                set_mode_success = False
                api_resp = ""

                if self.hive_session.session_id is not None:
                    lights = self.hive_session.products.light
                    if len(lights) > 0:
                        for cni in range(0, len(lights)):
                            if "id" in lights[cni]:
                                if lights[cni]["id"] == node_id:
                                    node_index = cni
                                    break
                        if node_index != -1:
                            json_string_content = ('{"status": "ON", "brightness": ' + str(new_brightness) + '}')
                            hive_api_url = (self.hive_api.details.urls.nodes
                                            + '/' + lights[node_index][
                                                "type"]
                                            + '/' + lights[node_index][
                                                "id"])
                            api_resp_d = self.hive_api.json_call("POST", hive_api_url, json_string_content, False)

                            api_resp = api_resp_d['original']

                        if str(api_resp) == "<Response [200]>":
                            self.hive_api.get_nodes(node_id)
                            set_mode_success = True

                return set_mode_success

            def set_colour_temp(self, node_id, new_colour_temp):
                """Set light to turn on."""
                self.hive_api.check_hive_api_logon()

                node_index = -1

                set_mode_success = False
                api_resp = ""

                if self.hive_session.session_id is not None:
                    lights = self.hive_session.products.light
                    if len(lights) > 0:
                        for cni in range(0, len(lights)):
                            if "id" in lights[cni]:
                                if lights[cni]["id"] == node_id:
                                    node_index = cni
                                    break
                        if node_index != -1:
                            json_string_content = ('{"colourTemperature": '
                                                   + str(new_colour_temp)
                                                   + '}')
                            hive_api_url = (self.hive_api.details.urls.nodes
                                            + '/' + lights[node_index][
                                                "type"]
                                            + '/' + lights[node_index][
                                                "id"])
                            api_resp_d = self.hive_api.json_call("POST", hive_api_url, json_string_content, False)

                            api_resp = api_resp_d['original']

                        if str(api_resp) == "<Response [200]>":
                            self.hive_api.get_nodes(node_id)
                            set_mode_success = True

                return set_mode_success

        class Sensor:
            """Hive Sensors."""

            def __init__(self, hive_api) -> None:
                self.hive_api = hive_api
                self.hive_session = hive_api.session
                super().__init__()

            def hub_online_status(self, node_id):
                """Get the online status of the Hive hub."""
                return_status = "Offline"

                for a_hub in self.hive_session.devices.hub:
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

                battery_level_tmp = 0
                battery_level_found = False
                all_devices = self.hive_session.devices.thermostat + self.hive_session.devices.sensors

                current_node_attribute = "BatteryLevel_" + node_id

                if len(self.hive_session.devices.thermostat) > 0 or len(self.hive_session.devices.sensors) > 0:
                    for current_node_index in range(0, len(all_devices)):
                        if "id" in all_devices[current_node_index]:
                            if all_devices[current_node_index]["id"] == node_id:
                                node_index = current_node_index
                                break

                    if node_index != -1:
                        if "props" in all_devices[node_index] and "battery" in all_devices[node_index]["props"]:
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
                sensor_found = False

                current_node_attribute = "Sensor_State_" + node_id

                if len(self.hive_session.products.sensors) > 0:
                    for current_node_index in range(0, len(self.hive_session.products.sensors)):
                        if "id" in self.hive_session.products.sensors[current_node_index]:
                            if self.hive_session.products.sensors[current_node_index]["id"] == node_id:
                                node_index = current_node_index
                                break

                    if node_index != -1:
                        if node_device_type == "contactsensor":
                            state = (self.hive_session.products.sensors[node_index]["props"]["status"])
                            if state == 'OPEN':
                                sensor_state_tmp = True
                        elif node_device_type == "motionsensor":
                            sensor_state_tmp = (
                                self.hive_session.products.sensors[node_index]["props"]["motion"]["status"])
                    if sensor_state_tmp:
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
                hive_device_mode_found = False
                all_devices = self.hive_session.products.light + self.hive_session.products.plug

                current_node_attribute = "Device_Mode_" + node_id

                if len(self.hive_session.products.light) > 0 or len(self.hive_session.products.plug) > 0:
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

        class Switch:
            """Hive Switches."""

            def __init__(self, hive_api) -> None:
                self.hive_api = hive_api
                self.hive_session = hive_api.session
                super().__init__()

            def get_state(self, node_id):
                """Get smart plug current state."""
                node_index = -1

                smartplug_state_tmp = "UNKNOWN"
                smartplug_state_found = False

                current_node_attribute = "Smartplug_State_" + node_id

                if len(self.hive_session.products.plug) > 0:
                    for current_node_index in range(0, len(self.hive_session.products.plug)):
                        if "id" in self.hive_session.products.plug[current_node_index]:
                            if self.hive_session.products.plug[current_node_index]["id"] == node_id:
                                node_index = current_node_index
                                break

                    if node_index != -1:
                        if ("state" in self.hive_session.products.plug[node_index] and
                                "status" in self.hive_session.products.plug[node_index]["state"]):
                            smartplug_state_tmp = (self.hive_session.products.plug[node_index]["state"]["status"])
                            smartplug_state_found = True

                if smartplug_state_found:
                    NODE_ATTRIBS[current_node_attribute] = smartplug_state_tmp
                    smartplug_state_return = smartplug_state_tmp
                else:
                    if current_node_attribute in NODE_ATTRIBS:
                        smartplug_state_return = NODE_ATTRIBS.get(current_node_attribute)
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
                current_power_found = False

                current_node_attribute = "Smartplug_Current_Power_" + node_id

                if len(self.hive_session.products.plug) > 0:
                    for current_node_index in range(0, len(self.hive_session.products.plug)):
                        if "id" in self.hive_session.products.plug[current_node_index]:
                            if self.hive_session.products.plug[current_node_index]["id"] == node_id:
                                node_index = current_node_index
                                break

                    if node_index != -1:
                        if ("props" in self.hive_session.products.plug[node_index] and
                                "powerConsumption" in self.hive_session.products.plug[node_index]["props"]):
                            current_power_tmp = (
                                self.hive_session.products.plug[node_index]["props"]["powerConsumption"])
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
                self.hive_api.check_hive_api_logon()

                node_index = -1

                set_mode_success = False

                if self.hive_session.session_id is not None:
                    if len(self.hive_session.products.plug) > 0:
                        for current_node_index in range(0, len(self.hive_session.products.plug)):
                            if "id" in self.hive_session.products.plug[current_node_index]:
                                if self.hive_session.products.plug[current_node_index]["id"] == node_id:
                                    node_index = current_node_index
                                    break
                        if node_index != -1:
                            json_string_content = '{"status": "ON"}'
                            hive_api_url = (self.hive_api.details.urls.nodes
                                            + '/'
                                            + self.hive_session.products.plug[node_index]["type"]
                                            + '/'
                                            + self.hive_session.products.plug[node_index]["id"])
                            api_resp_d = self.hive_api.json_call("POST", hive_api_url, json_string_content, False)

                            api_resp = api_resp_d['original']

                            if str(api_resp) == "<Response [200]>":
                                self.hive_api.get_nodes(node_id)
                                set_mode_success = True

                return set_mode_success

            def turn_off(self, node_id, ):
                """Set smart plug to turn off."""
                self.hive_api.check_hive_api_logon()

                node_index = -1

                set_mode_success = False

                if self.hive_session.session_id is not None:
                    if len(self.hive_session.products.plug) > 0:
                        for current_node_index in range(0, len(self.hive_session.products.plug)):
                            if "id" in self.hive_session.products.plug[current_node_index]:
                                if self.hive_session.products.plug[current_node_index]["id"] == node_id:
                                    node_index = current_node_index
                                    break
                        if node_index != -1:
                            json_string_content = '{"status": "OFF"}'
                            hive_api_url = (self.hive_api.details.urls.nodes
                                            + '/'
                                            + self.hive_session.products.plug[node_index]["type"]
                                            + '/'
                                            + self.hive_session.products.plug[node_index]["id"])
                            api_resp_d = self.hive_api.json_call("POST", hive_api_url, json_string_content, False)

                            api_resp = api_resp_d['original']

                            if str(api_resp) == "<Response [200]>":
                                self.hive_api.get_nodes(node_id)
                                set_mode_success = True

                return set_mode_success

        class Weather:
            """Hive Weather."""

            def __init__(self, hive_api) -> None:
                self.hive_api = hive_api
                self.hive_session = hive_api.session
                super().__init__()

            def temperature(self):
                """Get Hive Weather temperature."""
                return self.hive_session.weather.temperature.value

        if device == Pyhiveapi.Device.Heating:
            return Heating(self.hive_api)
        elif device == Pyhiveapi.Device.Hotwater:
            return Hotwater(self.hive_api)
        elif device == Pyhiveapi.Device.Light:
            return Light(self.hive_api)
        elif device == Pyhiveapi.Device.Sensor:
            return Sensor(self.hive_api)
        elif device == Pyhiveapi.Device.Switch:
            return Switch(self.hive_api)
        elif device == Pyhiveapi.Device.Weather:
            return Weather(self.hive_api)
