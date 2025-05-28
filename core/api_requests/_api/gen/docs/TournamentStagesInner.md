# TournamentStagesInner


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**stage** | **str** | Название этапа турнира - 1/8, 1/4 и т.д. | 
**competitions** | [**List[Competition]**](Competition.md) |  | 

## Example

```python
from openapi_client.models.tournament_stages_inner import TournamentStagesInner

# TODO update the JSON string below
json = "{}"
# create an instance of TournamentStagesInner from a JSON string
tournament_stages_inner_instance = TournamentStagesInner.from_json(json)
# print the JSON string representation of the object
print(TournamentStagesInner.to_json())

# convert the object into a dict
tournament_stages_inner_dict = tournament_stages_inner_instance.to_dict()
# create an instance of TournamentStagesInner from a dict
tournament_stages_inner_from_dict = TournamentStagesInner.from_dict(tournament_stages_inner_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


