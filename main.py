from signal import signal, SIGTERM, SIGHUP, pause
from sqlite3.dbapi2 import Date
import RPi.GPIO as GPIO
from rpi_lcd import LCD
from pad4pi import rpi_gpio
from enum import Enum
from datetime import datetime
import sqlite3 as  sql
import requests
import time


ip = "http://localhost:8080" #Do testow loklanych
#ip = "http://192.168.1.57:8080" #Do testow z telefonem jako routerem
#ip = "http://192.168.1.16:8080" #Do testow z routerem w moim domu
r = requests.post("http://localhost:8080", "123457") #Do testow bez aplikacji

#Stany dla maszyny stanow wyswietlacza
class STATE(Enum):
    AWAITING_CODE = 0
    ENTER_CODE = 1
    CORRECT_CODE = 2
    INCORRET_CODE = 3
    TIME_OUT = 4
    OPEN_DOOR = 5
    CLOSE_DOOR = 6
    NO_CODE= 7

#Ustawienie pinow w oznaczenia BCM
def init_raspberry_pi():
    GPIO.setmode(GPIO.BCM)

#Inicjalizacja ekranu
def init_lcd():
    lcd = LCD()
    return lcd

#Inicjalizacja serwo
def init_servomechanism():
    duty_cycle = 2.5 #Wartosc domyslna dla 'drzwi'
    servo_pin = 18
    GPIO.setup(servo_pin, GPIO.OUT)
    pwm_servo = GPIO.PWM(servo_pin, 50)
    pwm_servo.start(duty_cycle)
    return pwm_servo

#Inicjalizacja klawiatury
def init_keyboard():
    #Ustawienie layoutu klawiatury
    KEYPAD = [
        ["1","2","3","A"],
        ["4","5","6","B"],
        ["7","8","9","C"],
        ["*","0","#","D"]
    ]
    ROW_PINS = [4, 14, 15, 17] # BCM 
    COL_PINS = [13, 27, 22, 23] # BCM 
    factory = rpi_gpio.KeypadFactory()
    keypad = factory.create_keypad(keypad=KEYPAD,row_pins=ROW_PINS, col_pins=COL_PINS) #stworzenie klasy klawiatury membranowej
    return keypad

#Ustawienie zmiennyhc globalnych
init_raspberry_pi()
keypad = init_keyboard()
servo = init_servomechanism()
lcd = init_lcd()
# Inicjalizacja bazy danych
database = sql.connect("data.db", check_same_thread=False)
cursor = database.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS blik(data text, expected text, recevied text, status integer)")

entered_code = "" #kod wpisany przez uzytkownika

#Stany dla maszyny stanow
current_state = STATE.AWAITING_CODE
previous_state = STATE.AWAITING_CODE

#Zmana stanow w maszynie stanow wyswietlacza
def switch_state(state):
    global current_state, previous_state
    current_state = STATE(state)
    if previous_state != current_state: #jezeli poprzedni stan jest inny niz obecny nalezy zaktualizowac zawartosc ekranu
        refresh_screen()
    previous_state = current_state

#Ustawianie zawartosci ekranu na podstawie obecnego stanu
def refresh_screen():
    lcd.clear()
    if current_state == STATE.AWAITING_CODE:
        lcd.text("Welcome!", 1)
        lcd.text("Awaiting input!", 2)
        time.sleep(1)
    elif current_state == STATE.ENTER_CODE:
        lcd.text("Enter code:", 1)
        lcd.text(len(entered_code) * "*", 2)
    elif current_state == STATE.CORRECT_CODE:
        lcd.text("Code accepted!", 1)
        time.sleep(3)
    elif current_state == STATE.INCORRET_CODE:
        lcd.text("Incorrect code!", 1)
        time.sleep(5)
    elif current_state == STATE.TIME_OUT:
        lcd.text("Time passed!", 1)
        time.sleep(3)
    elif current_state == STATE.OPEN_DOOR:
        lcd.text("Door opened!", 1)
        time.sleep(3)
    elif current_state == STATE.CLOSE_DOOR:
        lcd.text("Door closed!", 1)
        time.sleep(4)
    if current_state == STATE.NO_CODE:
        lcd.text("No passcode!", 1)
        lcd.text("Create from app!", 2)
        time.sleep(5)

#Sprzatanie zmiennyhc i ich wartosci po zakonczeniu/zatrzymaniu dzialania programu
def cleanup():
    database.commit()
    cursor.close()
    keypad.cleanup()
    lcd.clear()

#Otworzenie 'drzwi'
def open_door():
    duty_cycle = 10.0
    servo.ChangeDutyCycle(duty_cycle)

