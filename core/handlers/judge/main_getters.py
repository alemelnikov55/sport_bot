from aiogram_dialog import DialogManager

from database.service_requests import get_all_sports


async def get_sports(dialog_manager: DialogManager, **kwargs):
    """Получение списка видов спорта"""
    sports = await get_all_sports()
    formated_sports = [{'name': name, 'id': id_} for name, id_ in sports.items()]

    dialog_manager.dialog_data['sports'] = formated_sports

    return {'sports': formated_sports}
