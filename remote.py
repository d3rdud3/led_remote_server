from flask import Flask
import subprocess
from apscheduler.schedulers.background import BackgroundScheduler
from flask import request
import atexit
import time
from flask_cors import CORS, cross_origin
app = Flask(__name__)
CORS(app)

def execute(keyIdent):
    cmd = ["/usr/bin/irsend","SEND_ONCE","led",keyIdent]
    p = subprocess.Popen(cmd, stdout = subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            stdin=subprocess.PIPE)
    out,err = p.communicate()
    return "200"

scheduler = BackgroundScheduler()

@app.route("/on")
def on():
    setLightEnabledState(True)
    return execute("KEY_POWER")

@app.route("/off")
def off():
    setLightEnabledState(False)
    return execute("KEY_POWER2")

@app.route("/brightnessup")
def brightnessup():
    return execute("KEY_BRIGHTNESSUP")

@app.route("/brightnessdown")
def brightnessdown():
    return execute("KEY_BRIGHTNESSDOWN")

@app.route("/red")
def red():
    return execute("KEY_RED")

@app.route("/green")
def green():
    return execute("KEY_GREEN")

@app.route("/blue")
def blue():
    return execute("KEY_BLUE")

@app.route("/white")
def white():
    return execute("BTN_0")

@app.route("/redone")
def redone():
    return execute("BTN_1")

@app.route("/greenone")
def greenone():
    return execute("BTN_2")

@app.route("/blueone")
def blueone():
    return execute("BTN_3")

@app.route("/actionone")
def actionone():
    return execute("KEY_PROG1")

@app.route("/redtwo")
def redtwo():
    return execute("BTN_4")

@app.route("/greentwo")
def greentwo():
    return execute("BTN_5")

@app.route("/bluetwo")
def bluetwo():
    return execute("BTN_6")

@app.route("/actiontwo")
def actiontwo():
    return execute("KEY_PROG2")

@app.route("/redthree")
def redthree():
    return execute("BTN_7")

@app.route("/greenthree")
def greenthree():
    return execute("BTN_8")

@app.route("/bluethree")
def bluethree():
    return execute("BTN_9")

@app.route("/actionthree")
def actionthree():
    return execute("KEY_PROG3")

@app.route("/redfour")
def redfour():
    return execute("KEY_YELLOW")

@app.route("/greenfour")
def greenfour():
    return execute("BTN_A")

@app.route("/bluefour")
def bluefour():
    return execute("BTN_B")

@app.route("/actionfour")
def actionfour():
    return execute("KEY_PROG4")

@app.route("/alive")
def heartbeat():
    return "200"

@app.route("/sunrise")
def sunrise():
    with open("/home/pi/piremote/enabled.props", "r") as infile:
        for line in infile:
            if(line == "enabled"):
                #start on
                on()
                #red color
                red()

                #brightness down max
                for num in range(0,20):
                    time.sleep(.5)
                    brightnessdown()

                #brightnessup slow
                for num in range(0,3):
                    time.sleep(1.5)
                    brightnessup()

                #orange
                time.sleep(1)
                redtwo();

                # brightnessup slow
                for num in range(0,4):
                    time.sleep(1.5)
                    brightnessup()

                #yellow
                time.sleep(1)
                redthree()

                # brightnessup slow
                for num in range(0,6):
                   time.sleep(1.5)
                   brightnessup()

                # daylight
                time.sleep(60)
                return white()
    return ""		

# schedule new timer
def reschedule(hour,min):
    scheduler.remove_all_jobs()
    scheduler.add_job(sunrise, 'cron', day_of_week='mon-fri', hour=hour, minute=min, second=0)

# set sunrise time
@app.route("/sunrisetime", methods=['POST'])
def sunrisetime():
    request_data = request.get_json()
    file = open("/home/pi/piremote/remote.props","w")
    file.write(request_data['time'])
    file.close()
    readprops()
    return "200"

# set sunrise time
@app.route("/setEnabledState", methods=['POST'])
def setEnabledState():
    print(request)
    request_data = request.get_json()
    print(request_data)
    if(request_data['disable'] == 'enable'):
        file = open("/home/pi/piremote/enabled.props", "w")
        file.write("enabled")
        file.close()
    if(request_data['disable'] == "disable"):
        file = open("/home/pi/piremote/enabled.props", "w")
        file.write("disabled")
        file.close()
    return "200"

# set persistent light state
def setLightEnabledState(state):
    if(state==True):
        file = open("/home/pi/piremote/light_enabled.props", "w")
        file.write("enabled")
        file.close()
    else:
        file = open("/home/pi/piremote/light_enabled.props", "w")
        file.write("disabled")
        file.close()

# set sunrise time
@app.route("/timerState")
def sunrisetimeState():
    with open("/home/pi/piremote/remote.props", "r") as infile:
        for line in infile:
            return line

# set sunrise time
@app.route("/lightState")
def enabledLightState():
    with open("/home/pi/piremote/light_enabled.props", "r") as infile:
        for line in infile:
            return line

# set sunrise time
@app.route("/enabledState")
def enabledState():
    with open("/home/pi/piremote/enabled.props", "r") as infile:
        for line in infile:
            return line

# read props and set new scheduler
def readprops():
    with open("/home/pi/piremote/remote.props", "r") as infile:
        for line in infile:
            items = line.split(":")
            reschedule(items[0],items[1])

# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())

if __name__ == "__main__":
#    request_data = request.get_json()
    file = open("/home/pi/piremote/remote.props", "w")
    file.write("6:00")
    file.close()
    scheduler.start()
    scheduler.add_job(sunrise, 'cron', day_of_week='mon-fri', hour=6, minute=0, second=0)
    app.run(host='0.0.0.0', port=8444)
