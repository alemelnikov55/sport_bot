# openapi_client.ResultsApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_result**](ResultsApi.md#create_result) | **POST** /referee-integration/api/v1/results | Отправка результатов спортивного события


# **create_result**
> create_result(create_result_request)

Отправка результатов спортивного события

### Example


```python
import openapi_client
from openapi_client.models.create_result_request import CreateResultRequest
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
    api_instance = openapi_client.ResultsApi(api_client)
    create_result_request = {"correlationId":"3d7bc6c4-72d2-4d01-9db6-d2d4910b2fb7","disciplineId":"507f1f77bcf86cd799439014","results":[{"athleteId":1,"result":10000}]} # CreateResultRequest | 

    try:
        # Отправка результатов спортивного события
        api_instance.create_result(create_result_request)
    except Exception as e:
        print("Exception when calling ResultsApi->create_result: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **create_result_request** | [**CreateResultRequest**](CreateResultRequest.md)|  | 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**204** | Успешный ответ |  -  |
**400** | Ошибка валидации |  -  |
**401** | Ошибка авторизации |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

