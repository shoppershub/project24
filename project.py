import sqlite3 as sql
from functools import wraps
from flask import Flask,render_template,request,redirect,url_for,session,jsonify
from SQL_execute import GetData, dict_factory

app = Flask(__name__)
app.secret_key = 'project24'

def login_required(f):
    @wraps(f)
    def fn(*args,**kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args,**kwargs)
    return fn

@app.route('/')
def index():
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

@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/listUsers')
@login_required
def listUsers():
    con = sql.connect('products.db')
    con.row_factory = sql.Row

    cur = con.cursor()
    cur.execute('SELECT * FROM user')

    rows = cur.fetchall()
    return render_template('listUsers.html', rows = rows)

@app.route('/search',methods=["POST","GET"])
def search():
    if request.method == "POST":
        searchQ=request.form['searchbox']
        if not searchQ:
            return render_template('search.html',found = False)

        con = sql.connect('products.db')
        con.row_factory = sql.Row

        cur = con.cursor()
        cur.execute('SELECT * FROM products WHERE name LIKE ? OR brand LIKE ?',("%"+searchQ+"%","%"+searchQ+"%"))

        products = cur.fetchall()
        con.close()

        if products == [] :
            found = False;
        else :
            found = True;
        return render_template('search.html',products = products, found = found)
    else:
        q = request.args.get('q') + "%"
        con = sql.connect('products.db')
        con.row_factory = dict_factory

        cur = con.cursor()
        cur.execute('SELECT * FROM products WHERE name LIKE ? OR brand LIKE ?',(q,q))

        products = cur.fetchall()
        con.close()

        return jsonify(products)

@app.route('/productInfo/<name>/<storage>')
def productInfo(name,storage):
    print(name)

    con = sql.connect('products.db')
    con.row_factory = sql.Row

    cur = con.cursor()
    cur.execute('SELECT * FROM products WHERE name = ? AND storage = ? ',(name,storage))

    products = cur.fetchall()
    con.close()
    logged = False
    username = ""

    if 'username' in session:
        logged = True;
        username = session['username']
    return render_template('productInfo.html',products = products, logged = logged, username= username)

@app.route('/customerCare')
def customerCare():

    return render_template('customerCare.html')

''' Only for admins '''
@app.route('/samsung')
def samsung():
    samsung = GetData('SELECT * FROM products where brand="samsung"');
    logged = False
    username = ""

    if 'username' in session:
        logged = True;
        username = session['username']
    return render_template('samsung.html', products = samsung, logged = logged, username= username)

@app.route('/redmi')
def redmi():
    redmi = GetData('SELECT * FROM products where brand="Redmi"');
    logged = False
    username = ""

    if 'username' in session:
        logged = True;
        username = session['username']
    return render_template('redmi.html', products = redmi, logged = logged, username= username)


@app.route('/apple')
def apple():
    apple = GetData('SELECT * FROM products where brand="Apple"');
    logged = False
    username = ""

    if 'username' in session:
        logged = True;
        username = session['username']
    return render_template('apple.html', products = apple, logged = logged, username= username)

@app.route('/applebelow32gb')
def applebelow32gb():
    apple = GetData('SELECT * FROM products where brand="Apple"');
    below64gb=list()
    for product in apple:
        s=product["storage"]
        st=s[0:-2]
        if int(st)<=32:
            below64gb.append(product)
    logged = False
    username = ""

    if 'username' in session:
        logged = True;
        username = session['username']
    return render_template('apple.html', products = below64gb, logged = logged, username= username)

@app.route('/apple32gb64gb')
def apple32gb64gb():
    apple = GetData('SELECT * FROM products where brand="Apple"');
    logged = False
    username = ""

    if 'username' in session:
        logged = True;
        username = session['username']
    below64gb=list()
    for product in apple:
        s=product["storage"]
        st=s[0:-2]
        if int(st)>32 and int(st)<=64:
            below64gb.append(product)
    return render_template('apple.html', products = below64gb, logged = logged, username= username)

@app.route('/apple64gb256gb')
def apple64gb256gb():
    apple = GetData('SELECT * FROM products where brand="Apple"');
    logged = False
    username = ""

    if 'username' in session:
        logged = True;
        username = session['username']
    below64gb=list()
    for product in apple:
        s=product["storage"]
        st=s[0:-2]
        if int(st)>64 and int(st)<=256:
            below64gb.append(product)
    
    return render_template('apple.html', products = below64gb, logged = logged, username= username)

@app.route('/samsungbelow32gb')
def samsungbelow32gb():
    apple = GetData('SELECT * FROM products where brand="samsung"');
    below64gb=list()
    for product in apple:
        s=product["storage"]
        st=s[0:-2]
        if int(st)<=32:
            below64gb.append(product)
    logged = False
    username = ""

    if 'username' in session:
        logged = True;
        username = session['username']
    return render_template('samsung.html', products = below64gb, logged = logged, username= username)

@app.route('/samsung32gb64gb')
def samsung32gb64gb():
    apple = GetData('SELECT * FROM products where brand="samsung"');
    below64gb=list()
    for product in apple:
        s=product["storage"]
        st=s[0:-2]
        if int(st)>32 and int(st)<=64:
            below64gb.append(product)
    logged = False
    username = ""

    if 'username' in session:
        logged = True;
        username = session['username']
    return render_template('samsung.html', products = below64gb, logged = logged, username= username)

