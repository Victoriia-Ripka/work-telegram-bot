import mysql.connector

mydb = mysql.connector.connect(
  host="127.0.0.1",
  user="root",
  password="iamfp_MYSQL1",
  database='mydb',
  auth_plugin='mysql_native_password'
)

print(mydb)
