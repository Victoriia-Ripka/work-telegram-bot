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
currentMonth = datetime.now().month


class Form(StatesGroup):
    id_workmate_type = State()
    workmate_id = State()
    workmate_surname = State()
    table = State()
    unit_workmates = State()
    unit_sickdoc = State()
    workmate = State()
    unit = State()
    sick_paper = State()
    update_workmate = State()
    update_unit = State()
    update_sick_paper = State()
    delete_workmate = State()
    delete_unit = State()
    delete_sick_paper = State()


async def set_commands():
    await dp.bot.set_my_commands(commands=[
        types.BotCommand("start", "bot launch"),
        types.BotCommand("help", "list of commands"),
        types.BotCommand("workmates", "list of workmates"),
        types.BotCommand("units", "list of units"),
        types.BotCommand("workmate", "needed workmate"),
        types.BotCommand("unit_workmates", "list of workmates in the unit"),
        types.BotCommand("table", "table of unit"),
        types.BotCommand("unit_sickdoc", "all sickdoc of unit"),
        types.BotCommand("insert_workmate", ""),
        types.BotCommand("insert_unit", ""),
        types.BotCommand("insert_sick_paper", ""),
        types.BotCommand("update_workmate", ""),
        types.BotCommand("update_unit", ""),
        types.BotCommand("update_sick_paper", ""),
        types.BotCommand("delete_workmate", ""),
        types.BotCommand("delete_unit", ""),
        types.BotCommand("delete_sick_paper", ""),
    ])


@dp.message_handler(commands="start")
async def start(message: types.Message):
    await message.answer(f"Good afternoon. I will help you with information about workmates in your office.\n" \
                         "Use /help to see all available commands.")


@dp.message_handler(commands="help")
async def help(message: types.Message):
    text = f'I can help you manage database of workmates in your office.\n\n' \
           '/start - bot launch, greetings\n/help - a list of all available commands and their ' \
           'purpose \n\nORDINARY SELECT:\n/workmates – a list of all workmates in the office\n' \
           '/units – a list of all units in the office\n/workmate – select one workmate with written surname or id\n' \
           '/unit_workmates – a list of all workmates in the unit with choosen id\n/table – table of chosen unit\n' \
           '/unit_sickdoc - \n\nINSERT COMMANDS:\n/insert_workmate\n/insert_unit\n/insert_sick_paper\n\n' \
           'UPDATE COMMANDS:\n/update_workmate\n/update_unit\n/update_sick_paper\n\nDELETE COMMANDS:\n' \
           '/delete_workmate\n/delete_unit\n/delete_sick_paper\n\n'
    await message.answer(text)


# Function that creates a message the contains a list of all the workmates and etc
def message_select_workmates(ans):
    text = ""
    for row in ans:
        id = row[0]
        surname = row[1]
        name = row[2]
        unit_id = row[3]
        age = row[4]
        text += str(id) + " | " + str(name) + " | " + str(surname) + "| " + str(unit_id) + "| " + str(age) + "\n"
    message = """Received 📖 Information about workmates:\nid | name | surname | unit_id | age \n\n""" + text
    return message


def message_select_workmate(ans):
    text = ""
    for row in ans:
        id = row[0]
        surname = row[1]
        name = row[2]
        unit_id = row[3]
        age = row[4]
        sick_days = 0 if row[5] is None else row[5]
        text += str(id) + ": " + str(surname) + " " + str(name) + "| " + str(unit_id) + "| " + str(age) + " | " + \
                str(sick_days) + "\n"
    message = """Received 📖 Information about workmate:\nid: surname name | unit_id | age | sick days in current month
        \n\n""" + text
    return message


def message_select_units(ans):
    text = ""
    for row in ans:
        id = row[0]
        count_workmates = row[1]
        title = row[2]
        text += str(id) + " | " + str(title) + " | " + str(count_workmates) + "\n"
    message = """Received 📖 Information about workmates:\nid | title | count workmates\n\n""" + text
    return message


