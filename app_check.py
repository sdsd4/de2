from flask import Flask
import pymysql

app = Flask(__name__)
app.secret_key = 'secret'

def check_db():
    try:
        conn = pymysql.connect(host='localhost', port=3306, user='root', password='', database='korochki2', 
                         cursorclass=pymysql.cursors.DictCursor, charset='utf8')
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
        conn.close()
        return "БД ок"
    except Exception as e:
        return f"Ошибка БД: {e}"

@app.route('/')
def index():
    status = check_db()
    return f"Сайт ок<p>{status}</p>"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)