import sqlite3 as sql
from flask import Flask,render_template,request
from SQL_execute import GetData

app = Flask(__name__)

@app.route('/')
def index():
    # TODO - Add Images in database
    
    con = sql.connect('products.db')
    con.row_factory = sql.Row
        
    cur = con.cursor()
    ret = cur.execute('SELECT * FROM img')
    img = ret.fetchone()[0] #Might throw error
    
    con.close()

    products = GetData('SELECT * FROM products');
    return render_template('index.html', products = products, imgPath = img)

''' Allows user to login, nothing else for now '''
@app.route('/login',methods = ['POST','GET'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        try:
            enteredPassword = request.form['password']
            userEmail = request.form['email']

            con = sql.connect('products.db')
            con.row_factory = sql.Row

            cur = con.cursor()
            ret = cur.execute('SELECT password FROM user WHERE email=?',(userEmail,))
            storedPassword = ret.fetchone()[0] #Might throw error

            con.close()
            if enteredPassword == storedPassword:
                return render_template('welcome_user.html',msg = "Welcome back " + userEmail, a_user = True)
            else:
                return render_template('welcome_user.html',msg = "wrong password!", a_user = False)
        except TypeError:
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
        except:
            con.rollback()
            msg = "Error in insert operation"

        finally:
            con.close()
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

if __name__ == "__main__":
    app.run(debug=True)