def message_select_table(ans):
    text = ""
    my_cursor.execute(f'SELECT count_work_days FROM mydb.month WHERE month_number={currentMonth}')
    worked_days = my_cursor.fetchone()[0]
    for row in ans:
        id = row[0]
        name = row[1]
        surname = row[2]
        days_worked = row[3]
        if days_worked is None:
            days_worked = worked_days

        sick = 0 if row[4] is None else row[4]
        text += str(id) + " | " + str(name) + " | " + str(surname) + "| " + str(sick) + "| " + str(days_worked) + "\n"
    message = """Received 📖 Information about workmates:\nid | name | surname | sick days | days worked\n\n""" + text
    return message

def message_select_workmates_sickdoc(ans):
    text = ""
    for row in ans:
        id = row[0]
        surname = row[1]
        name = row[2]

        text += str(id) + " | " + str(name) + " " + str(surname) + "\n"
    message = """Received 📖 Information about workmates:\nid | name surname \n\n""" + text
    return message

######
###### SELECT COMMANDS
######

keyboard_inline_workmate = InlineKeyboardMarkup()
keyboard_inline_workmate.add(InlineKeyboardButton(text="id", callback_data="id"),
                             InlineKeyboardButton(text="surname", callback_data="surname"))


@dp.message_handler(commands='workmate')
async def workmate(message: types.Message):
    await message.answer("Choose needed type of search", reply_markup=keyboard_inline_workmate)


@dp.callback_query_handler(text=["id", "surname"])
async def select_workmate(call: types.CallbackQuery):
    if call.data == "id":
        await Form.workmate_id.set()
        await call.message.answer("""INPUT\nworkmate's id""")
    if call.data == "surname":
        await Form.workmate_surname.set()
        await call.message.answer("""INPUT\nworkmate's surname""")


@dp.message_handler(state=Form.workmate_id)
async def select_workmate_id(message: types.Message, state: FSMContext):
    id_data = message.values["text"]
    try:
        id = int(id_data)
    except ValueError:
        await state.finish()
        await message.answer("sorry, you input wrong data type. please, try again")
        await message.answer("Choose needed type of search", reply_markup=keyboard_inline_workmate)
        return

    sql = f'''SELECT *, (SELECT SUM(count_days_disease) sum 
                        FROM mydb.sick_document 
                        WHERE workmate_id_workmate in (SELECT id_workmate 
                                                    FROM mydb.workmate 
                                                    WHERE id_workmate = {id}) 
                                                    AND month_number={currentMonth}
                        group by workmate_id_workmate ) sick_days 
                        FROM mydb.workmate WHERE id_workmate = {id}'''
    my_cursor.execute(sql)  # Execute the query
    data = my_cursor.fetchall()
    await state.finish()
    if data:
        testo_messaggio = message_select_workmate(data)
        await message.answer(testo_messaggio)
    else:
        text = "Something went wrong, please try again."
        await message.answer(text)


@dp.message_handler(state=Form.workmate_surname)
async def select_workmate_surname(message: types.Message, state: FSMContext):
    id_data = message.values["text"]
    try:
        surname = id_data.title()
        print(surname)
    except ValueError:
        await state.finish()
        await message.answer("sorry, you input wrong data type. please, try again")
        await message.answer("Choose needed type of search", reply_markup=keyboard_inline_workmate)
        return

    sql = f'''SELECT *, (SELECT SUM(count_days_disease) sum 
                        FROM mydb.sick_document 
                        WHERE workmate_id_workmate in (SELECT id_workmate 
                                                    FROM mydb.workmate 
                                                    WHERE surname = {surname}) 
                                                    AND month_number={currentMonth}
                        group by workmate_id_workmate ) sick_days 
                        FROM mydb.workmate WHERE surname = {surname}'''
    my_cursor.execute(sql)
    data = my_cursor.fetchall()
    print(data)
    await state.finish()
    if data:
        testo_messaggio = message_select_workmate(data)
        await message.answer(testo_messaggio)
    else:
        text = "Something went wrong, please try again."
        await message.answer(text)


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

