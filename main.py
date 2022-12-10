import db
import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext

API_TOKEN = '5649458393:AAHgc8zf-IIXjyu7RQaCy7NBwu4HpUXvpRQ'

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage = storage)
logging.basicConfig(level=logging.INFO)

my_cursor = db.mydb.cursor()


# States
class Form(StatesGroup):
    table = State()
    unit_workmates = State()
    absenteeism = State()


@dp.message_handler(commands="start")
async def start(message: types.Message):
    await message.answer("Good afternoon. I will help you with information about workmates in your office")


@dp.message_handler(commands="workmates")
async def workmates(message: types.Message):
    sql = 'SELECT * FROM workmate'
    my_cursor.execute(sql)
    my_result = my_cursor.fetchall()
    for row in my_result:
        await message.answer(row)


@dp.message_handler(commands="units")
async def units(message: types.Message):
    sql = 'SELECT * FROM unit'
    my_cursor.execute(sql)
    my_result = my_cursor.fetchall()
    for row in my_result:
        await message.answer(row)

# create inline keyboard with dynamic count of units for show workmates
my_cursor.execute('SELECT * FROM unit')
units_data = my_cursor.fetchall()
count_units = len(units_data)

buttons = []
keyboard_inline = InlineKeyboardMarkup()
for unit_id in range(count_units):
    number = unit_id + 1
    buttons.append(InlineKeyboardButton(text=f'unit {number}', callback_data=f'unit_{number}'))
    keyboard_inline.add(InlineKeyboardButton(text=f'unit {number}', callback_data=f'unit_{number}'))


@dp.message_handler(commands='unit_workmates')
async def units_id(message: types.Message):
    await Form.unit_workmates.set()
    await message.reply("choose needed unit", reply_markup=keyboard_inline)


@dp.message_handler(commands='table')
async def units_id(message: types.Message):
    await Form.table.set()
    await message.reply("choose needed unit", reply_markup=keyboard_inline)


@dp.message_handler(commands='absenteeism')
async def unit_info_absenteeism(message: types.Message):
    await Form.absenteeism.set()
    await message.reply("choose needed unit", reply_markup=keyboard_inline)


@dp.callback_query_handler(state=Form.unit_workmates)
async def unit_workmates(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer(f"workmates of unit {str(call.data)}")
    for id in range(count_units):
        if call.data == buttons[id].callback_data:
            needed_unit_id = id + 1
            sql = f'SELECT * FROM workmate WHERE unit_id = {needed_unit_id}'
            my_cursor.execute(sql)
            my_result = my_cursor.fetchall()
            for row in my_result:
                await call.message.answer(row)
    await state.finish()


@dp.callback_query_handler(state=Form.table)
async def table(call: types.CallbackQuery, state: FSMContext):
    my_cursor.execute('SELECT count_work_days FROM mydb.month WHERE month_number = 1')
    count_work_days = my_cursor.fetchall()
    my_cursor.execute('SELECT month_name FROM mydb.month WHERE month_number = 1')
    month = my_cursor.fetchall()
    await call.message.answer(f'{str(call.data)}')
    await call.message.answer(f'month {month}')
    await call.message.answer(f'count work days {count_work_days}')
    for id in range(count_units):
        if call.data == buttons[id].callback_data:
            my_cursor.execute(f"""SELECT id_workmate, name, surname, (SELECT count_days_disease FROM mydb.sick_document
            WHERE mydb.workmate.id_workmate = mydb.sick_document.workmate_id_workmate) sick_days,
            (SELECT (SELECT count_work_days FROM mydb.month WHERE month_number=1) - count_days_disease FROM mydb.sick_document 
			WHERE mydb.workmate.id_workmate = mydb.sick_document.workmate_id_workmate) number_days_worked
            FROM mydb.workmate
            WHERE unit_id=1""")
            data = my_cursor.fetchall()
            # print(data)
            for row in data:
                await call.message.answer(row)
    await state.finish()


@dp.callback_query_handler(state=Form.absenteeism)
async def unit_info_absenteeism(call: types.CallbackQuery, state: FSMContext):
    for id in range(count_units):
        if call.data == buttons[id].callback_data:
            await call.message.answer("there will be answer soon")
    await state.finish()


executor.start_polling(dp, skip_updates=True)


# sql = 'UPDATE workmate SET age = 20 WHERE id_workmate<13'
# my_cursor.execute(sql)
# mydb.commit()
# sql = 'SELECT * FROM workmate'
# my_cursor.execute(sql)
# result = my_cursor.fetchall()
# for row in result:
#     print(row)

# insert MONTH
# sqlFormula = "INSERT INTO month (month_name, month_number, count_days, count_work_days) VALUES (%s, %s, %s, %s);"
# month = ('May', 5, 30, 20)
# my_cursor.execute(sqlFormula, month)
# mydb.commit()

# (how to insert DEFAULT value?
# sqlFormula = "INSERT INTO month (month_name, month_number, count_days, count_work_days) VALUES (%s, %s, %s, %s);"
# workmates = [(), (), (), ...]
# my_cursor.executemany(sqlFormula, workmates)
# mydb.commit()

# show all tables in db
# my_cursor.execute('SHOW TABLES')
# for db in my_cursor:
#     print(db)
