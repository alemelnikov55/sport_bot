# openapi_client.DivisionsApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_divisions**](DivisionsApi.md#get_divisions) | **GET** /referee-integration/api/v1/divisions | Получение списка филиалов


# **get_divisions**
> GetDivisions200Response get_divisions()

Получение списка филиалов

### Example


```python
import openapi_client
from openapi_client.models.get_divisions200_response import GetDivisions200Response
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
    api_instance = openapi_client.DivisionsApi(api_client)

    try:
        # Получение списка филиалов
        api_response = api_instance.get_divisions()
        print("The response of DivisionsApi->get_divisions:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DivisionsApi->get_divisions: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**GetDivisions200Response**](GetDivisions200Response.md)

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

