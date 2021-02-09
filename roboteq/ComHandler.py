from pydantic import BaseModel
from queue import Queue
from typing import Optional, Callable
import time
import serial

class SerialHandler:
    """
    Serial Communication handler for Roboteq Devices using FIFO with Priority
    param: interruptExit - exits program with any error received (recommended for debugging)
    param: debugMode - prints every data sent to the controller and received from the controller
    """

    def __init__(self, interruptExit = False, debugMode = False):
        self.isConnected = False
        self.port = ""
        self.baudrate = 115200
        self.com = None
        self.interruptExit = interruptExit
        self.debugMode = debugMode

    def connect(self, port: str, baudrate: int = 115200) -> bool:
        """
        Attempt to establish connection with the controller
        If the attempt fails, the method will return False otherwise, True.

        """
        self.port = port
        self.baudrate = baudrate
        
        if self.debugMode == True:
            print(f"DEBUG MODE: {self.debugMode}")
            print(f"EXIT ON INTERRUPT: {self.interruptExit}")
            time.sleep(1)

        try: # attempt to create a serial object and check its status
            self.ser = serial.Serial(
                port = self.port,
                baudrate = self.baudrate,
                parity = serial.PARITY_NONE,
                stopbits = serial.STOPBITS_ONE,
                bytesize= serial.EIGHTBITS
            )
            if self.ser.isOpen():
                self.ser.close()
            self.ser.open()
            self.isConnected = True

        except Exception as e:
            if self.debugMode == True:
                print("DEBUG MODE: ERROR: Failed to connect to the roboteq device, read the exception error below:")
                print(e)
                print("\n")
            self.isConnected = False
            
        return self.isConnected

    def sendRawCommand(self, str_command: str = "") -> None:
        """
        Send a raw string command, the library will handle sending the command, but how you write it
        is up to you.
        """
        raw_command = f"{str_command}+\r"
        try:
            if self.debugMode == True:
                print(f"DEBUG MODE: Tx:{raw_command}")
            self.ser.write(raw_command.encode())

        except Exception as e:
            if self.debugMode == True:
                print("DEBUG MODE: Failed to send command to the controller, read the exception error below:")
                print(e)
                print("\n")
            if self.interruptExit == True:
                quit()
        
    def requestHandler(self, request: str = "") -> str:
        """
        Sends a command and a parameter, 
        """
        def getData(serial):
            rawData = b''
            while rawData == b'':
                try:
                    rawData = serial.read_all()
                except Exception as e:
                    if self.debugMode == True:
                        print("DEBUG MODE: Failed to read from the controller, read the exception error below:")
                        print(e)
                        print("\n")
                    if self.interruptExit == True:
                        quit()
                    rawData = b' '
            
            if self.debugMode == True:
                print(f"DEBUG MODE: Rx:{rawData}")
            return rawData

        self.sendRawCommand(request)
        result = getData(self.ser)
        result = result.decode()
        result = result.split("\r")
        try:
            return result[1]
        
        except IndexError: # will raise index error as sometimes the controller will return an odd answer, its rare, so its simply ignored.
            debug_return = "DEBUG MODE: Received faulty message, ignoring..."
            if self.interruptExit == True:
                quit()
            if self.debugMode == True:
                print(debug_return)
            return debug_return

    def dualMotorControl(self, left_motor: int = 0, right_motor: int = 0) -> None:
        """
        Controlling the motor using a Dual Drive mode
        Send speed for the left, and right side of the robot/vehicle seperately 
        Effective for doing Pivot drive and running track based robots
        left_motor: integer from -1000 to 1000
        right_motor: integer from -1000 to 1000
        """
        raw_command = f"!M {left_motor} {right_motor} "
        self.requestHandler(raw_command)
    
    def send_command(self, command: str, first_parameter = "", second_parameter = "") -> None:
        if first_parameter != "" and second_parameter != "":
            message = f"{command} {first_parameter} {second_parameter} "
        if first_parameter != "" and second_parameter == "":
            message = f"{command} {first_parameter} "
        if first_parameter == "" and second_parameter == "":
            message = f"{command} "
        
        try:
            response = self.requestHandler(message)
        except Exception as e:
            if self.debugMode == True:
                print("DEBUG MODE: Failed to construct a message, read the exception error below:")
                print(e)
                print(f"Received message: {response}")
                print("\n")
            if self.interruptExit == True:
                quit()

    def read_value(self, command: str = "", parameter = "") -> str:
        """
        Constructs a message and sends it to the controller.
        param: command (str)
        param: parameter (str/int)
        returns: answer from the controller, data from request commands, or echo from action commands.
        """
        request = f"{command} [{parameter}]"
        response = self.requestHandler(request)
        return response