from datetime import datetime, timedelta, timezone
import logging

import voluptuous as vol

from homeassistant.components.sensor import PLATFORM_SCHEMA

import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity

from homeassistant.util import Throttle
import homeassistant.util.dt as dt_util

from homeassistant.const import (
    ATTR_ATTRIBUTION,
    CONF_DEVICE_CLASS,
    CONF_NAME,
    CONF_MAXIMUM,
    CONF_MINIMUM,
    CONF_METHOD,
)

# add a few others not defined in homeassistant
CONF_MEAN = "mean"
CONF_DIFFERENCE = "difference"
CONF_SUM = "sum"
CONF_WEATHER = "weather"

DEFAULT_NAME = "MA"
ATTRIBUTION = "Data provided by {0}"

MIN_TIME_BETWEEN_UPDATES = timedelta(seconds=60 * 60) # hourly

DEVICE_CLASS = {
    "temperature": "Temperature",
    "rain": "Rain",
    "wind_speed": "Wind speed",
}

METHOD_TYPES = [
    CONF_MAXIMUM,
    CONF_MINIMUM,
    CONF_MEAN,
    CONF_DIFFERENCE,
    CONF_SUM,
]

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
        vol.Required(CONF_DEVICE_CLASS): vol.In(DEVICE_CLASS),
        vol.Required(CONF_METHOD): vol.In(METHOD_TYPES),
        vol.Required(CONF_WEATHER): cv.string
    }
)

_LOGGER = logging.getLogger(__name__)
DOMAIN = "weathersummary"

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    name = config.get(CONF_NAME)
    device_class = config.get(CONF_DEVICE_CLASS)
    method = config.get(CONF_METHOD)
    weather = config.get(CONF_WEATHER)

    async_add_entities(
        [WeatherSummary(name, device_class, method, weather)],
        False,
    )


class WeatherSummary(Entity):
    def __init__(self, name, device_class, method, weather):
        """Initialize the sensor."""
        self._name = name
        self._device_class = device_class
        self._method = method
        self._weather = weather
        self._state = None
        self._unit_of_measurement = ""

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    @property
    def unit_of_measurement(self):
        return self._unit_of_measurement

    @property
    def device_state_attributes(self):
         return {ATTR_ATTRIBUTION: ATTRIBUTION.format(self._weather)}


    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):
        """Get the latest data from Mobile Alerts and updates the state."""

        weather = self.hass.states.get(self._weather)
        forecasts = weather.attributes.get("forecast", [])

        if self._device_class == "temperature":
            self._unit_of_measurement = "C"
        elif self._device_class == "rain":
            self._unit_of_measurement = "mm"
            if 'precipitation' not in forecasts[0]:
                self._state = 0
                return

        now = dt_util.utcnow()

        values = []
        for forecast in forecasts:
            if type(forecast["datetime"]) == int:
                d = datetime.utcfromtimestamp(forecast["datetime"] / 1000)
            elif type(forecast["datetime"]) == datetime:
                d = forecast["datetime"]
                #_LOGGER.info("forecast is datetime {} {}".format(type(forecast["datetime"]), forecast["datetime"]))
            else:
                d = datetime.fromisoformat(forecast["datetime"])

            #self.logdt("forecast", d)
            #self.logdt("now", now)

            if d - now > timedelta(days=1):
                continue

            if self._device_class == "temperature":
                values.append(float(forecast["temperature"]))
            elif self._device_class == "rain":
                if forecast["precipitation"] is None:
                    values.append(0)
                else:
                    values.append(float(forecast["precipitation"]))

        if self._method == CONF_MAXIMUM:
            result = max(values)
        elif self._method == CONF_MINIMUM:
            result = min(values)
        elif self._method == CONF_MEAN:
            result = sum(values) / len(values) 
        elif self._method == CONF_DIFFERENCE:
            end = float(values[0])
            start = float(values[-1])
            result = end - start
        elif self._method == CONF_SUM:
            result = sum(values)

        if result > 100:
            result = int(result)
        else:
            result = round(result, 1)

        if self._device_class == "temperature" and len(values) == 0:
            self._state = "unknown"
        else:
            self._state = result

    def logdt(self, info, dt):
        _LOGGER.info("{} tzinfo {}".format(info, dt.tzinfo))
        if dt.tzinfo is not None:
            _LOGGER.info("{} tzinfo {}".format(info, dt.tzinfo.utcoffset(dt)))
