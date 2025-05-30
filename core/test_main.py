import asyncio
from pprint import pprint
import time

from sqlalchemy import text

from api_requests.final_table_getters import calculate_tug_of_war_places, DartsPlaceCalculator, \
    prepare_kettlebell_women_api_payload, TableTennisPlaceCalculator
from api_requests.api_base_config import api
from database.kettle_requests import get_kettlebell_male_results, get_kettlebell_women_scores
from database.models import async_session
from api_requests.data_preparation_fonc import build_football_tournament_data, build_volleyball_tournament_data, \
    RelayResultBuilder, RunningResultBuilder, FootballResultBuilder, VolleyballResultBuilder, DartsResultBuilder, \
    KettlebellResultBuilder, TugResultBuilder, TableTennisResultBuilder
from database.pong_requests import get_table_tennis_participants_by_gender
from database.service_requests import init_db, drop_all_tables


async def main():
    await drop_all_tables()
    await init_db()
    # #
    # # Парсим данные из гугл таблиц
    # participants_data = get_filtered_participants_data('123')
    # # Добавляем нескольких участников
    # added_participants = await bulk_create_participants(participants_data)
    # print(f"Добавлено участников: {added_participants}")

    async with async_session() as session:
        await session.execute(text("insert into judges values (1, 28191584)"))
        await session.commit()

        start = time.monotonic()
        # builder = TableTennisResultBuilder(session)
        # pong_result = await builder.build()
        # pprint(pong_result)
        # ids = await get_table_tennis_participants_by_gender(session, 'F')
        # api.send_results(pong_result)
        # print(ids)
        finish = time.monotonic()
        print(f'Время выполнения запроса: {finish - start} ')
    await session.close()


if __name__ == "__main__":
    asyncio.run(main())
