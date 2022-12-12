import db
import logging
from datetime import datetime
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext

API_TOKEN = '5649458393:AAHgc8zf-IIXjyu7RQaCy7NBwu4HpUXvpRQ'

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
logging.basicConfig(level=logging.INFO)

my_cursor = db.mydb.cursor()


class Form(StatesGroup):
    table = State()
    unit_workmates = State()
    unit_sickdoc = State()
    workmate = State()
    unit = State()
    sick_paper = State()


@dp.message_handler(commands="start")
async def start(message: types.Message):
    await message.answer("Good afternoon. I will help you with information about workmates in your office")


# Function that creates a message the contains a list of all the oders
def message_select_workmates(ans):
    text = ""
    for row in ans:
        id = row[0]
        name = row[1]
        surname = row[2]
        unit_id = row[3]
        age = row[4]
        text += str(id) + " | " + str(name) + " | " + str(surname) + "| " + str(unit_id) + "| " + str(age) + "\n"
    message = """Received 📖 Information about workmates:\nid | name | surname | unit_id | age \n\n""" + text
    return message


def message_select_units(ans):
    text = ""
    for row in ans:
        id = row[0]
        count_workmates = row[1]
        text += str(id) + " | " + str(count_workmates) + "\n"
    message = """Received 📖 Information about workmates:\nid | count workmates\n\n""" + text
    return message


def message_select_table(ans):
    text = ""
    for row in ans:
        id = row[0]
        name = row[1]
        surname = row[2]
        days_worked = row[3]
        sick = row[4]
        absenteeism = row[5]
        text += str(id) + " | " + str(name) + " | " + str(surname) + "| " + str(sick) + "| " + str(days_worked) + "| " \
                + str(absenteeism) + "\n"
    message = """Received 📖 Information about workmates:\nid | name | surname | sick days | days worked | absenteeism 
    \n\n""" + text
    return message

######
###### SELECT COMMANDS
######


@dp.message_handler(commands="workmates")
async def workmates(message: types.Message):
    sql = 'SELECT * FROM workmate'
    my_cursor.execute(sql)
    my_result = my_cursor.fetchall()
    if my_result:
        testo_messaggio = message_select_workmates(my_result)
        await message.answer(testo_messaggio)
    else:
        text = "No workmates found inside the database."
        await message.answer(text)


@dp.message_handler(commands="units")
async def units(message: types.Message):
    sql = 'SELECT * FROM unit'
    my_cursor.execute(sql)
    my_result = my_cursor.fetchall()
    if my_result:
        testo_messaggio = message_select_units(my_result)
        await message.answer(testo_messaggio)
    else:
        text = "No units found inside the database."
        await message.answer(text)


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

######
###### SELECT COMMANDS for units
######

@dp.message_handler(commands='unit_workmates')
async def units_id_workmates(message: types.Message):
    await Form.unit_workmates.set()
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
            if my_result:
                testo_messaggio = message_select_workmates(my_result)
                await call.message.answer(testo_messaggio)
            else:
                text = "No workmates found inside the database."
                await call.message.answer(text)
    await state.finish()


@dp.message_handler(commands='table')
async def units_id_table(message: types.Message):
    await Form.table.set()
    await message.reply("choose needed unit", reply_markup=keyboard_inline)


@dp.callback_query_handler(state=Form.table)
async def table(call: types.CallbackQuery, state: FSMContext):
    my_cursor.execute('SELECT count_work_days FROM mydb.month WHERE month_number = 1')
    count_work_days = my_cursor.fetchall()
    my_cursor.execute('SELECT month_name FROM mydb.month WHERE month_number = 1')
    month = my_cursor.fetchall()
    await call.message.answer(f'{str(call.data)}')
    await call.message.answer(f'month {str(month[0][0])}')
    await call.message.answer(f'count work days {str(count_work_days[0][0])}')
    for id in range(count_units):
        if call.data == buttons[id].callback_data:
            my_cursor.execute(f"""SELECT id_workmate, name, surname, (SELECT (SELECT count_work_days FROM mydb.month WHERE month_number=1) - count_days_disease
									FROM mydb.sick_document 
									WHERE mydb.workmate.id_workmate = mydb.sick_document.workmate_id_workmate) number_days_worked,
                                    (SELECT count_days_disease FROM mydb.sick_document 
									WHERE mydb.workmate.id_workmate = mydb.sick_document.workmate_id_workmate) sick_days,
                                    ( SELECT (SELECT count_work_days FROM mydb.month WHERE month_number=1) - number_days_worked - sick_days) absenteeism
                                    FROM mydb.workmate
                                    WHERE unit_id = 1""")
            data = my_cursor.fetchall()
            if data:
                testo_messaggio = message_select_table(data)
                await call.message.answer(testo_messaggio)
            else:
                text = "No workmates found inside the database."
                await call.message.answer(text)
    await state.finish()


