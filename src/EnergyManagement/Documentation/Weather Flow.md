# Weather Data Management Workflow
## Table of Contents

1. [Summary](#1-summary)
2. [Code Files](#2-code-files)
3. [Files Path](#3-files-path)
4. [Description](#4-description)
   1. [`weather_test.py`](#41-weather_testpy)
      1. [Purpose](#purpose)
      2. [Imports](#imports)
      3. [Functions](#functions)
         1. [`get_weather()`](#1-get_weather)
            1. [Description](#description)
            2. [Arguments](#arguments)
            3. [Returns](#returns)
      4. [API Configuration](#api-configuration)
         1. [`url`](#1-url)
         2. [`params`](#2-params)
      5. [Weather Data Variables](#weather-data-variables)
         1. [`temp_c`](#1-temp_c)
         2. [`pressure_hpa`](#2-pressure_hpa)
         3. [`cloud_cover`](#3-cloud_cover)
         4. [`rain_mm`](#4-rain_mm)
         5. [`wind_speed_ms`](#5-wind_speed_ms)
         6. [`ghi`](#6-ghi)
      6. [Air Density Calculation](#air-density-calculation)
         1. [`temp_k`](#1-temp_k)
         2. [`pressure_pa`](#2-pressure_pa)
         3. [`R_specific`](#3-r_specific)
         4. [`air_density`](#4-air_density)
      7. [Output and Return Values](#output-and-return-values)



## 1. Summary:
This document describes the weather data management and how it is used for the EMS (Energy Management System). In addition the document explains the logic behind the implementation.

Part of the development of the EMS will be done using Open-Meteo. This is an open-source weather API that provides the environmental data of a specific geographic location. The API is used to retrieve current environmental variables such as temperature, atmospheric pressure, cloud cover, precipitation, wind speed, and solar radiation. These values are then processed by the weather_test.py file to calculate additional variables required by the EMS.


## 2. Code Files:
These are the files that are described in this document.

- File 1: `weather_test.py`


## 3. Files Path:
These are the paths where the files can be found.

- Path 1: `src\DataCollection\weather_test.py`



## 4. Description:

This section describes the logic and workflow of the previously mentioned files.


### 4.1: `weather_test.py`

### Purpose:
This file contains all the necessary functions and variables regarding the
weather data that will be used for the EMS. This file retrieves real-time
environmental data from the Open-Meteo API and calculates the remaining
variables that will be discussed later on. This section describes the implementation of the `weather_test.py` file. This includes the necessary imports, functions, variables, calculations, constants, and the main execution.

#### **Imports**:

- `requests`: This library is imported to allow the program to communicate with the Open-Meteo API through HTTP requests.


#### **Functions**:

#### 1. `get_weather()`

*Description:*

- Retrieves the current environmental data from the Open-Meteo API and calculates
the air density required by the EMS.

*Arguments:*

- `lat`: The latitude of the location from which the weather data is requested.
- `lon`: The longitude of the location from which the weather data is requested.

*Returns:*

A dictionary containing the environmental variables required by the EMS:

- `cloud_cover`: Current cloud cover percentage.
- `v_w`: Current wind speed in meters per second.
- `rho`: Calculated air density in kilograms per cubic meter.
- `ghi`: Global horizontal irradiance in watts per square meter.

Returns `None` if an error occurs while communicating with the API.


#### **API Configuration**

#### 1. `url`
- *Description:*
Defines the URL of the Open-Meteo forecast API used to retrieve the
environmental data.

#### 2. `params`

- *Description:*
Defines the parameters sent to the Open-Meteo API, including the requested
location, environmental variables, and wind speed unit.

#### **Weather Data Variables**

#### 1. `temp_c`

- *Description:*
Stores the current temperature retrieved from the API in degrees Celsius.

#### 2. `pressure_hpa`

- *Description:*
Stores the current surface atmospheric pressure retrieved from the API
in hectopascals (hPa).

#### 3. `cloud_cover`

- *Description:*
Stores the current cloud cover percentage retrieved from the API.

#### 4. `rain_mm`

- *Description:*
Stores the current precipitation in millimeters.

#### 5. `wind_speed_ms`

- *Description:*
Stores the current wind speed in meters per second.

#### 6. `ghi`

- *Description:*
Stores the current solar radiation value used as global horizontal
irradiance (GHI) in watts per square meter.


#### **Air Density Calculation**

#### 1. `temp_k`

- *Description:*
Stores the temperature converted from degrees Celsius to Kelvin.

#### 2. `pressure_pa`

- *Description:*
Stores the atmospheric pressure converted from hectopascals to Pascals.

#### 3. `R_specific`

- *Description:*
Defines the specific gas constant for dry air.

- *Value:*
`287.05 J/(kg·K)`

#### 4. `air_density`

- *Description:*
Stores the calculated air density using the Ideal Gas Law.

*Formula:* 

`ρ = P / (R · T)`

where:
- `ρ` = air density
- `P` = atmospheric pressure in Pascals
- `R` = specific gas constant for dry air
- `T` = temperature in Kelvin


#### **Output and Return Values**

The function prints the retrieved and calculated environmental variables
to the console for verification. The function then returns the following dictionary:

```python
{
    "cloud_cover": cloud_cover,
    "v_w": wind_speed_ms,
    "rho": air_density,
    "ghi": ghi,
}