@app.route('/samsung64gb256gb')
def samsung64gb256gb():
    apple = GetData('SELECT * FROM products where brand="samsung"');
    below64gb=list()
    for product in apple:
        s=product["storage"]
        st=s[0:-2]
        if int(st)>64 and int(st)<=256:
            below64gb.append(product)
    logged = False
    username = ""

    if 'username' in session:
        logged = True;
        username = session['username']
    return render_template('samsung.html', products = below64gb, logged = logged, username= username)
@app.route('/redmibelow32gb')
def redmibelow32gb():
    apple = GetData('SELECT * FROM products where brand="Redmi"');
    below64gb=list()
    for product in apple:
        s=product["storage"]
        st=s[0:-2]
        if int(st)<=32:
            below64gb.append(product)
    logged = False
    username = ""

    if 'username' in session:
        logged = True;
        username = session['username']
    return render_template('redmi.html', products = below64gb, logged = logged, username= username)

@app.route('/redmi32gb64gb')
def redmi32gb64gb():
    apple = GetData('SELECT * FROM products where brand="Redmi"');
    below64gb=list()
    for product in apple:
        s=product["storage"]
        st=s[0:-2]
        if int(st)>32 and int(st)<=64:
            below64gb.append(product)
    logged = False
    username = ""

    if 'username' in session:
        logged = True;
        username = session['username']
    return render_template('redmi.html', products = below64gb, logged = logged, username= username)

@app.route('/redmi64gb256gb')
def redmi64gb256gb():
    apple = GetData('SELECT * FROM products where brand="Redmi"');
    below64gb=list()
    for product in apple:
        s=product["storage"]
        st=s[0:-2]
        if int(st)>64 and int(st)<=256:
            below64gb.append(product)
    logged = False
    username = ""

    if 'username' in session:
        logged = True;
        username = session['username']
    return render_template('redmi.html', products = below64gb, logged = logged, username= username)

@app.route('/samsbp')
def samsbp():
    samsort=GetData('SELECT * FROM products WHERE brand="samsung"')
    samprice=list()
    samsorted=list()
    for product in samsort:
        x=product["price"]
        samprice.append(int(x))

    samprice.sort()
    for i in range(0,len(samprice)-1):
        if samprice[i]==samprice[i+1]:
            samprice[i]=0
    for price in samprice:
        for y in samsort:
            if price==y["price"]:
                samsorted.append(y)
    logged = False
    username = ""

    if 'username' in session:
        logged = True;
        username = session['username']
    return render_template('samsung.html',products=samsorted, logged = logged, username= username)

@app.route('/samsbs')
def samsbs():
    samsort=GetData('SELECT * FROM products WHERE brand="samsung"')
    logged = False
    username = ""

    if 'username' in session:
        logged = True;
        username = session['username']
    samsorted=list()
    for product in samsort:
        x=product["storage"]
        if x=="32GB":
            samsorted.append(product)
    for product in samsort:
        x=product["storage"]
        if x=="64GB":
            samsorted.append(product)
    for product in samsort:
        x=product["storage"]
        if x=="256GB":
            samsorted.append(product)


    return render_template('samsung.html',products=samsorted, logged = logged, username= username)

@app.route('/redmisbp')
def redmisbp():
    samsort=GetData('SELECT * FROM products WHERE brand="Redmi"')
    logged = False
    username = ""

    if 'username' in session:
        logged = True;
        username = session['username']
    samprice=list()
    samsorted=list()
    for product in samsort:
        x=product["price"]
        samprice.append(int(x))
    samprice.sort()
    for i in range(0,len(samprice)-1):
        if samprice[i]==samprice[i+1]:
            samprice[i]=0
    for price in samprice:
        for y in samsort:
            if price==y["price"]:
                samsorted.append(y)
    return render_template('redmi.html',products=samsorted, logged = logged, username= username)

@app.route('/redmisbs')
def redmisbs():
    samsort=GetData('SELECT * FROM products WHERE brand="Redmi"')
    logged = False
    username = ""

    if 'username' in session:
        logged = True;
        username = session['username']
    samsorted=list()
    for product in samsort:
        x=product["storage"]
        if x=="32GB":
            samsorted.append(product)
    for product in samsort:
        x=product["storage"]
        if x=="64GB":
            samsorted.append(product)
    for product in samsort:
        x=product["storage"]
        if x=="256GB":
            samsorted.append(product)


    return render_template('redmi.html',products=samsorted, logged = logged, username= username)

@app.route('/applesbp')
def applesbp():
    samsort=GetData('SELECT * FROM products WHERE brand="Apple"')
    logged = False
    username = ""

    if 'username' in session:
        logged = True;
        username = session['username']
    samprice=list()
    samsorted=list()
    for product in samsort:
        x=product["price"]
        samprice.append(int(x))
    samprice.sort()
    for i in range(0,len(samprice)-1):
        if samprice[i]==samprice[i+1]:
            samprice[i]=0
    for price in samprice:
        for y in samsort:
            if price==y["price"]:
                samsorted.append(y)
    return render_template('apple.html',products=samsorted, logged = logged, username= username)

@app.route('/applesbs')
def applesbs():
    samsort=GetData('SELECT * FROM products WHERE brand="Apple"')
    logged = False
    username = ""

    if 'username' in session:
        logged = True;
        username = session['username']
    samsorted=list()
    for product in samsort:
        x=product["storage"]
        if x=="32GB":
            samsorted.append(product)
    for product in samsort:
        x=product["storage"]
        if x=="64GB":
            samsorted.append(product)
    for product in samsort:
        x=product["storage"]
        if x=="256GB":
            samsorted.append(product)


    return render_template('apple.html',products=samsorted, logged = logged, username= username)


if __name__ == "__main__":
    app.run(debug=True)