@dp.message_handler(commands='unit_sickdoc')
async def units_id_sickdoc(message: types.Message):
    await Form.sick.set()
    await message.reply("choose needed unit", reply_markup=keyboard_inline)


@dp.callback_query_handler(state=Form.unit_sickdoc)
async def unit_info_sickdoc(call: types.CallbackQuery, state: FSMContext):
    for id in range(count_units):
        if call.data == buttons[id].callback_data:
            await call.message.answer("there will be answer soon")
    await state.finish()


######
###### INSERT COMMANDS
######

@dp.message_handler(commands='insert_workmate')
async def insert_workmate(message: types.Message):
    try:
        await Form.workmate.set()
        await message.answer("""INPUT\nsurname name unit_id age""")

    except Exception as e:
        print(e)
        await message.answer("Conversation Terminated✔")
        return


@dp.message_handler(state=Form.workmate)
async def insert_workmate(message: types.Message, state: FSMContext):

    data_workmate = message.values["text"].split(" ")
    try:
        surname = data_workmate[0].title()
        name = data_workmate[1].title()
        unit_id = int(data_workmate[2])
        age = int(data_workmate[3])
    except ValueError:
        await state.finish()
        await message.answer("sorry, you input wrong data type. please, try again")
        await Form.workmate.set()
        return

    # Create the tuple "params" with all the parameters inserted by the user
    workmate = (surname, name, unit_id, age)
    sql = "INSERT INTO workmate (id_workmate, surname, name, unit_id, age) VALUES (NULL, %s, %s, %s, %s);"
    # the initial NULL is for the AUTOINCREMENT id inside the table
    my_cursor.execute(sql, workmate)  # Execute the query
    db.mydb.commit()  # commit the changes
    await state.finish()

    if my_cursor.rowcount < 1:
        await message.answer("Something went wrong, please try again")
    else:
        await message.answer("Workmate correctly inserted")


@dp.message_handler(commands='insert_unit')
async def insert_unit(message: types.Message):
    try:
        await Form.unit.set()
        await message.answer("""INPUT\nunit title""")

    except Exception as e:
        print(e)
        await message.answer("Conversation Terminated✔")
        return


@dp.message_handler(state=Form.unit)
async def insert_unit(message: types.Message, state: FSMContext):

    unit_title = message.values["text"].strip().replace(" ", "_")

    sql = "INSERT INTO unit (id, count_workmates, title) VALUES (NULL, 0, %s);"
    # the initial NULL is for the AUTOINCREMENT id inside the table
    my_cursor.execute(sql, (unit_title, ))  # Execute the query
    db.mydb.commit()  # commit the changes
    await state.finish()

    if my_cursor.rowcount < 1:
        await message.answer("Something went wrong, please try again")
    else:
        await message.answer("Unit correctly inserted")


@dp.message_handler(commands='insert_sick_paper')
async def insert_workmate(message: types.Message):
    try:
        await Form.sick_paper.set()
        await message.answer("""INPUT\nbeginning_disease end_disease workmate's_id\n\n year-month-day\t2023-01-05""")

    except Exception as e:
        print(e)
        await message.answer("Conversation Terminated✔")
        return


@dp.message_handler(state=Form.sick_paper)
async def insert_workmate(message: types.Message, state: FSMContext):

    data_workmate = message.values["text"].split(" ")
    try:
        beginning_disease = data_workmate[0]
        end_disease = data_workmate[1]
        beginning = beginning_disease.split('-')
        year1 = int(beginning[0])
        month1 = int(beginning[1])
        day1 = int(beginning[2])
        data1 = datetime(year1, month1, day1)
        end = end_disease.split('-')
        year2 = int(end[0])
        month2 = int(end[1])
        day2 = int(end[2])
        data2 = datetime(year2, month2, day2)
        count_days = data2 - data1
        workmate_id = int(data_workmate[2])
    except ValueError:
        await state.finish()
        await message.answer("sorry, you input wrong data type. please, try again")
        await Form.workmate.set()
        return

    # Create the tuple "params" with all the parameters inserted by the user
    workmate = (beginning_disease, end_disease, count_days.days, workmate_id)
    # CHECK DATA TYPE
    print(workmate)
    sql = "INSERT INTO sick_document (id, beginning_disease, end_disease, count_days_disease, workmate_id_workmate) " \
          "VALUES (NULL, %s, %s, %s, %s);"
    # the initial NULL is for the AUTOINCREMENT id inside the table
    my_cursor.execute(sql, workmate)  # Execute the query
    db.mydb.commit()  # commit the changes
    await state.finish()

    if my_cursor.rowcount < 1:
        await message.answer("Something went wrong, please try again")
    else:
        await message.answer("Sick paper correctly inserted")

