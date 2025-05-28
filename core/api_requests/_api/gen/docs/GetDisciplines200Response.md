# GetDisciplines200Response


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**items** | [**List[Discipline]**](Discipline.md) |  | 

## Example

```python
from openapi_client.models.get_disciplines200_response import GetDisciplines200Response

# TODO update the JSON string below
json = "{}"
# create an instance of GetDisciplines200Response from a JSON string
get_disciplines200_response_instance = GetDisciplines200Response.from_json(json)
# print the JSON string representation of the object
print(GetDisciplines200Response.to_json())

# convert the object into a dict
get_disciplines200_response_dict = get_disciplines200_response_instance.to_dict()
# create an instance of GetDisciplines200Response from a dict
get_disciplines200_response_from_dict = GetDisciplines200Response.from_dict(get_disciplines200_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


