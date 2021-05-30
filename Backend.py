from flask import Flask, render_template, request, session, redirect
from datetime import datetime
import sqlite3
import json
import pytz

app = Flask(__name__, template_folder="./")
app.config['SECRET_KEY'] = 'Secret'
IST = pytz.timezone('Asia/Kolkata')


class commonVar:
    key = ['asdf1234']
    fanStat = False
    lightStat = False
    door = False
    auto = False
    l1 = []
    l2 = []
    l3 = []


@app.route("/", methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template("login.html")
    if request.method == 'POST':
        password = request.form['password']
        username = request.form['username']
        conn = sqlite3.connect('data.db')
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username=" + '"' + username + '"')
        data = cur.fetchall()
        try:
            if password == data[0][1]:
                session['username'] = data[0][0]
                cur.close()
                conn.close()
                return redirect('/home')
            else:
                cur.close()
                conn.close()
                return render_template('login.html', msg="Username/Password is wrong")
        except IndexError:
            conn.close()
            cur.close()
            return render_template('login.html', msg="Username/Password is wrong")


@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('signup.html')
    if request.method == 'POST':
        username = request.form['username']
        password1 = request.form['password1']
        password2 = request.form['password2']
        key = request.form['key']
        conn = sqlite3.connect('data.db')
        cur = conn.cursor()
        if key in commonVar.key:
            if password1 == password2:
                cur.execute("CREATE TABLE IF NOT EXISTS users(username TEXT PRIMARY KEY, password TEXT)")
                values = "('" + username + "','" + password1 + "')"
                try:
                    cur.execute("INSERT INTO users VALUES" + values)
                    conn.commit()
                    return render_template("login.html", msg="Account creation successful. Login to continue.")
                except sqlite3.IntegrityError:
                    return render_template("signup.html", msg="Username already exists")
            else:
                return render_template("signup.html", msg="Passwords do not match")
        else:
            return render_template("signup.html", msg="Invalid key")


@app.route('/home', methods=['GET', 'POST'])
def home():
    if request.method == 'GET':
        conn = sqlite3.connect('data.db')
        cur = conn.cursor()
        cur.execute("SELECT * FROM history")
        data = cur.fetchall()
        cur.close()
        conn.close()
        commonVar.l1 = []
        commonVar.l2 = []
        commonVar.l3 = []
        for i in range(0, len(data)):
            commonVar.l1.append(data[i][0])
            commonVar.l2.append(data[i][1])
            commonVar.l3.append(data[i][2])
        return render_template('home.html', user=session['username'], humid=commonVar.l1,
                               temp=commonVar.l2, time=commonVar.l3)
    if request.method == 'POST':
        but = request.form['test']
        if but == "Fan":
            if commonVar.fanStat:
                commonVar.fanStat = False
                return render_template('home.html', user=session['username'], humid=commonVar.l1,
                                       temp=commonVar.l2, time=commonVar.l3, out1="The fan is now off")
            else:
                commonVar.fanStat = True
                return render_template('home.html', user=session['username'], humid=commonVar.l1,
                                       temp=commonVar.l2, time=commonVar.l3, out1="The fan is now on")
        elif but == "Light":
            if commonVar.lightStat:
                commonVar.lightStat = False
                return render_template('home.html', user=session['username'], humid=commonVar.l1,
                                       temp=commonVar.l2, time=commonVar.l3, out2="The light is now off")
            else:
                commonVar.lightStat = True
                return render_template('home.html', user=session['username'], humid=commonVar.l1,
                                       temp=commonVar.l2, time=commonVar.l3, out2="The light is now on")
        elif but == "Auto":
            if commonVar.auto:
                commonVar.auto = False
                return render_template('home.html', user=session['username'], humid=commonVar.l1,
                                       temp=commonVar.l2, time=commonVar.l3, out4="Automatic mode disabled")
            else:
                commonVar.auto = True
                return render_template('home.html', user=session['username'], humid=commonVar.l1,
                                       temp=commonVar.l2, time=commonVar.l3, out4="Automatic mode enabled")
        elif but == "Door":
            commonVar.door = True
            return render_template('home.html', user=session['username'], humid=commonVar.l1,
                                   temp=commonVar.l2, time=commonVar.l3, out3="Opening door")


@app.route('/dataDump', methods=['GET', 'POST'])
def dataDump():
    if request.method == 'GET':
        if commonVar.door:
            commonVar.door = False
            conn = sqlite3.connect("data.db")
            cur = conn.cursor()
            now = datetime.now(IST)
            timestamp = now.strftime("%d/%m/%Y %H:%M:%S")
            cur.execute("CREATE TABLE IF NOT EXISTS door(timestamp TEXT PRIMARY KEY)")
            cur.execute("INSERT INTO door VALUES('" + timestamp + "')")
            conn.commit()
            cur.close()
            conn.close()
            x = {"Fan": commonVar.fanStat, "Light": commonVar.lightStat, "Auto": commonVar.auto, "Door": True}
            return json.dumps(x)
        else:
            x = {"Fan": commonVar.fanStat, "Light": commonVar.lightStat, "Auto": commonVar.auto, "Door": False}
            return json.dumps(x)
    if request.method == 'POST':
        content = request.get_json()
        print(content)
        humidity = content['humid']
        temperature = content['temp']
        now = datetime.now()
        timestamp = now.strftime("%d/%m/%Y %H:%M:%S")
        conn = sqlite3.connect('data.db')
        cur = conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS history(humidity REAL, temperature REAL, timestamp TEXT PRIMARY KEY)")
        cur.execute("INSERT INTO history VALUES(" + str(humidity) + ',' + str(temperature) + ',"' + timestamp + '")')
        conn.commit()
        cur.close()
        conn.close()
        return "200"


@app.route('/doorInfo', methods=['GET'])
def doorInfo():
    if request.method == 'GET':
        conn = sqlite3.connect('data.db')
        cur = conn.cursor()
        cur.execute("SELECT * FROM door")
        data = cur.fetchall()
        cur.close()
        conn.close()
        return render_template('door.html', user=session['username'], data=data)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
