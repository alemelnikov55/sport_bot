# GetDivisions200ResponseItemsInner


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | ObjectId филиала | 
**name** | **str** | Название филиала | 

## Example

```python
from openapi_client.models.get_divisions200_response_items_inner import GetDivisions200ResponseItemsInner

# TODO update the JSON string below
json = "{}"
# create an instance of GetDivisions200ResponseItemsInner from a JSON string
get_divisions200_response_items_inner_instance = GetDivisions200ResponseItemsInner.from_json(json)
# print the JSON string representation of the object
print(GetDivisions200ResponseItemsInner.to_json())

# convert the object into a dict
get_divisions200_response_items_inner_dict = get_divisions200_response_items_inner_instance.to_dict()
# create an instance of GetDivisions200ResponseItemsInner from a dict
get_divisions200_response_items_inner_from_dict = GetDivisions200ResponseItemsInner.from_dict(get_divisions200_response_items_inner_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


