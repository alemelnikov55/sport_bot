# openapi_client.DisciplinesApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_disciplines**](DisciplinesApi.md#get_disciplines) | **GET** /referee-integration/api/v1/disciplines | Получение списка спортивных дисциплин


# **get_disciplines**
> GetDisciplines200Response get_disciplines()

Получение списка спортивных дисциплин

### Example


```python
import openapi_client
from openapi_client.models.get_disciplines200_response import GetDisciplines200Response
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
    api_instance = openapi_client.DisciplinesApi(api_client)

    try:
        # Получение списка спортивных дисциплин
        api_response = api_instance.get_disciplines()
        print("The response of DisciplinesApi->get_disciplines:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DisciplinesApi->get_disciplines: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**GetDisciplines200Response**](GetDisciplines200Response.md)

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

