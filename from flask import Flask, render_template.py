from flask import Flask, render_template, request, redirect, session
import psycopg2
import os

app = Flask(**name**)
app.secret_key = "change_this_key"

# ---------------- DB CONNECTION ----------------

def get_db():
return psycopg2.connect(os.environ["DATABASE_URL"])

# ---------------- INIT DB ----------------

def init_db():
conn = get_db()
cur = conn.cursor()

```
cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE,
    password TEXT,
    balance FLOAT DEFAULT 1000
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS transactions (
    id SERIAL PRIMARY KEY,
    sender TEXT,
    receiver TEXT,
    amount FLOAT
)
""")

conn.commit()
conn.close()
```

init_db()

# ---------------- HOME ----------------

@app.route("/")
def home():
if "user" not in session:
return redirect("/login")

```
conn = get_db()
cur = conn.cursor()

cur.execute("SELECT balance FROM users WHERE username=%s", (session["user"],))
balance = cur.fetchone()[0]

cur.execute("SELECT sender, receiver, amount FROM transactions ORDER BY id DESC")
transactions = cur.fetchall()

conn.close()

return render_template(
    "dashboard.html",
    user=session["user"],
    balance=balance,
    transactions=transactions
)
```

# ---------------- REGISTER ----------------

@app.route("/register", methods=["GET", "POST"])
def register():
if request.method == "POST":
username = request.form["username"]
password = request.form["password"]

```
    conn = get_db()
    cur = conn.cursor()

    try:
        cur.execute(
            "INSERT INTO users(username, password) VALUES(%s, %s)",
            (username, password)
        )
        conn.commit()
    except:
        pass

    conn.close()
    return redirect("/login")

return render_template("register.html")
```

# ---------------- LOGIN ----------------

@app.route("/login", methods=["GET", "POST"])
def login():
if request.method == "POST":
username = request.form["username"]
password = request.form["password"]

```
    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM users WHERE username=%s AND password=%s",
        (username, password)
    )

    user = cur.fetchone()
    conn.close()

    if user:
        session["user"] = username
        return redirect("/")

return render_template("login.html")
```

# ---------------- LOGOUT ----------------

@app.route("/logout")
def logout():
session.clear()
return redirect("/login")

# ---------------- SEND MONEY ----------------

@app.route("/send", methods=["POST"])
def send():
if "user" not in session:
return redirect("/login")

```
sender = session["user"]
receiver = request.form["receiver"]
amount = float(request.form["amount"])

if amount <= 0 or sender == receiver:
    return redirect("/")

conn = get_db()
cur = conn.cursor()

# check sender
cur.execute("SELECT balance FROM users WHERE username=%s", (sender,))
sender_data = cur.fetchone()
if not sender_data:
    conn.close()
    return redirect("/")

balance = sender_data[0]

# check receiver
cur.execute("SELECT balance FROM users WHERE username=%s", (receiver,))
if not cur.fetchone():
    conn.close()
    return redirect("/")

if balance >= amount:
    cur.execute(
        "UPDATE users SET balance = balance - %s WHERE username=%s",
        (amount, sender)
    )

    cur.execute(
        "UPDATE users SET balance = balance + %s WHERE username=%s",
        (amount, receiver)
    )

    cur.execute(
        "INSERT INTO transactions(sender, receiver, amount) VALUES(%s, %s, %s)",
        (sender, receiver, amount)
    )

    conn.commit()

conn.close()
return redirect("/")
```

# ---------------- RUN ----------------

if **name** == "**main**":
app.run()
