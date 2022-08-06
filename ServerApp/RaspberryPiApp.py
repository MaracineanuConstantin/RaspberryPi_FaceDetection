import socket
import RPi.GPIO as GPIO
import pigpio
import time

# Set servomotors pins
servoX= 17
servoY= 22 
 
pwmX = pigpio.pi() 
pwmX.set_mode(servoX, pigpio.OUTPUT)
 
pwmX.set_PWM_frequency(servoX,50)

pwmY = pigpio.pi() 
pwmY.set_mode(servoY, pigpio.OUTPUT)
 
pwmY.set_PWM_frequency(servoY,50)

# Set initial servoX position to 90 degrees
Xcurrent = 1500

pwmX.set_servo_pulsewidth(servoX,Xcurrent) 
time.sleep(0.5)

# Set initial servoY position to 110 degrees
Ycurrent = 1722

pwmY.set_servo_pulsewidth(servoY,Ycurrent) 
time.sleep(0.5)

# Connection
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socket:
    ip = "172.20.10.11"
    port = 65433
    socket.bind((ip,port))
    socket.listen(5)
    connection, address = socket.accept()
    with connection:
        print("Server is connected")
        while True:
            
            # Decodes received data
            data = connection.recv(2048).decode('utf-8')
            if data:
                print(data)
            
            index,moveUp,moveRight,moveDown,moveLeft=data.split(",")
            moveUp=int(moveUp)
            moveRight=int(moveRight)
            moveDown=int(moveDown)
            moveLeft=int(moveLeft)
            
            print("moveUp: ",moveUp)
            print("moveRight: ",moveRight)
            print("moveDown: ",moveDown)
            print("moveLeft: ",moveLeft)
            
            
            # Check the 80x80 squares to see where the face is located and center the face
            if moveLeft != 0:
                if moveLeft == 1:
                    Xcurrent = Xcurrent + 50
                if moveLeft == 2:
                    Xcurrent = Xcurrent + 100
                if moveLeft == 3:
                    Xcurrent = Xcurrent + 150
        
            if moveRight != 0:
                if moveRight == 1:
                    Xcurrent = Xcurrent - 50
                if moveRight == 2:
                    Xcurrent = Xcurrent - 100
                if moveRight == 3:
                    Xcurrent = Xcurrent - 150
        
            pwmX.set_servo_pulsewidth(servoX,Xcurrent)
            time.sleep(0.1)
            
            if moveUp != 0:
                if moveUp == 1:
                    Ycurrent = Ycurrent + 50
                if moveUp == 2:
                    Ycurrent = Ycurrent + 150
        
            if moveDown != 0:
                if moveDown == 1:
                    Ycurrent = Ycurrent - 50
                if moveDown == 2:
                    Ycurrent = Ycurrent - 150
                    
            pwmY.set_servo_pulsewidth(servoY,Ycurrent)
            time.sleep(0.1)
            
            moveUp = 0
            moveRight = 0
            moveDown = 0
            moveLeft = 0
            
            # Reset servomotors to inital position
            if Xcurrent < 600 or Xcurrent > 2400:
                print ("Reset servoX to initial position.")
                Xcurrent = 1500
                pwmX.set_servo_pulsewidth(servoX,Xcurrent)
            
            if Ycurrent < 1200 or Ycurrent > 2100:
                print ("Reset servoY to initial position.")
                Ycurrent = 1600
                pwmY.set_servo_pulsewidth(servoY,Ycurrent)

# Exit the program
pwmX.set_PWM_dutycycle(servoX,0)
pwmX.set_PWM_frequency(servoX,0)

pwmY.set_PWM_dutycycle(servoY,0)
pwmY.set_PWM_frequency(servoY,0)
                