import logging

from sqlalchemy import select, case, func
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Participant, KettleResult, Judges, Team

logger = logging.getLogger(__name__)


async def save_kettle_results(session: AsyncSession, lifter_id: int, count: int, telegram_id: int, weight: int = None) -> None:
    """
    Сохраняет результаты гиревого спорта для участника в базу данных.

    :param session:
    :param lifter_id:
    :param count:
    :param telegram_id:
    :param weight:
    :return:
    """
    result = await session.execute(
        select(Participant.team_id).where(Participant.participant_id == lifter_id)
    )

    team_id = result.scalar_one_or_none()

    judge_result = await session.execute(
        select(Judges.judge_id).where(Judges.telegram_id == telegram_id)
    )

    judge_id = judge_result.scalar_one_or_none()

    new_result = KettleResult(
        lifter_id=lifter_id,
        team_id=team_id,
        lift_count=count,
        weight=weight,
        judge_id=judge_id,
    )

    session.add(new_result)
    await session.commit()


async def get_kettle_export_results(session: AsyncSession) -> list[dict]:
    """
    Получает результаты гиревого спорта из базы данных и сортирует их по полу, категории и количеству повторений.
    """
    gender_order = case(
        (Participant.gender == 'M', 0),
        else_=1
    )

    stmt = (
        select(
            Participant.full_name,
            Team.name.label("team_name"),
            KettleResult.lift_count,
            KettleResult.weight,
            Participant.age,
            Participant.gender
        )
        .join(Participant, KettleResult.lifter_id == Participant.participant_id)
        .join(Team, KettleResult.team_id == Team.team_id)
        .order_by(
            gender_order,  # сначала мужчины
            KettleResult.weight.asc().nullsfirst(),  # категория по возрастанию (если есть)
            KettleResult.lift_count.desc()  # по убыванию числа повторений
        )
    )

    result = await session.execute(stmt)

    return [
        {
            'full_name': row.full_name,
            'team_name': row.team_name,
            'lift_count': row.lift_count,
            'weight': row.weight,
            'age': row.age,
            'gender': row.gender
        }
        for row in result.fetchall()
    ]


async def get_judge_history(session: AsyncSession, telegram_id: int) -> list[dict]:
    """
    Функция для получения истории последних 10 результатов гиревого спорта для судьи.
    """
    judge_stmt = select(Judges.judge_id).where(Judges.telegram_id == telegram_id)
    result = await session.execute(judge_stmt)
    judge_id = result.scalar_one_or_none()

    # Основной запрос по KettleResult
    stmt = (
        select(
            Participant.short_name,
            KettleResult.weight,
            KettleResult.lift_count
        )
        .join(Participant, KettleResult.lifter_id == Participant.participant_id)
        .where(KettleResult.judge_id == judge_id)
        .order_by(KettleResult.timestamp.desc())
        .limit(10)
    )

    result = await session.execute(stmt)

    history_result = [
        {
            "short_name": row.short_name,
            "weight": row.weight,
            "lift_count": row.lift_count
        }
        for row in result.fetchall()
    ]

    return history_result


async def get_kettlebell_male_results(session: AsyncSession):
    stmt = (
        select(
            KettleResult.lifter_id,
            Participant.short_name,
            Participant.age,
            KettleResult.weight,
            func.max(KettleResult.lift_count).label("max_lift")
        )
        .join(Participant, Participant.participant_id == KettleResult.lifter_id)
        .where(Participant.gender == 'M')
        .group_by(KettleResult.lifter_id, Participant.short_name, Participant.age, KettleResult.weight)
    )

    result = await session.execute(stmt)
    rows = result.all()

    categorized_results = {
        "18-34": {
            "до 73 кг": [],
            "до 85 кг": [],
            "свыше 85 кг": [],
        },
        "35+": {
            "до 73 кг": [],
            "до 85 кг": [],
            "свыше 85 кг": [],
        }
    }

    for lifter_id, short_name, age, weight, max_lift in rows:
        if weight is None:
            continue

        age_group = "18-34" if age < 35 else "35+"

        if weight <= 73:
            weight_category = "до 73 кг"
        elif weight <= 85:
            weight_category = "до 85 кг"
        else:
            weight_category = "свыше 85 кг"

        categorized_results[age_group][weight_category].append({
            "id": lifter_id,
            "short_name": short_name,
            "lift_count": max_lift
        })

    # Сортируем по lift_count убыванию
    for age_group in categorized_results:
        for category in categorized_results[age_group]:
            categorized_results[age_group][category].sort(key=lambda x: x["lift_count"], reverse=True)

    return categorized_results


async def get_kettlebell_women_scores(session: AsyncSession):
    stmt = (
        select(
            KettleResult.lifter_id,
            Participant.short_name,
            KettleResult.lift_count,
            KettleResult.weight
        )
        .join(Participant, Participant.participant_id == KettleResult.lifter_id)
        .where(Participant.gender == 'F')
    )

    result = await session.execute(stmt)
    rows = result.all()

    score_map = {}

    for lifter_id, short_name, lift_count, weight in rows:
        if weight is None or weight == 0:
            continue  # Исключаем некорректные записи
        score = ((lift_count * 1.5) / weight) * 100
        # Если у участницы уже есть результат — берём лучший (максимальный)
        if lifter_id not in score_map or score > score_map[lifter_id]['scores']:
            score_map[lifter_id] = {
                'id': lifter_id,
                'short_name': short_name,
                'scores': round(score, 2)
            }

    # Сортировка по убыванию очков
    sorted_scores = sorted(score_map.values(), key=lambda x: x['scores'], reverse=True)

    return sorted_scores
