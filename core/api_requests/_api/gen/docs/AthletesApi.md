# openapi_client.AthletesApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_athletes**](AthletesApi.md#get_athletes) | **GET** /referee-integration/api/v1/athletes | Получение данных спортсменов


# **get_athletes**
> GetAthletes200Response get_athletes()

Получение данных спортсменов

### Example


```python
import openapi_client
from openapi_client.models.get_athletes200_response import GetAthletes200Response
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.AthletesApi(api_client)

    try:
        # Получение данных спортсменов
        api_response = api_instance.get_athletes()
        print("The response of AthletesApi->get_athletes:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AthletesApi->get_athletes: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**GetAthletes200Response**](GetAthletes200Response.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Успешный ответ |  -  |
**401** | Ошибка авторизации |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

