import sqlite3 as sql
from flask import Flask,render_template,request,redirect,url_for,session
from SQL_execute import GetData

app = Flask(__name__)
app.secret_key = 'project24'

@app.route('/')
def index():

    # TODO - Add Images in database
    products = GetData('SELECT * FROM products ORDER BY RANDOM() LIMIT 5');

    logged = False
    username = ""

    if 'username' in session:
        logged = True;
        username = session['username']

    return render_template('index.html', products = products, logged = logged, username= username)

''' Allows user to login, nothing else for now '''
@app.route('/login',methods = ['POST','GET'])
def login():
    if request.method == 'GET':
        return render_template('login.html',logged = False)
    else:
        try:
            enteredPassword = request.form['password']
            userEmail = request.form['email']

            con = sql.connect('products.db')
            con.row_factory = sql.Row

            cur = con.cursor()
            data = cur.execute('SELECT * FROM user WHERE email=?',(userEmail,))
            data = data.fetchall()

            storedPassword = data[0]['password']
            username = data[0]['name']

            con.close()

            if enteredPassword == storedPassword:
                session['username'] = username
                return redirect(url_for('index'))

            else:
                return render_template('welcome_user.html',msg = "wrong password!", a_user = False)
        except TypeError as es:
            #print(es)
            return render_template('welcome_user.html',msg = "New User?", a_user = False)

@app.route('/register', methods = ['POST', 'GET'])
def register():
    if request.method == 'GET':
        return render_template('register.html')

    else:
        try:
            name = request.form['name']
            email = request.form['email']
            password = request.form['password']
            confirmPassword = request.form['confirmPassword']

            # TODO - Values should not be null
            # TODO - validate if passwords are same
            # TODO - Hash the password

            with sql.connect("products.db") as con:
                cur = con.cursor()
                cur.execute("INSERT INTO user (name,email,password) VALUES (?,?,?)",(name,email,password))
                con.commit()
                msg = "Record successfully added"
                registered = True
        except:
            con.rollback()
            msg = "Error in insert operation"

        finally:
            con.close()
            if registered:
                session['username'] = name
                return redirect(url_for('index'))

            return render_template('result.html', msg = msg)
            #TODO - Differentiate Admins and user by radiobutton

@app.route('/customerCare')
def customerCare():
    return render_template('customerCare.html')

''' Only for admins '''
@app.route('/samsung')
def samsung():
    samsung = GetData('SELECT * FROM products where brand="samsung"');
    return render_template('samsung.html', products = samsung)

@app.route('/redmi')
def redmi():
    redmi = GetData('SELECT * FROM products where brand="Redmi"');
    return render_template('redmi.html', products = redmi)


@app.route('/apple')
def apple():
    apple = GetData('SELECT * FROM products where brand="Apple"');
    return render_template('apple.html', products = apple)



@app.route('/listUsers')
def listUsers():
    con = sql.connect('products.db')
    con.row_factory = sql.Row

    cur = con.cursor()
    cur.execute('SELECT * FROM user')

    rows = cur.fetchall()
    return render_template('listUsers.html', rows = rows)

@app.route('/searchResult',methods=["POST"])
def search():
    searchQ=request.form['searchbox']
    if not searchQ:
        return render_template('search.html',found = False)

    con = sql.connect('products.db')
    con.row_factory = sql.Row

    cur = con.cursor()
    cur.execute('SELECT * FROM products WHERE name LIKE ? OR brand LIKE ?',("%"+searchQ+"%","%"+searchQ+"%"))

    products = cur.fetchall()
    con.close()
    if products == None:
        found = False;
    else :
        found = True;
    return render_template('search.html',products = products, found = found)

@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('username', None)
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)