#Zamkniece 'drzwi'
def close_door():
    duty_cycle = 2.5
    servo.ChangeDutyCycle(duty_cycle)

#Sekwencja operacji po wprowadzeniu poprawnego kodu
def correct_passcode_entered():
    switch_state(STATE.CORRECT_CODE)
    open_door()
    switch_state(STATE.OPEN_DOOR)
    close_door()
    switch_state(STATE.CLOSE_DOOR)

#sekwencja operacji po wprowadzeniu nieprawidłówego kodu
def incorrect_passcode_entered():
    switch_state(STATE.INCORRET_CODE)

#sekwencja olperacji po zatwierdzeniu kodu po upływie limitu czasowego
def time_out():
    switch_state(STATE.TIME_OUT)

#sekwencja operacji po zatwierdzeniu kodu kiedy nie wygenerowany został zaden kod
def no_code():
    switch_state(STATE.NO_CODE)

#funkcja sprawdzajaca jaki kod został wpisany po zatwierdzeniu przyciskiem 'A'
def check_passcode():
    global entered_code
    http_code = requests.get(ip).text #pobranie kodu z serwera w formie textu
    dt_string = datetime.now().strftime("%d/%m/%Y %H:%M:%S") #zmienna zawierajaca aktualna date
    deactive_keyboard() #wylaczenie klawiatury na czas sprawdzania kodu (zapobiega modyfikacji podczas sp[rawdzania poprawnosci])
    if entered_code == http_code:
        #wprowadzono poprawny kod
        cursor.execute("INSERT INTO blik VALUES (?,?,?,?)", (dt_string, http_code, entered_code, 1))
        correct_passcode_entered()
        database.commit()
    elif http_code == "Time":
        #zatwierdzono kod po uplynieciu czasu
        cursor.execute("INSERT INTO blik VALUES (?,?,?,?)", (dt_string, http_code, entered_code, 0))
        time_out()
        database.commit()
    elif http_code == 'None':
        #zatwierdzono kod gdy w aplikacji nie ma wygenerowanego żadnego kodu
        no_code()
    elif http_code != entered_code:
        #wprowadzono niepoprawny kod
        cursor.execute("INSERT INTO blik VALUES (?,?,?,?)", (dt_string, http_code, entered_code, -1))
        incorrect_passcode_entered()
        database.commit()
    else:
        #awaria (niemozliwe do spelnienia)
        print("BUG")
    entered_code = ""
    requests.post(ip,data = 'None')  #zresetowanie kodu do None
    switch_state(STATE.AWAITING_CODE)
    activate_keyboard() #Powrotne aktywowanie klawiatury

#Funkcja ktora wykonujemy kiedy nacisniemy klawisz z cyfra
def digit_entered(key):
    global entered_code
    entered_code += str(key)
    switch_state(STATE.ENTER_CODE)
    refresh_screen()

#funkcja wykonywana w momencie nacisniecia klawisza innego niz cyfra
def non_digit_entered(key):
    global entered_code

    # * usuwa ostatnia wpisana przez uzytkownika cyfre
    if key == "*" and len(entered_code) > 0:
        entered_code = entered_code[:-1]
        refresh_screen()

    # 'A' zatwierdza obecny wpisany kod i przechodzi do sprawdzenia jego poprawnosci    
    if key == "A":
        check_passcode()

    # 'B' wypisuje na konsole ostatni wpis w bazie danych
    if key == "B":
        cursor.execute("SELECT * FROM blik ORDER BY data DESC")
        print(cursor.fetchone())

    # 'C' usuwa cały wpisany obecnie kod
    if key == "C":
        entered_code = ""
        refresh_screen()

    # 'D' wyłącza program i czysci elementy
    if key == "D":
        cleanup()
        exit()

#funkcja przechwytujaca nacisniecia klawiszy klawiatury
def key_pressed(key):
    try:
        int_key = int(key)
        if int_key >= 0 and int_key <= 9:
            digit_entered(key)
    except ValueError:
        non_digit_entered(key)


def activate_keyboard():
    keypad.registerKeyPressHandler(key_pressed)

def deactive_keyboard():
    keypad.unregisterKeyPressHandler(key_pressed)

def main():
    try:
        refresh_screen() #pierwsze odswiezenie ekranu
        activate_keyboard() #wlaczenie mozliwosci wpisywania znakow na klawiaturze
        while True:
            #w tym mijescu czekamy na input z klawiatury
            time.sleep(0.3)
    except KeyboardInterrupt: #w momencie CTRL+C wylaczenie klawiatury
        pass
    finally:
        cleanup()



if __name__ == "__main__":
    main()