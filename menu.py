from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove




def get_keyboard() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton('Начать работу!'))

    return kb
def get_user_menu() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton('Изменить личные данные'))
    kb.add(KeyboardButton('Сканировать костюм'))
    kb.add(KeyboardButton('Список костюмов дома'))
    return kb
def get_admin_menu() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton('Изменить личные данные'))
    kb.add(KeyboardButton('Сканировать костюм'))
    kb.add(KeyboardButton('Список костюмов дома'))
    kb.add(KeyboardButton('Список должников'))
    kb.insert(KeyboardButton('Сканнер удаления'))
    return kb

def get_cancel() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton('/cancel'))

def get_user_data() ->ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton('Изменить ФИО'))
    kb.add(KeyboardButton('Изменить номер'))
    return kb