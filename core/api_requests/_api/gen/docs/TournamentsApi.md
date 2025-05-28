# openapi_client.TournamentsApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**update_tournament_stages**](TournamentsApi.md#update_tournament_stages) | **POST** /referee-integration/api/v1/tournaments | Отправка турнирной сетки


# **update_tournament_stages**
> update_tournament_stages(update_tournament_stages_request)

Отправка турнирной сетки

### Example


```python
import openapi_client
from openapi_client.models.update_tournament_stages_request import UpdateTournamentStagesRequest
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
    api_instance = openapi_client.TournamentsApi(api_client)
    update_tournament_stages_request = {"disciplineId":"507f1f77bcf86cd799439011","tournament":[{"stage":"1/4","competitions":[{"id":"68000ff8fa9fb49584df8000","status":"ended","participants":[{"divisionId":"507f1f77bcf86cd799439015"},{"divisionId":"507f1f77bcf86cd799439018"}]}]},{"stage":"1/2","competitions":[{"id":"68000ff8fa9fb49584df8001","status":"ongoing","participants":[{"divisionId":"507f1f77bcf86cd799439015"},{"divisionId":"507f1f77bcf86cd799439018"}]},{"id":"68000ff8fa9fb49584df8002","status":"planned","participants":[{"divisionId":"507f1f77bcf86cd799439015"},{"divisionId":"507f1f77bcf86cd799439018"}]}]},{"stage":"Финал","competitions":[{"id":"68000ff8fa9fb49584df8003","status":"upcoming","participants":[{"divisionId":"507f1f77bcf86cd799439015"},{}]}]}]} # UpdateTournamentStagesRequest | 

    try:
        # Отправка турнирной сетки
        api_instance.update_tournament_stages(update_tournament_stages_request)
    except Exception as e:
        print("Exception when calling TournamentsApi->update_tournament_stages: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **update_tournament_stages_request** | [**UpdateTournamentStagesRequest**](UpdateTournamentStagesRequest.md)|  | 

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

