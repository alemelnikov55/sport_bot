from typing import List, Dict, Union

from sqlalchemy import text, select, exists
from sqlalchemy.ext.asyncio import AsyncSession

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
                team_id = team_name_to_id.get(data['team_id'])
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


async def get_teams_by_sport(sport_identifier: Union[int, str], session: AsyncSession) -> Dict[str, int]:
    """
    Получает список команд, участвующих в данном виде спорта.

    :param sport_identifier: ID спорта (int) или название спорта (str)
    :param session: AsyncSession для выполнения запроса
    :return: Словарь {"team_name": team_id}
    """
    # Получаем ID спорта, если передано название
    if isinstance(sport_identifier, str):
        sport_query = await session.execute(
            select(Sport.sport_id).where(Sport.name == sport_identifier)
        )
        sport_id = sport_query.scalar()
    else:
        sport_id = sport_identifier

    if not sport_id:
        return {}

    # Получаем все команды, участвующие в данном виде спорта
    query = await session.execute(
        select(Team.team_id, Team.name)
        .join(Participant, Team.team_id == Participant.team_id)
        .join(ParticipantSport, Participant.participant_id == ParticipantSport.participant_id)
        .filter(ParticipantSport.sport_id == sport_id)
        .group_by(Team.team_id, Team.name)  # Группировка вместо distinct()
    )

    teams = {team_name: team_id for team_id, team_name in query.all()}

    return teams


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


async def get_team_participants_by_sport(
        team_identifier: Union[int, str],
        sport_identifier: Union[int, str],
        session: AsyncSession
) -> Dict[str, int]:
    """
    Получает список спортсменов из указанной команды, участвующих в данном виде спорта.

    :param team_identifier: ID команды (int) или название команды (str)
    :param sport_identifier: ID спорта (int) или название спорта (str)
    :param session: AsyncSession для выполнения запроса
    :return: Словарь {"full_name": participant_id}
    """
    async with session.begin():
        # Получаем ID команды, если передано название
        if isinstance(team_identifier, str):
            team_query = await session.execute(
                select(Team.team_id).where(Team.name == team_identifier)
            )
            team_id = team_query.scalar()
        else:
            team_id = team_identifier

        if not team_id:
            return {}

        # Получаем ID спорта, если передано название
        if isinstance(sport_identifier, str):
            sport_query = await session.execute(
                select(Sport.sport_id).where(Sport.name == sport_identifier)
            )
            sport_id = sport_query.scalar()
        else:
            sport_id = sport_identifier

        if not sport_id:
            return {}
        print(f'in query{team_id}, {sport_id}')
        # Запрос на получение спортсменов
        query = await session.execute(
            select(Participant.participant_id, Participant.full_name)
            .join(ParticipantSport, Participant.participant_id == ParticipantSport.participant_id)
            .filter(Participant.team_id == team_id, ParticipantSport.sport_id == sport_id)
        )

        participants = {full_name: participant_id for participant_id, full_name in query.all()}

    return participants
