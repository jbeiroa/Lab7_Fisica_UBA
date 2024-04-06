import serial

class Arduino(object):
    """

    Class that handles an Arduino to turn an LED on/off.

    """

    def __init__(self, usbport='COM3', baud=9600):
        self.ser = serial.Serial(
        port=usbport,
        baudrate=baud,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        timeout=1,
        xonxoff=0,
        rtscts=0,
        interCharTimeout=None
        )

    def led_on(self):
        """Arduino waits for 'p' to be sent and then turns the LED on.
        """
        self.ser.flush() #flush before sending signal
        self.ser.write(b'p')

    def led_off(self):
        """Arduino waits for 'a' to be sent and then turns the LED off.
        """
        self.ser.flush() #flush before sending signal
        self.ser.write(b'a')