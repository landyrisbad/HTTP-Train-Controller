from server import Server, Responses, urls
import RPi.GPIO as IO

class Controller:
    def __init__(self, pwmPin, in1Pin, in2Pin):
        self.pwmPin = pwmPin
        self.in1Pin = in1Pin
        self.in2Pin = in2Pin
        self.speedVal = 0

        IO.setup(self.in1Pin, IO.OUT)
        IO.setup(self.in2Pin, IO.OUT)
        IO.output(self.in1Pin, IO.LOW)
        IO.output(self.in2Pin, IO.HIGH)
        IO.setup(self.pwmPin, IO.OUT)
        self.speed = IO.PWM(self.pwmPin, 50)
        self.speed.start(0)

    def setDirection(self, value):
        if value == 0:
            IO.output(self.in1Pin, IO.HIGH)
            IO.output(self.in2Pin, IO.LOW)
        elif value == 1:
            IO.output(self.in1Pin, IO.LOW)
            IO.output(self.in2Pin, IO.HIGH)

    def setSpeed(self, value):
        self.speedVal = value
        self.speed.ChangeDutyCycle(value)

IO.setmode(IO.BCM)
controllers = [Controller(21, 20, 16), Controller(1, 7, 8)]

class Views:
    @urls.route("/")
    def index():
        return Responses.render("index.html")

    @urls.route("/speed/<int:target>/<int:value>")
    def setSpeed(args):
        try:
            controllers[args["target"]].setSpeed(args["value"] * 10)
        except Exception as e:
            return str(e).encode()
        return f"success, speed set {args['value']*10} on track {args['target']}".encode()

    @urls.route("/direction/<int:target>/<int:value>")
    def setDirection(args):
        try:
            controllers[args["target"]].setDirection(args["value"])
        except Exception as e:
            return str(e).encode()

        return f"success, direction set {args['value']} on track {args['target']}".encode()

    @urls.route("/speed/<int:target>")
    def giveSpeed (args):
        try:
            return f"{controllers[args['target']].speedVal}"
        except Exception as e:
            return f"failed with {e}"

    @urls.route("/zoneinfo")
    def zoneinfo ():

        return f"{len(controllers)},0"

    @urls.route("/autorun/<int:value>/<int:loopNum>")
    def setAutoRun(args):
        pass

Server.run(80, Views)
IO.cleanup()