from pydantic import BaseModel, Field, field_validator
from typing import List, Dict, Optional, Any


class Participant(BaseModel):
    full_name: str = Field(..., alias="ФИО участника")
    short_name: str = Field(..., alias="Фамилия")
    gender: str = Field(..., alias="Пол")
    team_id: Optional[str] = Field(None, alias="Команда")
    participant_id: Optional[int] = Field(None, alias="Номер")
    age: Optional[int] = Field(None, alias="Возраст")
    sports: List[str]

    @field_validator("gender", mode="before")
    @classmethod
    def convert_gender(cls, value: str) -> str:
        return "M" if value.lower().startswith("м") else "F"


def transform_participant(data: Dict, counter: Dict) -> Participant:
    if "Номер" not in data or data["Номер"] is None:
        if "_counter" not in counter:
            counter["_counter"] = 9000
        counter["_counter"] += 1
        data["Номер"] = counter["_counter"]
    return Participant(**data)


def transform_participants(data_list: List[Dict[str, Any]], missing_counter: Dict[str, int]) -> List[Dict[str, Any]]:
    return [transform_participant(data, missing_counter).model_dump() for data in data_list]
