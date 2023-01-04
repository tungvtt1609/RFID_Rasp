#!/usr/bin/env python
import time    #setup time hệ thống
import RPi.GPIO as GPIO    #thư viện sử dụng GPIO
from mfrc522 import SimpleMFRC522   #thư viện sử dụng module RFID
import mysql.connector    #thư viện sử dụng mysql
import Adafruit_CharLCD as LCD    #thư viện sử dụng LCD

db = mysql.connector.connect(      #tạo database
  host="localhost",
  user="attendanceadmin",
  passwd="raspberry",
  database="attendancesystem"
)

cursor = db.cursor()   #khởi tạo database
reader = SimpleMFRC522()    #khởi tạo RFID

lcd = LCD.Adafruit_CharLCD(4, 24, 23, 17, 18, 22, 16, 2, 4);     #khai báo chân LCD

try:      #thực hiện đọc thẻ card
  while True:
    lcd.clear()
    lcd.message('Place Card to\nrecord attendance')
    id, text = reader.read()

    cursor.execute("Select id, name FROM users WHERE rfid_uid="+str(id))   #lưu trữ dữ liệu id
    result = cursor.fetchone()

    lcd.clear()

    if cursor.rowcount >= 1:
      lcd.message("Welcome " + result[1])
      cursor.execute("INSERT INTO attendance (user_id) VALUES (%s)", (result[0],) )   #chèn user_id vào từng giá trị cột
      db.commit()
    else:
      lcd.message("User does not exist.")
    time.sleep(2)
finally:
  GPIO.cleanup()