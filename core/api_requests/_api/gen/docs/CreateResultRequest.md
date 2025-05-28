# CreateResultRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**correlation_id** | **str** | Идентификатор пакета результатов. Можно любой рандомный уникальный, например GUID. Будет использоваться для предотвращения повторной обработки одного и того же запроса | 
**discipline_id** | **str** | Идентификатор дисциплины | 
**competition_id** | **str** | Идентификатор игры из турнирной сетки, если дисциплина isTournament&#x3D;true | [optional] 
**results** | [**List[Optional[OneOf]]**](OneOf.md) | Если есть competitionId, то в результатах должно быть только две команды | 

## Example

```python
from openapi_client.models.create_result_request import CreateResultRequest

# TODO update the JSON string below
json = "{}"
# create an instance of CreateResultRequest from a JSON string
create_result_request_instance = CreateResultRequest.from_json(json)
# print the JSON string representation of the object
print(CreateResultRequest.to_json())

# convert the object into a dict
create_result_request_dict = create_result_request_instance.to_dict()
# create an instance of CreateResultRequest from a dict
create_result_request_from_dict = CreateResultRequest.from_dict(create_result_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


