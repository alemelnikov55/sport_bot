# Athlete


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** | Идентификатор аккаунта | 
**first_name** | **str** | Имя | 
**last_name** | **str** | Фамилия | 
**middle_name** | **str** | Отчество | 
**division_id** | **str** | Идентификатор филиала | 

## Example

```python
from openapi_client.models.athlete import Athlete

# TODO update the JSON string below
json = "{}"
# create an instance of Athlete from a JSON string
athlete_instance = Athlete.from_json(json)
# print the JSON string representation of the object
print(Athlete.to_json())

# convert the object into a dict
athlete_dict = athlete_instance.to_dict()
# create an instance of Athlete from a dict
athlete_from_dict = Athlete.from_dict(athlete_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


