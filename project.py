import sqlite3 as sql
from functools import wraps
from flask import Flask,render_template,request,redirect,url_for,session,jsonify
from SQL_execute import GetData, dict_factory
from passlib.apps import custom_app_context as passHash

app = Flask(__name__)

app.secret_key = 'project24'
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
admins = ['maulik','harsh','suprit']

def login_required(f):
    @wraps(f)
    def fn(*args,**kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args,**kwargs)
    return fn

def check_admin(username):
    for admin in admins:
        if username == admin:
            return True
    return False

@app.route('/')
def index():
    products = GetData('SELECT * FROM products ORDER BY RANDOM() LIMIT 5');

    logged = False
    username = ""

    if 'username' in session:
        logged = True;
        username = session['username']

    return render_template('index.html', products = products, logged = logged, username= username)

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
            data = cur.execute('SELECT * FROM user WHERE email=?',(userEmail,))
            data = data.fetchall()

            storedPassword = data[0]['password'] #Throws IndexError if no entry is found
            username = data[0]['name']

            con.close()

            if passHash.verify(enteredPassword,storedPassword):
                session['username'] = username
                return redirect(url_for('index'))

            else:
                return render_template('login.html',wrongPassword = True,userNotFound=False)

        except IndexError as es:
            #print(es)
            return render_template('login.html',userNotFound = True,wrongPassword=False)

@app.route('/register', methods = ['POST', 'GET'])
def register():
    if request.method == 'GET':
        return render_template('register.html')

    else:
        try:
            name = request.form['name']
            email = request.form['email']
            password = passHash.hash(request.form['password'])
            confirmPassword = request.form['confirmPassword']

            # TODO - Values should not be null
            #      - Done by Jscript
            # TODO - validate if passwords are same

            with sql.connect("products.db") as con:
                con.row_factory = dict_factory
                cur = con.cursor()

                cur.execute("SELECT * FROM user WHERE name=? OR email=?",(name,email))
                users = cur.fetchall()
                print(users)

                if users:
                    print("already!")
                    registered = False
                    alreadyUser = True

                else:
                    cur.execute("INSERT INTO user (name,email,password) VALUES (?,?,?)",(name,email,password))
                    con.commit()
                    msg = "Record successfully added"
                    registered = True
                    alreadyUser = False
        except:
            con.rollback()
            msg = "Error in insert operation"

        finally:
            con.close()
            if registered:
                session['username'] = name
                return redirect(url_for('index'))

            elif alreadyUser:
                return render_template('register.html',alreadyUser = True)
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

@app.route('/Cart/<name>/<storage>')
@login_required
def Cart(name,storage):
    username=session['username']
    productname=name
    productstorage=storage
    con = sql.connect('products.db')
    con.row_factory = dict_factory
    cur = con.cursor()

    #If item is already present in cart
    cur2 = con.cursor()
    ret = cur2.execute('SELECT * FROM cart WHERE (username=? AND productname=? AND storage=?)',(username,productname,productstorage))
    ret = ret.fetchall()
    if ret:
        return redirect(url_for('CartDisplay'))

    cur.execute('INSERT INTO cart(username,productname,storage) VALUES(?,?,?)', (username,productname,productstorage))
    con.commit()
    con.close()
    return redirect(url_for('CartDisplay'))


@app.route('/rmCart/<name>/<storage>')
@login_required
def rmCart(name,storage):
    username=session['username']
    productname=name
    productstorage=storage
    con = sql.connect('products.db')
    con.row_factory = dict_factory
    cur = con.cursor()
    cur.execute('DELETE FROM cart WHERE username=? AND productname=? AND storage=?', (username,productname,productstorage))
    con.commit()
    con.close()
    return redirect(url_for('CartDisplay'))

@app.route('/CartDisplay')
@login_required
def CartDisplay():
    username=session['username']
    con = sql.connect('products.db')
    con.row_factory = sql.Row
    cur = con.cursor()
    acart = cur.execute('SELECT * FROM cart WHERE username=?',(username,))
    acart = acart.fetchall()
    aproduct=GetData('SELECT * FROM products');
    cart=list()
    for i in acart:
        for j in aproduct:
            if (i["productname"]==j["name"] and i["storage"]==j["storage"]):
                cart.append(j)
    return render_template('cartdisplay.html', products = cart, logged = True, username= username)

@app.route('/buyProduct/<name>/<storage>')
@login_required
def buyProduct(name,storage):
    username=session['username']
    productname=name
    productstorage=storage
    con=sql.connect('products.db')
    con.row_factory=dict_factory
    cur=con.cursor()
    cur.execute('SELECT * FROM productsold WHERE name=? AND storage=?',(name,storage,))
    dbdict=cur.fetchall()
    dbaddname=productname
    dbaddstorage=productstorage
    dbaddnumber=dbdict[0]["numberofproductssold"]+1
    cur.execute('INSERT INTO userreport(username,productname,productstorage) VALUES(?,?,?)',(username,productname,productstorage))
    cur.execute('DELETE FROM productsold WHERE name=? AND storage=?', (name,storage,))
    cur.execute('INSERT INTO productsold(name,storage,numberofproductssold) VALUES(?,?,?)', (dbaddname,dbaddstorage,dbaddnumber))
    con.commit()
    con.close()
    con = sql.connect('products.db')
    con.row_factory = dict_factory
    cur = con.cursor()
    cur.execute('DELETE FROM cart WHERE username=? AND productname=? AND storage=?', (username,productname,productstorage))
    con.commit()
    con.close()
    return

@app.route('/reportNoOfProductsSold')
@login_required
def reportNoOfProductsSold():
    username=session["username"]

    is_admin = check_admin(username)
    if is_admin == False:
        return render_template('reportNoOfProductsSold.html',not_admin=True)

    con=sql.connect('products.db')
    con.row_factory=dict_factory
    cur=con.cursor()
    cur.execute('SELECT * FROM productsold')
    lis=cur.fetchall()
    return render_template('reportNoOfProductsSold.html', rows=lis, logged=True, username=username)

@app.route('/userReport')
@login_required
def userReport():
    username=session["username"]

    is_admin = check_admin(username)
    if is_admin == False:
        return render_template('reportNoOfProductsSold.html',not_admin=True)

    con=sql.connect('products.db')
    con.row_factory=dict_factory
    cur=con.cursor()
    cur.execute('SELECT * FROM userreport')
    lis=cur.fetchall()
    return render_template('userReport.html', rows=lis, logged=True, username=username)


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