# create inline keyboard with titles and unit's ids
buttons = []
keyboard_inline = InlineKeyboardMarkup()
for unit_id in range(count_units):
    number = unit_id + 1
    sql = f"SELECT title FROM mydb.unit where id = %s"
    my_cursor.execute(sql, (number,))
    title = my_cursor.fetchone()
    buttons.append(InlineKeyboardButton(text=f'unit {number}: {title[0]}', callback_data=f'unit_{number}'))
    keyboard_inline.add(InlineKeyboardButton(text=f'unit {number}: {title[0]}', callback_data=f'unit_{number}'))


######
###### SELECT COMMANDS for units
######

@dp.message_handler(commands='unit_workmates')
async def units_id_workmates(message: types.Message):
    await Form.unit_workmates.set()
    await message.reply("choose needed unit", reply_markup=keyboard_inline)


@dp.callback_query_handler(state=Form.unit_workmates)
async def unit_workmates(call: types.CallbackQuery, state: FSMContext):
    print(call["message"]["reply_markup"]["inline_keyboard"])
    # await call.message.answer(f"workmates of unit {str(call.text)}")
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
        unit_id = id + 1
        if call.data == buttons[id].callback_data:
            my_cursor.execute(f"""SELECT id_workmate, name, surname, (SELECT (SELECT count_work_days FROM mydb.month 
                                    WHERE month_number=1) - count_days_disease FROM mydb.sick_document 
									WHERE mydb.workmate.id_workmate = mydb.sick_document.workmate_id_workmate) number_days_worked,
                                    (SELECT count_days_disease FROM mydb.sick_document 
									WHERE mydb.workmate.id_workmate = mydb.sick_document.workmate_id_workmate) sick_days,
                                    ( SELECT (SELECT count_work_days FROM mydb.month WHERE month_number=1) - number_days_worked - sick_days) absenteeism
                                    FROM mydb.workmate WHERE unit_id = {unit_id}""")
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
    await Form.unit_sickdoc.set()
    await message.reply("choose needed unit", reply_markup=keyboard_inline)


