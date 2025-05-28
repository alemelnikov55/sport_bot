# GetAthletes200ResponseItemsInner


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** |  | 
**first_name** | **str** |  | [optional] 
**last_name** | **str** |  | [optional] 
**middle_name** | **str** |  | [optional] 
**birth_date** | **date** | Дата рождения, формат даты ISO. Обязательно для спортсмена. Используется для вычисления возрастной категории | [optional] 
**weight** | **float** | Вес в кг. Обязательно для спортсмена. Используется для вычисления весовой категории | [optional] 
**gender** | **str** | Пол. Обязательно для спортсмена | [optional] 
**division_id** | **str** |  | [optional] 
**disciplines** | **List[str]** |  | [optional] 

## Example

```python
from openapi_client.models.get_athletes200_response_items_inner import GetAthletes200ResponseItemsInner

# TODO update the JSON string below
json = "{}"
# create an instance of GetAthletes200ResponseItemsInner from a JSON string
get_athletes200_response_items_inner_instance = GetAthletes200ResponseItemsInner.from_json(json)
# print the JSON string representation of the object
print(GetAthletes200ResponseItemsInner.to_json())

# convert the object into a dict
get_athletes200_response_items_inner_dict = get_athletes200_response_items_inner_instance.to_dict()
# create an instance of GetAthletes200ResponseItemsInner from a dict
get_athletes200_response_items_inner_from_dict = GetAthletes200ResponseItemsInner.from_dict(get_athletes200_response_items_inner_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


