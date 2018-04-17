from flask import Flask
from flask import render_template
from flask import request
from flask_login import LoginManager
from flask_login import login_required
from flask_login import login_user
from flask_login import logout_user
from flask import redirect
from flask import url_for
from flask import request

from mockdbhelper import MockDBHelper as DBHelper
from user import User

app = Flask(__name__)
app.secret_key = 'thsPdhakdlOhdlash4et'
login_manager =  LoginManager(app)

DB = DBHelper()

def get_current_ac(data=None):
  if data['Volt'] is not "0" and data['Watt'] is not "0":
    tmp1 = str(data['Watt'])
    if tmp1 != "" and tmp1 != "0":
      return (float(data['Watt'])/float(data['Volt']))
    else: 
      return (0)

def get_inverter_input(data=None):
  if data['Watt'] != "0" and data['Watt'] != "":
    return (float(data['Watt'])/0.85)
  else:
    return (0)

def get_current(power=None,volt=None):
  if power > 0:
    if volt > 0:
      return (float(power)/float(volt))
  return(0)

def get_sla_discharge_capacity(capacity=None):
  if capacity :
    return(float(capacity)*0.8)
  else:
   return (0)

def get_time_cap_amp(capacity=None,current=None,factor=None):
  if capacity > 0:
    if current > 0:
      time_dec=float(capacity)/float(current) 
      if factor:
        if time_dec >= 19.0:
          time_dec = time_dec
        elif time_dec >= 18.0:
          time_dec = time_dec*0.99
        elif time_dec >= 10.0:
          time_dec = time_dec*0.98
        elif time_dec >=5.0:
          time_dec = time_dec*0.8
        else:
          time_dec = time_dec*0.6
      time_text = get_min_dec(time_dec)
      return(time_text)

def get_min_dec(decimal=None):
  if decimal:
     t1 = int(decimal)
     t2 = decimal - t1
     t3 = int(t2 * 60)
     time_text = "%ih:%imin"%(t1,t3)
     return(time_text)
  else:
    return(0)  

@login_manager.user_loader
def load_user(user_id):
  user_password = DB.get_user(user_id)
  if user_password:
    return User(user_id)



@app.route("/")
def home():
  return render_template("index.html")

@app.route("/account")
@login_required
def account():
  return "You are logged in"

@app.route("/login",methods=["POST"])
def login():
  email = request.form.get("email")
  password = request.form.get("password")
  user_password = DB.get_user(email)
  if user_password and user_password == password:
    user = User(email)
    login_user(user, remember=True)
    return redirect(url_for('account'))
  return account() 
 # return home() 

@app.route("/logout")
def logout():
  logout_user()
  return redirect(url_for("home"))

@app.route("/solar")
def solar(vacDic=None):
  try:
    vacDic
  except NameError:
    vacDic = None
  if vacDic: 
    vacDic['Ampere'] = round(get_current_ac(vacDic),2)
    if str(vacDic['Ampere']) == "0.0":
      #print vacDic['Ampere']
      return render_template("solar.html",power=0,voltage=0,ampere=0,powerdc=0,currentdc=0,battcap=0,battcap80=0,
time80=0,timeHighAmp=0,alert=0)
    vacDic['Wattdc'] = round(get_inverter_input(vacDic),2)
    vacDic['Amperedc'] = round(get_current(vacDic['Wattdc'],12),2)
    vacDic['BattCap80'] = round(get_sla_discharge_capacity(vacDic['BattCap']),2)
    vacDic['Time80'] = get_time_cap_amp(vacDic['BattCap80'],vacDic['Amperedc'])
    vacDic['TimeHighAmp'] = get_time_cap_amp(vacDic['BattCap80'],vacDic['Amperedc'],0.6)
    return render_template("solar.html",power=vacDic['Watt'],voltage=vacDic['Volt'],
ampere=vacDic['Ampere'],powerdc=vacDic['Wattdc'],currentdc=vacDic['Amperedc'],battcap=vacDic['BattCap'],battcap80=vacDic['BattCap80'],time80=vacDic['Time80'],timeHighAmp=vacDic['TimeHighAmp'],alert=1)
  else:
    return render_template("solar.html",power=0,voltage=0,ampere=0,powerdc=0,currentdc=0,battcap=0,battcap80=0,
time80=0,timeHighAmp=0,alert=0)


@app.route("/calculate",methods=["POST"])
def add():
  wattVAC = request.form.get("wattVac")
 # if wattVAC.isspace():
 #   wattVAC = 0
  voltVAC = request.form.get("voltageVac")
  batCap = request.form.get("batteryCap")
 # if batCap.isspace():
 #   batCap = 0
  vacDic={'Watt':wattVAC,'Volt':voltVAC,'BattCap':batCap}
  return solar(vacDic)


if __name__ == '__main__':
  app.run(port=5000,debug=True)
