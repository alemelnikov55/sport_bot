# Competition

Соревнование в рамках дисциплины или турнира по дисциплине

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | Идентификатор соревнования | 
**status** | **str** | Статус результатов по соревнованию: - planned - запланировано, но состав ещё не определён - upcoming - соревнование ожидает начала - ongoing - соревнование идёт - ended - соревнование завершено  | 
**participants** | [**List[CompetitionParticipantsInner]**](CompetitionParticipantsInner.md) |  | 

## Example

```python
from openapi_client.models.competition import Competition

# TODO update the JSON string below
json = "{}"
# create an instance of Competition from a JSON string
competition_instance = Competition.from_json(json)
# print the JSON string representation of the object
print(Competition.to_json())

# convert the object into a dict
competition_dict = competition_instance.to_dict()
# create an instance of Competition from a dict
competition_from_dict = Competition.from_dict(competition_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


