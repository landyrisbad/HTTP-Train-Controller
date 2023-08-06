from server import Server, Responses, urls
import RPi.GPIO as io

pwm = 21
in1 = 20
in2 = 16

io.setmode(io.BCM)
io.setup(in1,io.OUT)
io.setup(in2,io.OUT)
io.output(in1,io.LOW)
io.output(in2,io.HIGH)
io.setup(pwm,io.OUT)
speed=io.PWM(pwm,50)
speed.start(0)

class Views:
    @urls.route("/")
    def index():
        return Responses.render("index.html")

    @urls.route("/speed/<int:value>")
    def setSpeed(args):
        try:
            speed.ChangeDutyCycle(args["value"]*10)
        except Exception as e:
            return str(e).encode()
        return f"success, speed set {args['value']*10}".encode()

    @urls.route("/direction/<int:value>")
    def setDirection(args):
        try:
            if args["value"] == 0:
                io.output(in1,io.HIGH)
                io.output(in2,io.LOW)
            elif args["value"] == 1:
                io.output(in1,io.LOW)
                io.output(in2,io.HIGH)
        except Exception as e:
            return str(e).encode()

        return f"success, direction set {args['value']}".encode()


Server.run(80, Views)
io.cleanup()