@dp.callback_query_handler(state=Form.unit_sickdoc)
async def unit_info_sickdoc(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer(f'{str(call.data)}')
    my_cursor.execute('SELECT month_name FROM mydb.month WHERE month_number = 1')
    month = my_cursor.fetchall()
    await call.message.answer(f'month {str(month[0][0])}')
    for id in range(count_units):
        unit_id = id + 1
        if call.data == buttons[id].callback_data:
            my_cursor.execute(f"""SELECT id_workmate, surname, name, unit_id FROM workmate
                WHERE id_workmate in (SELECT id FROM sick_document 
                WHERE workmate_id_workmate in (SELECT id_workmate FROM workmate WHERE 
                unit_id={unit_id}) AND month_number={currentMonth})""")
            data = my_cursor.fetchall()
            if data:
                testo_messaggio = message_select_workmates_sickdoc(data)
                await call.message.answer(testo_messaggio)
            else:
                text = "No sick documents found inside this unit during current month."
                await call.message.answer(text)
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

    my_cursor.execute(f"SELECT count_workmates FROM mydb.unit WHERE id={unit_id}")
    count_workmates = int(my_cursor.fetchone()[0]) + 1
    my_cursor.execute(f"UPDATE unit SET count_workmates={count_workmates} WHERE id={unit_id}")
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
    my_cursor.execute(sql, (unit_title,))  # Execute the query
    db.mydb.commit()  # commit the changes
    await state.finish()

    if my_cursor.rowcount < 1:
        await message.answer("Something went wrong, please try again")
    else:
        await message.answer("Unit correctly inserted")


@dp.message_handler(commands='insert_sick_paper')
async def insert_sick_paper(message: types.Message):
    try:
        await Form.sick_paper.set()
        await message.answer("""INPUT\nbeginning_disease end_disease workmate's_id\n\n year-month-day\t2023-01-05""")

    except Exception as e:
        print(e)
        await message.answer("Conversation Terminated✔")
        return


@dp.message_handler(state=Form.sick_paper)
async def insert_sick_paper(message: types.Message, state: FSMContext):
    data_workmate = message.values["text"].split(" ")
    try:
        beginning_disease = data_workmate[0]
        end_disease = data_workmate[1]
        beginning = beginning_disease.split('-')
        data1 = datetime(int(beginning[0]), int(beginning[1]), int(beginning[2]))
        end = end_disease.split('-')
        data2 = datetime(int(end[0]), int(end[1]), int(end[2]))
        count_days = data2 - data1
        workmate_id = int(data_workmate[2])
    except ValueError:
        await state.finish()
        await message.answer("sorry, you input wrong data type. please, try again")
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


######
###### UPDATE COMMANDS
######

@dp.message_handler(commands='update_workmate')
async def update_workmate(message: types.Message):
    try:
        await Form.update_workmate.set()
        await message.answer("""INPUT new information about workmate\nid surname name unit_id age""")

    except Exception as e:
        print(e)
        await message.answer("Conversation Terminated✔")
        return


@dp.message_handler(state=Form.update_workmate)
async def update_workmate(message: types.Message, state: FSMContext):
    data_workmate = message.values["text"].split(" ")
    try:
        id = int(data_workmate[0])
        surname = data_workmate[1].title()
        name = data_workmate[2].title()
        unit_id = int(data_workmate[3])
        age = int(data_workmate[4])
    except ValueError:
        await state.finish()
        await message.answer("sorry, you input wrong data type. please, try again")
        await Form.workmate.set()
        return

    # Create the tuple "params" with all the parameters inserted by the user
    workmate = (surname, name, unit_id, age, id)
    sql = "UPDATE workmate SET surname = %s, name = %s, unit_id = %s, age = %s WHERE id_workmate = %s;"
    my_cursor.execute(sql, workmate)  # Execute the query
    db.mydb.commit()  # commit the changes
    await state.finish()

    if my_cursor.rowcount < 1:
        await message.answer("Something went wrong, please try again")
    else:
        await message.answer("Workmate correctly updated")


@dp.message_handler(commands='update_unit')
async def update_unit(message: types.Message):
    try:
        await Form.update_unit.set()
        await message.answer("""INPUT new information about unit\nid title""")

    except Exception as e:
        print(e)
        await message.answer("Conversation Terminated✔")
        return


@dp.message_handler(state=Form.update_unit)
async def update_unit(message: types.Message, state: FSMContext):
    data_unit = message.values["text"].split(" ")
    params = ()
    try:
        if len(data_unit) == 2:
            id = int(data_unit[0])
            title = data_unit[1]
            params = (title, id)
        else:
            # unit_title = message.values["text"].strip().replace(" ", "_")
            pass
    except ValueError:
        await state.finish()
        await message.answer("sorry, you input wrong data type. please, try again")
        # await message.answer("""INPUT new information about unit\nid title""")
        return

    sql = "UPDATE unit SET title = %s WHERE id = %s;"
    my_cursor.execute(sql, params)  # Execute the query
    db.mydb.commit()  # commit the changes
    await state.finish()

    if my_cursor.rowcount < 1:
        await message.answer("Something went wrong, please try again")
    else:
        await message.answer("Unit correctly updated")


@dp.message_handler(commands='update_sick_paper')
async def update_sick_paper(message: types.Message):
    try:
        await Form.update_sick_paper.set()
        await message.answer(
            """INPUT new information\ndocument's_id beginning_disease end_disease\n\n year-month-day\t2023-01-05""")

    except Exception as e:
        print(e)
        await message.answer("Conversation Terminated✔")
        return


@dp.message_handler(state=Form.update_sick_paper)
async def update_sick_paper(message: types.Message, state: FSMContext):
    data_workmate = message.values["text"].split(" ")
    try:
        id = int(data_workmate[0])
        beginning_disease = data_workmate[1]
        beginning = beginning_disease.split('-')
        data1 = datetime(int(beginning[0]), int(beginning[1]), int(beginning[2]))
        end_disease = data_workmate[2]
        end = end_disease.split('-')
        data2 = datetime(int(end[0]), int(end[1]), int(end[2]))
        count_days = data2 - data1
    except ValueError:
        await state.finish()
        await message.answer("sorry, you input wrong data type. please, try again")
        return

    data = (beginning_disease, end_disease, count_days.days, id)
    sql = "UPDATE sick_document SET beginning_disease = %s, end_disease = %s, count_days_disease = %s  WHERE id = %s"
    my_cursor.execute(sql, data)  # Execute the query
    db.mydb.commit()  # commit the changes
    await state.finish()

    if my_cursor.rowcount < 1:
        await message.answer("Something went wrong, please try again")
    else:
        await message.answer("Unit correctly updated")


######
###### DELETE COMMANDS
######

@dp.message_handler(commands='delete_workmate')
async def delete_workmate(message: types.Message):
    try:
        await Form.delete_workmate.set()
        await message.answer("""INPUT\nid workmate""")

    except Exception as e:
        print(e)
        await message.answer("Conversation Terminated✔")
        return


@dp.message_handler(state=Form.delete_workmate)
async def delete_workmate(message: types.Message, state: FSMContext):
    data_workmate = message.values["text"].split(" ")
    try:
        id = int(data_workmate[0])
    except ValueError:
        await state.finish()
        await message.answer("sorry, you input wrong data type. please, try again")
        await Form.workmate.set()
        return

    my_cursor.execute(f"SELECT unit_id FROM mydb.workmate WHERE id_workmate={id}")
    unit_id = my_cursor.fetchone()[0]

    sql = "DELETE FROM workmate WHERE id_workmate = %s;"
    my_cursor.execute(sql, (id,))  # Execute the query
    # db.mydb.commit()  # commit the changes

    my_cursor.execute(f"SELECT count_workmates FROM mydb.unit WHERE id={unit_id}")
    count_workmates = int(my_cursor.fetchone()[0]) - 1
    my_cursor.execute(f"UPDATE unit SET count_workmates={count_workmates} WHERE id={unit_id}")
    db.mydb.commit()  # commit the changes
    await state.finish()

    await state.finish()

    if my_cursor.rowcount < 1:
        await message.answer("Something went wrong, please try again")
    else:
        await message.answer("Workmate correctly deleted")


@dp.message_handler(commands='delete_unit')
async def delete_unit(message: types.Message):
    try:
        await Form.delete_unit.set()
        await message.answer("""INPUT\nid unit""")

    except Exception as e:
        print(e)
        await message.answer("Conversation Terminated✔")
        return


@dp.message_handler(state=Form.delete_unit)
async def delete_unit(message: types.Message, state: FSMContext):
    data_unit = message.values["text"].split(" ")
    try:
        id = int(data_unit[0])
    except ValueError:
        await state.finish()
        await message.answer("sorry, you input wrong data type. please, try again")
        await Form.workmate.set()
        return

    sql = "DELETE FROM unit WHERE id = %s;"
    my_cursor.execute(sql, (id,))  # Execute the query
    db.mydb.commit()  # commit the changes
    await state.finish()

    if my_cursor.rowcount < 1:
        await message.answer("Something went wrong, please try again")
    else:
        await message.answer("Unit correctly deleted")


@dp.message_handler(commands='delete_sick_paper')
async def delete_sick_paper(message: types.Message):
    try:
        await Form.delete_sick_paper.set()
        await message.answer("""INPUT\ndocument's id""")

    except Exception as e:
        print(e)
        await message.answer("Conversation Terminated✔")
        return


@dp.message_handler(state=Form.delete_sick_paper)
async def delete_sick_paper(message: types.Message, state: FSMContext):
    data_document = message.values["text"].split(" ")
    try:
        id = int(data_document[0])
    except ValueError:
        await state.finish()
        await message.answer("sorry, you input wrong data type. please, try again")
        await Form.workmate.set()
        return

    sql = "DELETE FROM sick_document WHERE id = %s;"
    my_cursor.execute(sql, (id,))  # Execute the query
    db.mydb.commit()  # commit the changes
    await state.finish()

    if my_cursor.rowcount < 1:
        await message.answer("Something went wrong, please try again")
    else:
        await message.answer("Unit correctly updated")


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
