# Weathersummary component

## Installation

To install this integration you will need to add this as a custom repository in HACS.
Open HACS page, then click integrations
Click the three dots top right, select Custom repositories

1. URL enter <https://github.com/cestlagalere/weathersummary>
2. Catgory select Integration
3. click Add

Once installed you will then be able to install this integration from the HACS integrations page.

Restart your Home Assistant to complete the installation.

## Configuration

    - platform: weathersummary
      name: temperature_max_next_24
      method: maximum
      device_class: temperature
      weather: weather.openweathermap
    
    - platform: weathersummary
      name: rain_next_24
      method: sum
      device_class: rain
      weather: weather.openweathermap


method: maximum, minimum, sum

weather: points to a weather entity

device_class: attribute of the weather entity
