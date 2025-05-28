# Discipline

Спортивная дисциплина

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | Идентификатор | 
**name** | **str** | Название дисциплины | 
**is_tournament** | **bool** | Турнирная дисциплина | 
**is_team** | **bool** | Командная или индивидиуальная дисциплина | 
**result_type** | **str** | Тип результатов соревнований по дисциплине | 

## Example

```python
from openapi_client.models.discipline import Discipline

# TODO update the JSON string below
json = "{}"
# create an instance of Discipline from a JSON string
discipline_instance = Discipline.from_json(json)
# print the JSON string representation of the object
print(Discipline.to_json())

# convert the object into a dict
discipline_dict = discipline_instance.to_dict()
# create an instance of Discipline from a dict
discipline_from_dict = Discipline.from_dict(discipline_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


