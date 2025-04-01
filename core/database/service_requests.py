from typing import List, Dict, Union

from sqlalchemy import text, select

from database.models import Base, Team, Participant, Sport, ParticipantSport, engine, async_session


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_all_tables():
    """Удаляет все таблицы в базе данных auto_quiz."""

    async with async_session() as session:
        await session.execute(text("DROP SCHEMA public CASCADE;"))
        await session.execute(text("CREATE SCHEMA public;"))
        await session.commit()
        print("Все таблицы удалены.")


async def bulk_create_participants(participants_data: List[Dict]) -> int:
    """
    Добавляет участников, создавая команды и связи.
    Обрабатывает входящий team_name как название команды.
    """
    added_count = 0
    async with async_session() as session:
        async with session.begin():
            # Создаем все уникальные команды из входных данных
            team_names = {data['team_id'] for data in participants_data if 'team_id' in data}
            existing_teams = {}

            # Сначала создаем все необходимые команды
            for team_name in team_names:
                # Проверяем существование команды
                team = await session.execute(
                    select(Team).where(Team.name == team_name)
                )
                team = team.scalar_one_or_none()

                if not team:
                    team = Team(name=team_name)
                    session.add(team)

                await session.flush()  # Фиксируем все команды

                # Получаем ID всех команд
                teams = await session.execute(select(Team))
                team_name_to_id = {team.name: team.team_id for team in teams.scalars()}

                # Обрабатываем участников
                sports_cache = {}
                for data in participants_data:
                    if await session.get(Participant, data["participant_id"]):
                        continue

                    # Получаем team_id (теперь он точно есть)
                    team_id = team_name_to_id.get(data['team_id']) if 'team_id' in data else None

                    participant = Participant(
                        participant_id=data["participant_id"],
                        full_name=data["full_name"],
                        short_name=data["short_name"],
                        gender=data["gender"],
                        age=data["age"],
                        team_id=team_id
                    )

                    session.add(participant)
                    added_count += 1
                    await session.flush()

                    # Обрабатываем виды спорта
                    for sport_name in data.get("sports", []):
                        if sport_name not in sports_cache:
                            sport = await session.execute(
                                select(Sport).where(Sport.name == sport_name))
                            sport = sport.scalar_one_or_none()

                            if not sport:
                                sport = Sport(name=sport_name)
                                session.add(sport)
                                await session.flush()

                            sports_cache[sport_name] = sport.sport_id

                        session.add(ParticipantSport(
                            participant_id=data["participant_id"],
                            sport_id=sports_cache[sport_name]
                        ))

            await session.commit()
    return added_count


async def get_teams_by_sport(sport_identifier: Union[str, int]) -> Dict[str, int]:
    """
    Возвращает команды, имеющие участников в указанном виде спорта.

    Args:
        sport_identifier: название вида спорта ('football', 'volleyball') или sport_id

    Returns:
        Словарь в формате {название_команды: team_id}
    """
    async with async_session() as session:
        # Определяем условие для фильтрации в зависимости от типа идентификатора
        if isinstance(sport_identifier, int):
            sport_condition = Sport.sport_id == sport_identifier
        else:
            sport_condition = Sport.name == sport_identifier

        # Основной запрос с явными join через отношения
        result = await session.execute(
            select(Team.name, Team.team_id)
            .join(Team.participants)  # Используем relationship
            .join(Participant.sports)  # Используем relationship
            .join(ParticipantSport.sport)  # Используем relationship
            .where(sport_condition)
            .distinct()
        )

        return {name: team_id for name, team_id in result.all()}


async def get_all_sports() -> Dict[str, int]:
    """
    Получает все виды спорта из таблицы Sport.

    Returns:
        Словарь в формате {название_спорта: sport_id}
    """
    async with async_session() as session:
        # Выполняем запрос на получение всех видов спорта
        result = await session.execute(
            select(Sport.name, Sport.sport_id)
        )

        # Преобразуем результат в словарь
        return {name: sport_id for name, sport_id in result.all()}

