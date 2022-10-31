from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from config import TOKEN_API, HELP_COMMAND
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher.storage import FSMContext
from menu import *


from pyzbar.pyzbar import decode
import os
from os import listdir
from os.path import isfile, join

from io import BytesIO
from PIL import Image

import db
class ClientStatesGroup(StatesGroup):
    login = State()
    phone = State()
class ClientUpdateStates(StatesGroup):
    updateName = State()
    updatePhone = State()

class ClientScannerStates(StatesGroup):
    image = State()
    delete_by_image = State()

storage = MemoryStorage()
bot = Bot(TOKEN_API)
dp = Dispatcher(bot,storage=storage)

kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

async def get_actual_menu(id):
    user = await db.GetUserById(id)
    if (user[2] == False):
        return get_user_menu()
    return get_admin_menu()

@dp.message_handler(commands=['cancel'], state='*')
async def cmd_start(message: types.Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        return
    await message.reply('Отменил',
                        reply_markup=get_keyboard())
    await state.finish()
@dp.message_handler(Text(equals='Начать работу!', ignore_case=True), state=None)
async def start_work(message: types.Message) -> None:
    await  message.answer(text="Начнём. Используй /login для авторизации/регистрации", reply_markup=get_keyboard())
    await message.delete()
@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await message.answer(text=f"Привет, котик! Напиши /help, чтобы увидеть функционал", reply_markup=get_keyboard())
    await  db.GetAllUsers()




@dp.message_handler(commands=['help'])
async def help_command(message: types.Message):
    await message.reply(text=HELP_COMMAND)




@dp.message_handler(commands=['login'])
async def login_command(message: types.Message):
    user = await db.GetUserById(message.from_user.id)

    if(user==None):
        await ClientStatesGroup.login.set()
        return await message.answer(text="Введи ФИО, дружок!", reply_markup=get_cancel())
    else:
        if (user[2] == False):
            await message.answer(text="Вы авторизированы", reply_markup=get_user_menu())
        else:

            await message.answer(text="Вы авторизированы, господин", reply_markup=get_admin_menu())


@dp.message_handler(state=ClientStatesGroup.login)
async def load_login(message: types.Message,state:FSMContext):
    async with state.proxy() as data:
        data['login']=message.text
    await ClientStatesGroup.next()
    await message.reply('Отправьте номер телефона')

@dp.message_handler( state=ClientStatesGroup.phone)
async def load_phone(message: types.Message,state:FSMContext):
    async with state.proxy() as data:
        data['phone']=message.text
    async with state.proxy() as data:
        await db.InsertUser(f"{message.from_user.id}",data['login'],data['phone'])
    await message.reply('Готово!', reply_markup=get_user_menu())
    await state.finish()

@dp.message_handler(Text(equals='Список костюмов дома', ignore_case=False), state=None)
async def load_basket(message: types.Message):
    print(message.from_user.id)
    result = await db.GetUserCostumes(message.from_user.id)

    await message.answer(text=result, reply_markup=ReplyKeyboardMarkup(
        resize_keyboard=True
    ).add(KeyboardButton('Назад в меню')))

@dp.message_handler(Text(equals='Назад в меню', ignore_case=False), state=None)
async def load_menu(message: types.Message):
    await message.delete()
    actual_menu = await get_actual_menu(message.from_user.id)
    await message.answer(text="Возвращаемся...",reply_markup=actual_menu)

@dp.message_handler(Text(equals='Список должников', ignore_case=False), state=None)
async def get_basket(message: types.Message):
    result = await db.GetAllUsersWithCostume()
    actual_menu = await get_actual_menu(message.from_user.id)
    await message.answer(text=result, reply_markup=actual_menu)

@dp.message_handler(Text(equals='Изменить личные данные', ignore_case=False), state=None)
async def load_user_menu(message: types.Message):
    await message.answer(text="Личный кабинет:", reply_markup=get_user_data())

@dp.message_handler(Text(equals='Сканировать костюм', ignore_case=False), state=None)
async def get_qr_photo(message: types.Message):
    await ClientScannerStates.image.set()
    await message.answer(text="Отправь фото QR-кода на костюме:")

@dp.message_handler(lambda message: not message.photo, state=ClientScannerStates.image)
async def check_photo(message: types.Message):
    return await message.reply('Это не фотография! Отправьте QR')

import cv2

import os


@dp.message_handler(lambda message: message.photo, content_types=['photo'], state=ClientScannerStates.image)
async def load_photo(message: types.Message, state: FSMContext):
    ikb = InlineKeyboardMarkup(row_width=2)
    ib1 = InlineKeyboardButton(text='❤️',
                               callback_data="like")
    ib2 = InlineKeyboardButton(text='👎',
                               callback_data="dislike")
    ikb.add(ib1, ib2)
    await message.photo[-1].download(
        destination=f"tmpQR\\{message.photo[-1].file_unique_id}.png"
    )
    async with state.proxy() as data:
        try:
            image = cv2.imread(
                f"tmpQR\\{message.photo[-1].file_unique_id}.png")
            print(f"tmpQR\\{message.photo[-1].file_unique_id}.png")
            qrCodeDetector = cv2.QRCodeDetector()
            decodedText, points, _ = qrCodeDetector.detectAndDecode(image)

            await message.answer(text=f"{decodedText}?", reply_markup=ikb)
        except:
            await message.answer(text="Чот не съел :(")
        if os.path.isfile(f'tmpQR\\{message.photo[-1].file_unique_id}.png'):
            os.remove(f'tmpQR\\{message.photo[-1].file_unique_id}.png')

    await state.finish()

@dp.message_handler(Text(equals='Сканнер удаления', ignore_case=False), state=None)
async def get_qr_photo(message: types.Message):
    await ClientScannerStates.delete_by_image.set()
    await message.answer(text="Отправь фото QR-кода на костюме:")
@dp.message_handler(lambda message: not message.photo, state=ClientScannerStates.delete_by_image)
async def check_photo(message: types.Message):
    return await message.reply('Это не фотография! Отправьте QR')

@dp.message_handler(lambda message: message.photo, content_types=['photo'], state=ClientScannerStates.delete_by_image)
async def load_photo(message: types.Message, state: FSMContext):
    ikb = InlineKeyboardMarkup(row_width=2)
    ib1 = InlineKeyboardButton(text='❤️',
                               callback_data="likeDel")
    ib2 = InlineKeyboardButton(text='👎',
                               callback_data="dislike")
    ikb.add(ib1, ib2)
    await message.photo[-1].download(
        destination=f"tmpQR\\{message.photo[-1].file_unique_id}.png"
    )
    async with state.proxy() as data:
        try:
            image = cv2.imread(
                f"tmpQR\\{message.photo[-1].file_unique_id}.png")
            print(f"tmpQR\\{message.photo[-1].file_unique_id}.png")
            qrCodeDetector = cv2.QRCodeDetector()
            decodedText, points, _ = qrCodeDetector.detectAndDecode(image)

            await message.answer(text=f"{decodedText}?", reply_markup=ikb)
        except:
            await message.answer(text="Чот не съел :(")
        if os.path.isfile(f'tmpQR\\{message.photo[-1].file_unique_id}.png'):
            os.remove(f'tmpQR\\{message.photo[-1].file_unique_id}.png')

    await state.finish()

@dp.callback_query_handler()
async def vote_callback(callback: types.CallbackQuery):



    if callback.data == 'like':
        costume_id = callback.message.text[:-1]
        await callback.answer(text=f'Костюм добавлен в корзину')
        await db.InsertScannedCostume(callback.from_user.id,costume_id)
    elif callback.data=='likeDel':
        costume_id = callback.message.text[:-1]
        await callback.answer(text=f'Удалён из корзины')
        await db.DeleteFromBasket(costume_id)
    await callback.answer('Ошибочка со сканом!')


@dp.message_handler(Text(equals='Изменить ФИО', ignore_case=False), state=None)
async def update_fullname(message: types.Message):
    await ClientUpdateStates.updateName.set()
    await message.answer(text="Введите новые ФИО:", reply_markup=get_cancel())
@dp.message_handler( state= ClientUpdateStates.updateName)
async def updatingName(message: types.Message,state:FSMContext):
    await db.UpdateUserName(message.from_user.id,message.text)
    await state.finish()
    actual_menu = await get_actual_menu(message.from_user.id)
    await message.reply('Готово!', reply_markup=actual_menu)

@dp.message_handler(Text(equals='Изменить номер', ignore_case=False), state=None)
async def update_fullname(message: types.Message):
    await ClientUpdateStates.updatePhone.set()
    await message.answer(text="Введите новый номер:", reply_markup=get_cancel())
@dp.message_handler(state= ClientUpdateStates.updatePhone)
async def updatingPhone(message: types.Message,state:FSMContext):
    await db.UpdateUserPhone(message.from_user.id,message.text)
    await state.finish()
    actual_menu = await get_actual_menu(message.from_user.id)
    await message.reply('Готово!', reply_markup=actual_menu)



if __name__ == '__main__':
    print("start")
    executor.start_polling(dp, skip_updates=True)
