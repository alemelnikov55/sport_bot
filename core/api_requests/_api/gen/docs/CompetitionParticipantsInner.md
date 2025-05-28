# CompetitionParticipantsInner


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**division_id** | **str** | Идентификатор филиала | [optional] 

## Example

```python
from openapi_client.models.competition_participants_inner import CompetitionParticipantsInner

# TODO update the JSON string below
json = "{}"
# create an instance of CompetitionParticipantsInner from a JSON string
competition_participants_inner_instance = CompetitionParticipantsInner.from_json(json)
# print the JSON string representation of the object
print(CompetitionParticipantsInner.to_json())

# convert the object into a dict
competition_participants_inner_dict = competition_participants_inner_instance.to_dict()
# create an instance of CompetitionParticipantsInner from a dict
competition_participants_inner_from_dict = CompetitionParticipantsInner.from_dict(competition_participants_inner_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


