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
    # await drop_all_tables()
    # await init_db()
    # #
    # # Парсим данные из гугл таблиц
    # participants_data = get_filtered_participants_data('123')
    # # Добавляем нескольких участников
    # added_participants = await bulk_create_participants(participants_data)
    # print(f"Добавлено участников: {added_participants}")

    async with async_session() as session:
        # await session.execute(text("insert into judges values (1, 28191584)"))
        # await session.commit()

        start = time.monotonic()
        builder = TableTennisResultBuilder(session)
        pong_result = await builder.build()
        pprint(pong_result)
        # ids = await get_table_tennis_participants_by_gender(session, 'F')
        api.send_results(pong_result)
        # print(ids)
        finish = time.monotonic()
        print(f'Время выполнения запроса: {finish - start} ')
    await session.close()


if __name__ == "__main__":
    asyncio.run(main())


{'bot': <aiogram.client.bot.Bot object at 0x7f87a5d815d0>, 'event_context': EventContext(chat=Chat(id=28191584, type='private', title=None, username='Alemelnikov', first_name='Alexey', last_name='Melnikov', is_forum=None, accent_color_id=None, active_usernames=None, available_reactions=None, background_custom_emoji_id=None, bio=None, birthdate=None, business_intro=None, business_location=None, business_opening_hours=None, can_set_sticker_set=None, custom_emoji_sticker_set_name=None, description=None, emoji_status_custom_emoji_id=None, emoji_status_expiration_date=None, has_aggressive_anti_spam_enabled=None, has_hidden_members=None, has_private_forwards=None, has_protected_content=None, has_restricted_voice_and_video_messages=None, has_visible_history=None, invite_link=None, join_by_request=None, join_to_send_messages=None, linked_chat_id=None, location=None, message_auto_delete_time=None, permissions=None, personal_chat=None, photo=None, pinned_message=None, profile_accent_color_id=None, profile_background_custom_emoji_id=None, slow_mode_delay=None, sticker_set_name=None, unrestrict_boost_count=None), user=User(id=28191584, is_bot=False, first_name='Alexey', last_name='Melnikov', username='Alemelnikov', language_code='en', is_premium=None, added_to_attachment_menu=None, can_join_groups=None, can_read_all_group_messages=None, supports_inline_queries=None, can_connect_to_business=None, has_main_web_app=None), thread_id=None, business_connection_id=None), 'event_from_user': User(id=28191584, is_bot=False, first_name='Alexey', last_name='Melnikov', username='Alemelnikov', language_code='en', is_premium=None, added_to_attachment_menu=None, can_join_groups=None, can_read_all_group_messages=None, supports_inline_queries=None, can_connect_to_business=None, has_main_web_app=None), 'event_chat': Chat(id=28191584, type='private', title=None, username='Alemelnikov', first_name='Alexey', last_name='Melnikov', is_forum=None, accent_color_id=None, active_usernames=None, available_reactions=None, background_custom_emoji_id=None, bio=None, birthdate=None, business_intro=None, business_location=None, business_opening_hours=None, can_set_sticker_set=None, custom_emoji_sticker_set_name=None, description=None, emoji_status_custom_emoji_id=None, emoji_status_expiration_date=None, has_aggressive_anti_spam_enabled=None, has_hidden_members=None, has_private_forwards=None, has_protected_content=None, has_restricted_voice_and_video_messages=None, has_visible_history=None, invite_link=None, join_by_request=None, join_to_send_messages=None, linked_chat_id=None, location=None, message_auto_delete_time=None, permissions=None, personal_chat=None, photo=None, pinned_message=None, profile_accent_color_id=None, profile_background_custom_emoji_id=None, slow_mode_delay=None, sticker_set_name=None, unrestrict_boost_count=None), 'fsm_storage': <aiogram.fsm.storage.redis.RedisStorage object at 0x7f8791060250>, 'state': <aiogram.fsm.context.FSMContext object at 0x7f87910bf2e0>, 'raw_state': 'UserStates:help_status', 'handler': HandlerObject(callback=<function handle_user_help_message at 0x7f87919f9240>, awaitable=True, params={'message', 'state'}, varkw=False, filters=[FilterObject(callback=<State 'UserStates:help_status'>, awaitable=False, params={'event', 'raw_state', 'self'}, varkw=False, magic=None), FilterObject(callback=<bound method MagicFilter.resolve of <aiogram.utils.magic_filter.MagicFilter object at 0x7f879152fb00>>, awaitable=False, params={'value', 'self'}, varkw=False, magic=<aiogram.utils.magic_filter.MagicFilter object at 0x7f879152fb00>)], flags={}), 'event_update': Update(update_id=907251724, message=Message(message_id=14032, date=datetime.datetime(2025, 5, 27, 14, 29, 22, tzinfo=TzInfo(UTC)), chat=Chat(id=28191584, type='private', title=None, username='Alemelnikov', first_name='Alexey', last_name='Melnikov', is_forum=None, accent_color_id=None, active_usernames=None, available_reactions=None, background_custom_emoji_id=None, bio=None, birthdate=None, business_intro=None, business_location=None, business_opening_hours=None, can_set_sticker_set=None, custom_emoji_sticker_set_name=None, description=None, emoji_status_custom_emoji_id=None, emoji_status_expiration_date=None, has_aggressive_anti_spam_enabled=None, has_hidden_members=None, has_private_forwards=None, has_protected_content=None, has_restricted_voice_and_video_messages=None, has_visible_history=None, invite_link=None, join_by_request=None, join_to_send_messages=None, linked_chat_id=None, location=None, message_auto_delete_time=None, permissions=None, personal_chat=None, photo=None, pinned_message=None, profile_accent_color_id=None, profile_background_custom_emoji_id=None, slow_mode_delay=None, sticker_set_name=None, unrestrict_boost_count=None), message_thread_id=None, from_user=User(id=28191584, is_bot=False, first_name='Alexey', last_name='Melnikov', username='Alemelnikov', language_code='en', is_premium=None, added_to_attachment_menu=None, can_join_groups=None, can_read_all_group_messages=None, supports_inline_queries=None, can_connect_to_business=None, has_main_web_app=None), sender_chat=None, sender_boost_count=None, sender_business_bot=None, business_connection_id=None, forward_origin=None, is_topic_message=None, is_automatic_forward=None, reply_to_message=None, external_reply=None, quote=None, reply_to_story=None, via_bot=None, edit_date=None, has_protected_content=None, is_from_offline=None, media_group_id=None, author_signature=None, text='sdadf', entities=None, link_preview_options=None, effect_id=None, animation=None, audio=None, document=None, paid_media=None, photo=None, sticker=None, story=None, video=None, video_note=None, voice=None, caption=None, caption_entities=None, show_caption_above_media=None, has_media_spoiler=None, contact=None, dice=None, game=None, poll=None, venue=None, location=None, new_chat_members=None, left_chat_member=None, new_chat_title=None, new_chat_photo=None, delete_chat_photo=None, group_chat_created=None, supergroup_chat_created=None, channel_chat_created=None, message_auto_delete_timer_changed=None, migrate_to_chat_id=None, migrate_from_chat_id=None, pinned_message=None, invoice=None, successful_payment=None, refunded_payment=None, users_shared=None, chat_shared=None, connected_website=None, write_access_allowed=None, passport_data=None, proximity_alert_triggered=None, boost_added=None, chat_background_set=None, forum_topic_created=None, forum_topic_edited=None, forum_topic_closed=None, forum_topic_reopened=None, general_forum_topic_hidden=None, general_forum_topic_unhidden=None, giveaway_created=None, giveaway=None, giveaway_winners=None, giveaway_completed=None, video_chat_scheduled=None, video_chat_started=None, video_chat_ended=None, video_chat_participants_invited=None, web_app_data=None, reply_markup=None, forward_date=None, forward_from=None, forward_from_chat=None, forward_from_message_id=None, forward_sender_name=None, forward_signature=None, user_shared=None), edited_message=None, channel_post=None, edited_channel_post=None, business_connection=None, business_message=None, edited_business_message=None, deleted_business_messages=None, message_reaction=None, message_reaction_count=None, inline_query=None, chosen_inline_result=None, callback_query=None, shipping_query=None, pre_checkout_query=None, purchased_paid_media=None, poll=None, poll_answer=None, my_chat_member=None, chat_member=None, chat_join_request=None, chat_boost=None, removed_chat_boost=None), 'event_router': <Router '0x7f87a12dc6d0'>}
<aiogram.fsm.context.FSMContext object at 0x7f87910bf2e0>