# Под удаление
# async def create_participant(participant_id: int,
#                              full_name: str,
#                              short_name: str,
#                              gender: str,
#                              age: int,
#                              football_team_id: int = None,
#                              plays_football: bool = False,
#                              plays_volleyball: bool = False) -> Participant:
#     """Создает одного участника с указанным ID"""
#     async with async_session() as session:
#         async with session.begin():
#             participant = Participant(
#                 participant_id=participant_id,
#                 full_name=full_name,
#                 short_name=short_name,
#                 gender=gender,
#                 age=age,
#                 football_team_id=football_team_id,
#                 plays_football=plays_football,
#                 plays_volleyball=plays_volleyball
#             )
#             session.add(participant)
#             await session.commit()
#             return participant
#
#
# async def bulk_create_participants(participants_data: List[Dict]) -> int:
#     """
#     Добавляет множество участников, автоматически создавая новые команды при необходимости.
#     Входные данные: список словарей, где football_team_id - название команды (строка)
#     Возвращает количество добавленных участников
#     """
#     added_count = 0
#     async with async_session() as session:
#         async with session.begin():
#             # Сначала собираем все уникальные названия команд
#             team_names = {p['football_team_id'] for p in participants_data
#                           if p.get('football_team_id') is not None}
#
#             # Получаем существующие команды
#             existing_teams = await session.execute(
#                 select(FootballTeam).where(FootballTeam.name.in_(team_names)))
#             existing_teams = {team.name: team.team_id for team in existing_teams.scalars()}
#
#             # Создаем отсутствующие команды
#             new_team_names = team_names - set(existing_teams.keys())
#             for team_name in new_team_names:
#                 team = FootballTeam(name=team_name)
#                 session.add(team)
#                 await session.flush()  # Получаем ID новой команды
#                 existing_teams[team.name] = team.team_id
#
#             # Теперь добавляем участников
#             for data in participants_data:
#                 if await session.get(Participant, data['participant_id']):
#                     continue  # Пропускаем существующих участников
#
#                 # Получаем ID команды (если указана)
#                 team_id = None
#                 if team_name := data.get('football_team_id'):
#                     team_id = existing_teams.get(team_name)
#
#                 participant = Participant(
#                     participant_id=data['participant_id'],
#                     full_name=data['full_name'],
#                     short_name=data['short_name'],
#                     gender=data['gender'],
#                     age=data['age'],
#                     football_team_id=team_id,
#                     plays_football=data.get('plays_football', False),
#                     plays_volleyball=data.get('plays_volleyball', False)
#                 )
#                 session.add(participant)
#                 added_count += 1
#
#             await session.commit()
#     return added_count
#
#
# async def get_teams_by_sport(sport: str) -> Dict[str, int]:
#     """
#     Возвращает команды, имеющие участников в указанном виде спорта.
#
#     Args:
#         sport: вид спорта ('football' или 'volleyball')
#
#     Returns:
#         Словарь в формате {название_команды: team_id}
#     """
#     async with async_session() as session:
#         # Определяем поле для фильтрации по виду спорта
#         sport_column = {
#             'football': Participant.plays_football,
#             'volleyball': Participant.plays_volleyball
#         }.get(sport.lower())
#
#         if not sport_column:
#             return {}
#
#         # Выполняем запрос с join таблиц
#         result = await session.execute(
#             select(
#                 FootballTeam.name,
#                 FootballTeam.team_id
#             )
#             .join(Participant)
#             .where(
#                 sport_column == True,
#                 Participant.football_team_id == FootballTeam.team_id
#             )
#             .distinct()
#         )
#
#         return {row.name: row.team_id for row in result.all()}


async def main():
    await drop_all_tables()
    await init_db()
    # print(await init_sports())
    participants = [
        {
            "participant_id": 1,
            "full_name": "Иванов Иван",
            "short_name": "Иванов И.",
            "gender": "M",
            "age": 25,
            "team_name": "Заря",
            "sports": ["football", "volleyball"]
        },
        # ... другие участники
    ]
    print(await bulk_create_participants(participants))
    team = await get_teams_by_sport("football")
    print(team)
    # Получение футбольных команд


# if __name__ == "__main__":
#     import asyncio
#
#     asyncio.run(main())