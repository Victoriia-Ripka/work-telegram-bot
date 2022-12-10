# import db
import logging
from aiogram import Bot, Dispatcher, executor, types

API_TOKEN = '5649458393:AAHgc8zf-IIXjyu7RQaCy7NBwu4HpUXvpRQ'

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)


@dp.message_handler(commands="test1")
async def cmd_test1(message: types.Message):
    await message.reply("Test 1")

executor.start_polling(dp, skip_updates=True)





# my_cursor = db.mydb.cursor()

# sql = 'UPDATE workmate SET age = 20 WHERE id_workmate<13'
# my_cursor.execute(sql)
# mydb.commit()
# sql = 'SELECT * FROM workmate'
# my_cursor.execute(sql)
# result = my_cursor.fetchall()
# for row in result:
#     print(row)

# print WORKMATES how to change unit_id
# unit_id = '1'
# sql = 'SELECT * FROM workmate WHERE unit_id = %s'
# my_cursor.execute(sql, unit_id)
# my_result = my_cursor.fetchall()
# print("workmate_id: surname name unit_id age")
# for row in my_result:
#     print(row)

# print UNITS
# my_cursor.execute('SELECT * FROM unit')
# my_result = my_cursor.fetchall()
# print("unit_id: count_workmates")
# for row in my_result:
#     print(row[0], ": ", row[1])

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
#
# for db in my_cursor:
#     print(db)