if __name__ == '__main__':
    try:
        print("Initializing Database...")
        # my_cursor = db.mydb.cursor()
        print("Connected to the database")

        # Command that creates the "oders" table
        sql_command = """CREATE DATABASE IF NOT EXISTS `mydb` DEFAULT CHARACTER SET utf8 ;"""
        my_cursor.execute(sql_command)
        sql_command = """CREATE TABLE IF NOT EXISTS `mydb`.`unit` (
                        `id` INT NOT NULL AUTO_INCREMENT,
                        `count_workmates` INT NULL,
                        PRIMARY KEY (`id`),
                        UNIQUE INDEX `id_UNIQUE` (`id` ASC) VISIBLE);"""
        my_cursor.execute(sql_command)
        sql_command = """CREATE TABLE IF NOT EXISTS `mydb`.`workmate` (
                        `id_workmate` INT NOT NULL AUTO_INCREMENT,
                        `surname` VARCHAR(45) NOT NULL,
                        `name` VARCHAR(45) NOT NULL,
                        `unit_id` INT NOT NULL,
                        PRIMARY KEY (`id_workmate`, `unit_id`),
                        UNIQUE INDEX `id_workmate_UNIQUE` (`id_workmate` ASC) VISIBLE,
                        INDEX `fk_workmate_unit_idx` (`unit_id` ASC) VISIBLE,
                        CONSTRAINT `fk_workmate_unit`
                        FOREIGN KEY (`unit_id`)
                        REFERENCES `mydb`.`unit` (`id`)
                        ON UPDATE CASCADE);"""
        my_cursor.execute(sql_command)
        sql_command = """CREATE TABLE IF NOT EXISTS `mydb`.`month` (
                         `month_name` VARCHAR(45) NOT NULL,
                         `month_number` INT NOT NULL,
                         `count_days` INT NOT NULL,
                         `count_work_days` INT NOT NULL,
                         UNIQUE INDEX `month_name_UNIQUE` (`month_name` ASC) VISIBLE,
                         PRIMARY KEY (`month_number`));"""
        my_cursor.execute(sql_command)
        sql_command = """CREATE TABLE IF NOT EXISTS `mydb`.`table` (
                         `id` INT NOT NULL AUTO_INCREMENT,
                          `unit_id` INT NOT NULL,
                          `month_month_number` INT NOT NULL,
                          PRIMARY KEY (`id`, `month_month_number`, `unit_id`),
                          UNIQUE INDEX `id_UNIQUE` (`id` ASC) VISIBLE,
                          INDEX `fk_table_unit1_idx` (`unit_id` ASC) VISIBLE,
                          INDEX `fk_table_month1_idx` (`month_month_number` ASC) VISIBLE,
                          CONSTRAINT `fk_table_unit1`
                            FOREIGN KEY (`unit_id`)
                            REFERENCES `mydb`.`unit` (`id`)
                            ON UPDATE CASCADE,
                          CONSTRAINT `fk_table_month1`
                            FOREIGN KEY (`month_month_number`)
                            REFERENCES `mydb`.`month` (`month_number`)
                            ON UPDATE CASCADE);"""
        my_cursor.execute(sql_command)
        sql_command = """CREATE TABLE IF NOT EXISTS `mydb`.`sick_document` (
                          `id` INT NOT NULL AUTO_INCREMENT,
                          `beginning_disease` DATE NOT NULL,
                          `end_disease` DATE NOT NULL,
                          `count_days_disease` INT NOT NULL,
                          `workmate_id_workmate` INT NOT NULL,
                          PRIMARY KEY (`id`, `workmate_id_workmate`),
                          UNIQUE INDEX `id_UNIQUE` (`id` ASC) VISIBLE,
                          INDEX `fk_sick_document_workmate1_idx` (`workmate_id_workmate` ASC) VISIBLE,
                          CONSTRAINT `fk_sick_document_workmate1`
                            FOREIGN KEY (`workmate_id_workmate`)
                            REFERENCES `mydb`.`workmate` (`id_workmate`)
                            ON UPDATE CASCADE);"""
        my_cursor.execute(sql_command)
        print("All tables are ready")

        print("Bot Started")
        executor.start_polling(dp, skip_updates=True)

    except Exception as error:
        print('Cause: {}'.format(error))
