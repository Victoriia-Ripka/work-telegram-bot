import mysql.connector

mydb = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="iamfp_MYSQL1",
    database='mydb',
    auth_plugin='mysql_native_password'
)

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
