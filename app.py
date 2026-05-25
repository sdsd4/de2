from flask import Flask, request, session, redirect, render_template
import pymysql
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key='secret'
def db(sql, args=None, fetch=False):
    with pymysql.connect(user='root', password='', database='korochki2', host='localhost', 
                         cursorclass=pymysql.cursors.DictCursor, charset='utf8') as conn:
        cur = conn.cursor()
        cur.execute(sql, args or ())
        if not fetch: conn.commit()
        return cur.fetchall() if fetch else None

if not db("SELECT 1 FROM users WHERE login='Admin' LIMIT 1", fetch=True):
    db("INSERT INTO users VALUES (NULL, %s, SHA2(%s, 256), %s, %s, %s, %s)",
       ("Admin", "KorokNET", "Administrator", "000", "admin@local", "admin"))

@app.route('/', methods = ['GET', 'POST'])
def main():
    p = request.args.get('page', 'login')
    if p == 'logout':
        session.clear()
        return redirect('/?page=login')
    if request.method=='POST':
        if p == 'register':
            db("INSERT INTO users (login, password, fio, phone, email, role) VALUES (%s, SHA2(%s,256), %s, %s, %s, 'user')",
               (request.form['login'], request.form['password'], request.form['fio'], request.form['phone'], request.form['email']))
            return render_template('msg.html', m="Вы зарегистрированы", l='/?page=login', t="Войти")
        if p == 'login':
            u = db('SELECT * FROM users WHERE login=%s AND password=SHA2(%s,256)',
               (request.form['login'], request.form['password']), fetch=True)
            u = u[0] if u else None
            if u:
                session.update(id=u['id'], role=u['role'])
                if u['role']=='admin':
                    return redirect('/?page=admin')
                else: return redirect('/?page=dashboard')
        if p == 'create' and 'id' in session:
            db("INSERT INTO requests (user_id,course,date,payment,status) VALUES (%s,%s,%s,%s,'Новая')",
               (session['id'], request.form['course'], request.form['date'], request.form['payment']))
            return render_template('msg.html', m="Заявка отправлена!", l="/?page=my", t="Перейти в мои заявки")
        if p == 'my' and 'id' in session and 'request_id' in request.form:
            db("INSERT INTO reviews (user_id,request_id,text) VALUES (%s,%s,%s)",
            (session['id'], request.form['request_id'], request.form['text']))
            return redirect('/?page=my') 
        
    if p=='register':
        return render_template('register.html')
    if p=='login':
        return render_template('login.html')
    if p=='dashboard':
        return render_template('dashboard.html')
    if p=='create':
        return render_template('create.html')
    if p == 'my':
        r = db("SELECT * FROM requests WHERE user_id=%s", (session['id'],), fetch=True)
        return render_template('my.html', r=r)
    if p=='admin' and session.get('role')=='admin':
        if 'id' in request.args: db("UPDATE requests SET status=%s WHERE id=%s", (request.args['status'], request.args['id']))
        return render_template('admin.html', 
                               r=db("SELECT requests.*, users.fio FROM requests JOIN users ON requests.user_id = users.id", 
                                    fetch=True))
    
    return redirect('/?page=login')
if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, port=5001)