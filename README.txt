1. sudo apt-get update
2. sudo apt-get upgrade
3. sudo apt-get install build-essential git python3-dev python3-pip python3-smbus
4. Check layout and clone adafruit LCD:
git clone https://github.com/pimylifeup/Adafruit_Python_CharLCD.git
5. cd ./Adafruit_Python_CharLCD
   sudo python3 setup.py install
6. config gpio:
sudo nano ~/Adafruit_Python_CharLCD/examples/char_lcd.py
find the line: # Raspberry Pi pin configuration:
lcd_rs = 4
lcd_en = 24
lcd_d4 = 23
lcd_d5 = 17
lcd_d6 = 18
lcd_d7 = 22

7. ctrl+x and press "Y" and then enter.
8. sudo pip3 install RPi.GPIO 
9. Check: python3 ~/Adafruit_Python_CharLCD/examples/char_lcd.py
10. Connect wire of RFID with Raspberry
SDA --> GPIO8  (Chân vật lý 24)
SCK --> GPIO11 (Chân vật lý 23)
MOSI --> GPIO10 (Chân vật lý 19)
MISO --> GPIO9 (Chân vật lý 21)
RST --> GPIO25 (Chân vật lý 22)

11. sudo raspi-config
active SPI
12. sudo reboot
13. lsmod | grep spi 
Check "spi_bcm2835", DONE.
14. sudo pip3 install spidev
15. sudo pip3 install mfrc522

#######################################

16. Database for system
sudo apt-get install mysql-server -y 
17. sudo mysql_secure_installation (reply: y)
18. sudo mysql -u root -p 
19. CREATE DATABASE attendancesystem;
20. CREATE USER 'attendanceadmin'@'localhost' IDENTIFIED BY 'raspberry';
21. GRANT ALL PRIVILEGES ON attendancesystem.* TO 'attendanceadmin'@'localhost';
22. use attendancesystem;

create table attendance(
   id INT UNSIGNED NOT NULL AUTO_INCREMENT UNIQUE,
   user_id INT UNSIGNED NOT NULL,
   clock_in TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
   PRIMARY KEY ( id )
);

create table users(
   id INT UNSIGNED NOT NULL AUTO_INCREMENT UNIQUE,
   rfid_uid VARCHAR(255) NOT NULL,
   name VARCHAR(255) NOT NULL,
   created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
   PRIMARY KEY ( id )
);

23. exit;
24. sudo pip3 install mysql-connector-python 
25. mkdir ~/attendancesystem
26. sudo nano ~/attendancesystem/save_user.py
27. add code

#!/usr/bin/env python

import time
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
import mysql.connector
import Adafruit_CharLCD as LCD

db = mysql.connector.connect(
  host="localhost",
  user="attendanceadmin",
  passwd="pimylifeup",
  database="attendancesystem"
)

cursor = db.cursor()
reader = SimpleMFRC522()
lcd = LCD.Adafruit_CharLCD(4, 24, 23, 17, 18, 22, 16, 2, 4);

try:
  while True:
    lcd.clear()
    lcd.message('Place Card to\nregister')
    id, text = reader.read()
    cursor.execute("SELECT id FROM users WHERE rfid_uid="+str(id))
    cursor.fetchone()

    if cursor.rowcount >= 1:
      lcd.clear()
      lcd.message("Overwrite\nexisting user?")
      overwrite = input("Overwite (Y/N)? ")
      if overwrite[0] == 'Y' or overwrite[0] == 'y':
        lcd.clear()
        lcd.message("Overwriting user.")
        time.sleep(1)
        sql_insert = "UPDATE users SET name = %s WHERE rfid_uid=%s"
      else:
        continue;
    else:
      sql_insert = "INSERT INTO users (name, rfid_uid) VALUES (%s, %s)"
    lcd.clear()
    lcd.message('Enter new name')
    new_name = input("Name: ")

    cursor.execute(sql_insert, (new_name, id))

    db.commit()

    lcd.clear()
    lcd.message("User " + new_name + "\nSaved")
    time.sleep(2)
finally:
  GPIO.cleanup()

28. python3 ~/attendancesystem/save_user.py
29. sudo nano ~/attendancesystem/check_attendance.py
30 add code

#!/usr/bin/env python
import time
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
import mysql.connector
import Adafruit_CharLCD as LCD

db = mysql.connector.connect(
  host="localhost",
  user="attendanceadmin",
  passwd="pimylifeup",
  database="attendancesystem"
)

cursor = db.cursor()
reader = SimpleMFRC522()

lcd = LCD.Adafruit_CharLCD(4, 24, 23, 17, 18, 22, 16, 2, 4);

try:
  while True:
    lcd.clear()
    lcd.message('Place Card to\nrecord attendance')
    id, text = reader.read()

    cursor.execute("Select id, name FROM users WHERE rfid_uid="+str(id))
    result = cursor.fetchone()

    lcd.clear()

    if cursor.rowcount >= 1:
      lcd.message("Welcome " + result[1])
      cursor.execute("INSERT INTO attendance (user_id) VALUES (%s)", (result[0],) )
      db.commit()
    else:
      lcd.message("User does not exist.")
    time.sleep(2)
finally:
  GPIO.cleanup()

31. python3 ~/attendancesystem/check_attendance.py
32. Check database
sudo mysql -u root -p
33. use attendancesystem;
34. SELECT * FROM users;
35. SELECT * FROM attendance;
36. exit;
37. sudo mkdir /var/www/html/attendance
38. sudo git clone https://github.com/pimylifeup/attendance-system-frontend.git /var/www/html/attendance
39. sudo nano /var/www/html/attendance/common.php
40. 'password'      => 'raspberry'
41. http://Pi's_ip/attendance
