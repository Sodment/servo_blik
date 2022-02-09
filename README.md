# servo_blik

A flutter app and python server created as a project for Embeded Systems course. It functions similarly to BLIK as the user generates code to enter on the keyboard to move the servomechanism. After a couple of seconds the code expires and you need to generate a new one to eneter. The RPi serves as server and database and App is only required for code generation and time counting

## Requirements:
  - RaspberryPi (capable of running python 3.6 or newer, we used RaspberryPI 4B)
  - An Android or iOS device comatible for development in Flutter 2.2.3 or newer
  - Membrane 4x4 keyboard
  - Servomechanism
  - i2c compatible LCD display
  
## Getting Started
  1. Connect peripherals using the main.py code for keyboard and servo, LCD display should by connected by using adequet GPIO on RPi for i2c
  2. Run server.py on your raspberry pi
  3. Run main.py on your raspberyy pi (should coexist with server.py)
  4. If everything goes right the LCD should display a welcome message
  5. You can now use app to send the code to the server and move the servo with it

## How to use
The keys on keyboard are matched as followed: 
0-9 - number imputs

A - check the current code and insert an entry request into the database (Display should pop up a messaage about correctness of the code)

B - DEBUG, prints out on the CONSOLE last entry to the database

C - delete enetered by keyboard code

D - exits the app (only the main.py!)

\* - deletes the last entered digit

To generate code use the app (there is only one button there "Generate code!")

  

