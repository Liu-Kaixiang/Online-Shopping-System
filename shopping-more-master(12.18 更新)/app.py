# -*- coding: utf-8 -*-
from flask import Flask
from flask import *
from werkzeug.utils import secure_filename
import pygal
from flask_bootstrap import Bootstrap
from urllib.parse import *
import sqlite3, hashlib, os, time, random
#import oss as oss
import pypyodbc
import config

app = Flask(__name__)
app.secret_key = 'dev'
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = set(['jpeg', 'jpg', 'png', 'gif'])

Bootstrap(app)

def getConnection():
    connection = pypyodbc.connect("Driver= {"+config.DATABASE_CONFIG["Driver"]+"} ;Server=" + config.DATABASE_CONFIG["Server"] + ";Database=" + config.DATABASE_CONFIG["Database"] + ";uid=" + config.DATABASE_CONFIG["UID"] + ";pwd=" + config.DATABASE_CONFIG["Password"])
    return connection

def getLoginDetails():
    with getConnection() as conn:
        cur = conn.cursor()
        if 'email' not in session:
            loggedIn = False
            firstName = ''
            userId_=0
            noOfItems = 0
        else:
            loggedIn = True
            cur.execute("SELECT user_id, username FROM user_inf WHERE email = ?", (session['email'], ))
            userId_, firstName = cur.fetchone()
            cur.execute("SELECT count(goods_id) FROM shopping_cart WHERE user_id = ?", (userId_, ))
            noOfItems = cur.fetchone()[0]
    return (loggedIn, firstName,userId_,noOfItems)

def parse(data):
    ans = []
    i = 0
    while i < len(data):
        curr = []
        for j in range(7):
            if i >= len(data):
                break
            curr.append(data[i])
            i += 1
        ans.append(curr)
    return ans

def is_valid(email, password):
    con = getConnection()
    cur = con.cursor()
    cur.execute('SELECT email, password FROM user_inf')
    data = cur.fetchall()
    for row in data:
        if row[0] == email and row[1] == hashlib.md5(password.encode()).hexdigest():
            return True
    return False

def allowed_file(filename):
    return '.' in filename and \
            filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def redirect_back(default='hello', **kwargs):
    for target in request.args.get('next'), request.referrer:
        if not target:
            continue
        if is_safe_url(target):
            return redirect(target)
    return redirect(url_for(default, **kwargs))

def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc

def random_color():
    colorArr = ['1','2','3','4','5','6','7','8','9','a','b','c','d','e','f']
    color = ""
    for i in range(6):
        color += colorArr[random.randint(0, 14)]
    return "#" + color

@app.route('/')
def root():
    loggedIn, firstName,_,noOfItems = getLoginDetails()
    with getConnection() as conn:
        cur = conn.cursor()
        cur.execute('SELECT goods.goods_id, goods_name, price, goods_describe, image_addr, inventory FROM goods, goods_image, goods_attribute WHERE goods.goods_id=goods_image.goods_id AND goods.goods_id=goods_attribute.goods_id')
        itemData = cur.fetchall()
        # cur.execute('SELECT category_id, category_name FROM category')
        # categoryData = cur.fetchall()
    # if len(itemData) > 9:
    #     itemData = itemData[0:9]
    return render_template('index.html', itemData=itemData, loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems)

@app.route("/goods/<int:goods_id>")
def goods(goods_id):
    loggedIn, firstName,_,noOfItems = getLoginDetails()
    goods_id = request.args.get('goods_id')
    # print(goods_id)
    with getConnection() as conn:
        cur = conn.cursor()
        cur.execute('SELECT goods.goods_id, goods_name, price, goods_describe, image_addr, sales, inventory, discount_rate, discount_deadline FROM goods, goods_image, goods_attribute WHERE goods.goods_id=goods_image.goods_id AND goods.goods_id=goods_attribute.goods_id AND goods.goods_id=?', (goods_id,))
        itemData = cur.fetchall()[0]
        cur.execute('SELECT goods.category_id, category_name FROM category, goods WHERE goods.goods_id=? AND goods.category_id=category.category_id', (goods_id,))
        categoryData = cur.fetchall()[0]
        cur.execute('SELECT shop.shop_id, shop_name FROM shop, goods WHERE goods.goods_id=? AND goods.shop_id=shop.shop_id', (goods_id,))
        shopData = cur.fetchall()[0]
    data = ['王睿之（ID：001）：很棒！','徐瑞泽（ID：002）：还不错！','陈一航（ID：003）：很好用！']
    # print(itemData)
    # print(shopData)
    # print(categoryData)
    if len(data) > 3:
        data = data[0:3]
    return render_template("goods.html", categoryData=categoryData, itemData=itemData, data=data, shopData=shopData, loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems)

@app.route("/store")
def test():
    loggedIn, firstName,userId,noOfItems = getLoginDetails()
    with getConnection() as conn:
        cur = conn.cursor()
        cur.execute('SELECT shop_id, shop_name, address, shop_describe, img, announcement FROM shop ORDER BY shop_id')
        itemData = cur.fetchall()
        #print(itemData[4])
        #print(itemData)
        # cur.execute('SELECT goods.goods_id, goods_name, price, goods_describe, image_addr, inventory FROM goods, goods_image, goods_attribute WHERE goods.goods_id=goods_image.goods_id AND goods.goods_id=goods_attribute.goods_id AND goods.shop_id=?', (shop_id,))
        # goodsData = cur.fetchall()
        # print(goodsData)
        # cur.execute('SELECT shop.shop_id, shop_name FROM shop, goods WHERE goods.goods_id=? AND goods.shop_id=shop.shop_id', (goods_id,))
        # shopData = cur.fetchall()[0]
    return render_template("index_store.html", itemData=itemData, loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems)

@app.route("/store/<int:shop_id>")
def store(shop_id):
    loggedIn, firstName,_,noOfItems = getLoginDetails()
    shop_id = request.args.get('shop_id')
    # print(shop_id)
    with getConnection() as conn:
        cur = conn.cursor()
        cur.execute('SELECT shop_id, shop_name, address, phone, shop_describe, announcement, img, sales FROM shop WHERE shop_id=? ORDER BY sales DESC', (shop_id,))
        itemData = cur.fetchall()[0]
        print(itemData)
        cur.execute('SELECT goods.goods_id, goods_name, price, goods_describe, image_addr, inventory FROM goods, goods_image, goods_attribute WHERE goods.goods_id=goods_image.goods_id AND goods.goods_id=goods_attribute.goods_id AND goods.shop_id=?', (shop_id,))
        categoryData = cur.fetchall()
        maxData = categoryData[0:3]
        # cur.execute('SELECT shop.shop_id, shop_name FROM shop, goods WHERE goods.goods_id=? AND goods.shop_id=shop.shop_id', (goods_id,))
        # shopData = cur.fetchall()[0]
    return render_template("store.html", maxData=maxData, itemData=itemData, categoryData=categoryData, loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems)

@app.route("/add")
def admin():
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT categoryId, name FROM categories")
        categories = cur.fetchall()
    #conn.close()
    return render_template('add.html', categories=categories)

@app.route("/addItem", methods=["GET", "POST"])
def addItem():
    if request.method == "POST":
        name = request.form['name']
        price = float(request.form['price'])
        description = request.form['description']
        stock = int(request.form['stock'])
        categoryId = int(request.form['category'])

        #Uploading image procedure
        image = request.files['image']
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image.save(os.path.join(UPLOAD_FOLDER, filename))
        imagename = filename
        with sqlite3.connect('database.db') as conn:
            try:
                cur = conn.cursor()
                cur.execute('''INSERT INTO products (name, price, description, image, stock, categoryId) VALUES (?, ?, ?, ?, ?, ?)''', (name, price, description, imagename, stock, categoryId))
                conn.commit()
                msg="added successfully"
            except:
                msg="error occured"
                conn.rollback()
        #conn.close()
        print(msg)
        return redirect(url_for('root'))

@app.route("/remove")
def remove():
    with getConnection() as conn:
        cur = conn.cursor()
        cur.execute('SELECT productId, name, price, description, image, stock FROM products')
        data = cur.fetchall()
    #conn.close()
    return render_template('remove.html', data=data)

@app.route("/removeItem")
def removeItem():
    productId = request.args.get('productId')
    with sqlite3.connect('database.db') as conn:
        try:
            cur = conn.cursor()
            cur.execute('DELETE FROM products WHERE productID = ?', (productId, ))
            conn.commit()
            msg = "Deleted successsfully"
        except:
            conn.rollback()
            msg = "Error occured"
    #conn.close()
    print(msg)
    return redirect(url_for('root'))

@app.route('/displayCategory/<int:categoryId>')
def displayCategory(categoryId):
    loggedIn, firstName,userId,noOfItems= getLoginDetails()
    with getConnection() as conn:
        cur = conn.cursor()
        cur.execute('SELECT goods.goods_id, goods_name, price, goods_describe, image_addr, inventory FROM goods, goods_image, goods_attribute WHERE goods.goods_id=goods_image.goods_id AND goods.goods_id=goods_attribute.goods_id AND goods.category_id=?',
                    (categoryId,))
        itemData = cur.fetchall()
        cur.execute("SELECT category_name from category WHERE category.category_id = ?", (categoryId,))
        categoryName = cur.fetchone()[0]
    #conn.close()
    existItem = True
    if len(itemData) == 0:
        existItem = False
    return render_template('display.html', itemData=itemData, loggedIn=loggedIn, firstName=firstName,
                           noOfItems=noOfItems, existItem=existItem, categoryName=categoryName)

@app.route("/search", methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        searching = str(request.form.get('search'))
        print(searching)
        loggedIn, firstName,userId,noOfItems = getLoginDetails()
        t = '%' + searching + '%'
        #print(t)
        with getConnection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT goods.goods_id, goods_name, price, goods_describe, image_addr, inventory FROM goods, goods_image, goods_attribute, shop WHERE goods.goods_id=goods_image.goods_id AND goods.goods_id=goods_attribute.goods_id AND goods.shop_id=shop.shop_id AND ((goods.goods_name LIKE ?) OR (shop.shop_name LIKE ?))", (t,t,))
            itemData = cur.fetchall()
            print(itemData)
        # cur.execute('SELECT category_id, category_name FROM category')
        # categoryData = cur.fetchall()
    # if len(itemData) > 9:
    #     itemData = itemData[0:9]
        return render_template('index.html', itemData=itemData, loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems)
    if request.method == 'GET':
        searching = str(request.form.get('search'))
        print(searching)
        loggedIn, firstName,userId,noOfItems = getLoginDetails()
        t = '%' + searching + '%'
        print(t)
        with getConnection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT goods.goods_id, goods_name, price, goods_describe, image_addr, inventory FROM goods, goods_image, goods_attribute WHERE goods.goods_id=goods_image.goods_id AND goods.goods_id=goods_attribute.goods_id AND (goods.goods_name LIKE ?)", (t,))
            itemData = cur.fetchall()
            print(itemData)
        # cur.execute('SELECT category_id, category_name FROM category')
        # categoryData = cur.fetchall()
    # if len(itemData) > 9:
    #     itemData = itemData[0:9]
        return render_template('index.html', itemData=itemData, loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems)

@app.route("/loginForm")
def loginForm():
    if 'email' in session:
        return redirect(url_for('root'))
    else:
        return render_template('login.html', error='')

@app.route("/login", methods = ['POST', 'GET'])
def login():
    error=''
    if request.method == 'POST':
        email = request.form['inputEmail']
        password = request.form['inputPassword']
        if is_valid(email, password):
            session['email'] = email
            return redirect(url_for('root'))
        else:
            error = 'Invalid UserId / Password'
    return render_template('login.html', error=error)

@app.route("/registerationForm")
def registrationForm():
    return render_template("register.html")

@app.route("/register", methods = ['GET', 'POST'])
def register():
    if request.method == 'POST':
        #Parse form data
        password = request.form['password']
        email = request.form['email']
        firstName = request.form['firstName']
        lastName = request.form['lastName']
        phone = request.form['phone']
        with getConnection() as con:
            try:
                cur = con.cursor()
                cur.execute('INSERT INTO users (password, email, firstName, lastName, phone) VALUES (?, ?, ?, ?, ?)', (hashlib.md5(password.encode()).hexdigest(), email, firstName, lastName, phone))
                con.commit()
                flash("Registered Successfully")
            except:
                con.rollback()
                flash("Error occured")
        #con.close()
        return redirect(url_for('root'))

# @app.route("/profile")
# def profileForm():
#     if 'email' not in session:
#         return redirect(url_for('loginForm'))
#     with sqlite3.connect('database.db') as conn:
#         cur = conn.cursor()
#         cur.execute("SELECT userId, email, firstName, lastName, phone FROM user_inf WHERE email = ?", (session['email'], ))
#         profileData = cur.fetchone()
#     #conn.close()
#     return render_template("profile.html", profileData=profileData)

@app.route("/editProfile", methods = ['GET', 'POST'])
def editProfile():
    if request.method == 'POST':
        email = request.form['email']
        firstName = request.form['firstName']
        lastName = request.form['lastName']
        phone = request.form['phone']
        with sqlite3.connect('database.db') as con:
            try:
                cur = con.cursor()
                cur.execute('UPDATE users SET firstName = ?, lastName = ?, phone = ? WHERE email = ?', (firstName, lastName, phone, email))
                con.commit()
                flash("Saved Successfully")
            except:
                con.rollback()
                flash("Error occured")
        #con.close()
        return redirect(url_for('root'))

@app.route("/ranking/<string:rank_way>")
def rank(rank_way):
    loggedIn, firstName,_,noOfItems = getLoginDetails()
    # if rank_way == 'price':
    #     rank_way = float(rank_way)
    # else:
    #     rank_way = int(rank_way)
    print(rank_way)
    with getConnection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT goods.goods_id, goods_name, price, goods_describe, image_addr, inventory FROM goods, goods_image, goods_attribute WHERE goods.goods_id=goods_image.goods_id AND goods.goods_id=goods_attribute.goods_id ORDER BY " + rank_way + " DESC")
        itemData = cur.fetchall()
        # cur.execute('SELECT category_id, category_name FROM category')
        # categoryData = cur.fetchall()
    # if len(itemData) > 9:
    #     itemData = itemData[0:9]
    return render_template('ranking.html', itemData=itemData, loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems)

@app.route("/price", methods=['GET', 'POST'])
def price():
    if request.method == 'POST':
        price_down = str(request.form.get('price_down'))
        price_up = str(request.form.get('price_up'))
        loggedIn, firstName,_,noOfItems = getLoginDetails()
        with getConnection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT goods.goods_id, goods_name, price, goods_describe, image_addr, inventory FROM goods, goods_image, goods_attribute, shop WHERE goods.goods_id=goods_image.goods_id AND goods.goods_id=goods_attribute.goods_id AND goods.shop_id=shop.shop_id AND ((goods_attribute.price >= ?) AND (goods_attribute.price <= ?))", (price_down,price_up,))
            itemData = cur.fetchall()
            print(itemData)
        # cur.execute('SELECT category_id, category_name FROM category')
        # categoryData = cur.fetchall()
    # if len(itemData) > 9:
    #     itemData = itemData[0:9]
        return render_template('ranking.html', itemData=itemData, loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems)
    
@app.route("/password")
def passwordForm():
    if 'email' not in session:
        return redirect(url_for('loginForm'))
    else:
        return render_template("password.html", msg='')

@app.route("/changePassword", methods = ['GET', 'POST'])
def changePassword():
    if 'email' not in session:
        return redirect(url_for('loginForm'))
    if request.method == "POST":
        oldPassword = request.form['oldpassword']
        oldPassword = hashlib.md5(oldPassword.encode()).hexdigest()
        newPassword = request.form['newpassword']
        newPassword = hashlib.md5(newPassword.encode()).hexdigest()
        with sqlite3.connect('database.db') as conn:
            cur = conn.cursor()
            cur.execute("SELECT userId, password FROM users WHERE email = ?", (session['email'],))
            userId, password = cur.fetchone()
            if (password == oldPassword):
                try:
                    cur.execute("UPDATE users SET password = ? WHERE userId = ?", (newPassword, userId))
                    conn.commit()
                    flash("Changed successfully")
                except:
                    conn.rollback()
                    flash("Failed")
                return redirect(url_for('root'))
            else:
                msg = "Wrong password"
        #conn.close()
        return render_template("password.html", msg=msg)
    else:
        return render_template("password.html", msg='')

@app.route("/logout")
def logout():
    session.pop('email', None)
    return redirect(url_for('root'))

@app.route("/addToCart")
def addToCart():
    if 'email' not in session:
        return redirect(url_for('loginForm'))
    goods_id = int(request.args.get('goods_id'))
    with getConnection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT user_id FROM user_inf WHERE email = ?", (session['email'], ))
        userId = cur.fetchone()[0]
        cur.execute("SELECT goods_num FROM shopping_cart WHERE user_id = ? AND goods_id = ?", (userId, goods_id))
        num = cur.fetchall()
        print(len(num))
        try:
            if len(num)!=0: # 判断是否为空值
                #print(2)
                new_num = num[0][0] + 1
                cur.execute("UPDATE shopping_cart SET goods_num = ? WHERE user_id = ? AND goods_id = ?", (new_num, userId, goods_id))
            else:
                #print(1)
                cur.execute("INSERT INTO shopping_cart (user_id, goods_id, goods_num) VALUES (?, ?, ?)", (userId, goods_id, 1))
            conn.commit()
            flash("Added successfully")
        except:
            conn.rollback()
            flash("Error occured")
    #conn.close()
    return redirect(url_for('cart'))

@app.route("/cart")
def cart():
    if 'email' not in session:
        return redirect(url_for('loginForm'))
    loggedIn, firstName,userId,noOfItems = getLoginDetails()
    email = session['email']
    with getConnection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT user_id FROM user_inf WHERE email = ?", (email, ))
        userId = cur.fetchone()[0]
        cur.execute("SELECT goods.goods_id, goods.goods_name, goods_attribute.price, goods_image.image_addr, shopping_cart.goods_num FROM goods,goods_attribute,goods_image,shopping_cart WHERE goods.goods_id = shopping_cart.goods_id AND goods.goods_id=goods_attribute.goods_id and goods.goods_id = goods_image.goods_id AND shopping_cart.user_id = ?", (userId, ))
        products = cur.fetchall()
    totalPrice = 0
    for i,row in enumerate(products):
        partialPrice = row[2] * row[4]
        products[i] = (row[0], row[1], row[2], row[3], row[4], partialPrice)
        totalPrice += partialPrice
    existItem = False
    if noOfItems > 0:
        existItem = True
    return render_template("cart.html", products = products, totalPrice=totalPrice, existItem=existItem, loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems)

@app.route("/removeFromCart")
def removeFromCart():
    if 'email' not in session:
        return redirect(url_for('loginForm'))
    email = session['email']
    goods_id = int(request.args.get('goods_id'))
    with getConnection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT user_id FROM user_inf WHERE email = ?", (email, ))
        userId = cur.fetchone()[0]
        cur.execute("SELECT goods_num FROM shopping_cart WHERE user_id = ? AND goods_id = ?", (userId, goods_id))
        num = cur.fetchall()
        try:
            if num[0][0] > 1:
                new_num = num[0][0] - 1
                cur.execute("UPDATE shopping_cart SET goods_num = ? WHERE user_id = ? AND goods_id = ?",
                            (new_num, userId, goods_id))
            else:
                cur.execute("DELETE FROM shopping_cart WHERE user_id = ? AND goods_id = ?", (userId, goods_id))
            conn.commit()
            flash("removed successfully")
        except:
            conn.rollback()
            flash("error occured")
    #conn.close()
    return redirect_back()

@app.route("/newOrder")
def newOrder():
    if 'email' not in session:
        return redirect(url_for('loginForm'))
    productId = int(request.args.get('productId'))
    with getConnection() as conn:
        cur = conn.cursor()
        cur.execute("select user_id from user_inf where email = ?", (session['email'],))
        user_id = cur.fetchone()[0]
        cur.execute(
            "select goods_num,price,cart_id from shopping_cart,goods_attribute where shopping_cart.goods_id=goods_attribute.goods_id and user_id=? and shopping_cart.goods_id=?",
            (user_id, productId))
        item = cur.fetchone()
        num = item[0]
        price = num * item[1]
        cart_id = item[2]
        cur.execute("select shop_id from goods where goods_id=?", (productId,))
        shop_id = cur.fetchone()[0]
        try:
            cur.execute(
                "insert into goods_in_orders(goods_id,goods_num,actual_price,shop_id,user_id) values(?,?,?,?,?)",
                (productId, num, price, shop_id, user_id))
            cur.execute("delete from shopping_cart where cart_id=?", (cart_id,))
            conn.commit()
            flash("Trade successfully")
        except:
            conn.rollback()
            flash("Trade failed")
    return redirect(url_for('orders'))

@app.route("/newAllOrder")
def newAllOrder():
    if 'email' not in session:
        return redirect(url_for('loginForm'))
    with getConnection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT user_id FROM user_inf WHERE email = ?", (session['email'],))
        user_id = cur.fetchone()[0]
        cur.execute(
            "select goods_num,price,cart_id,shopping_cart.goods_id from shopping_cart,goods_attribute where shopping_cart.goods_id=goods_attribute.goods_id and user_id=?",
            (user_id,))
        orders=cur.fetchall()
        if len(orders) == 0:
            flash("No Trade")
            return redirect(url_for('cart'))
        try:
            for order in orders:
                num = order[0]
                price = order[1]*num
                cart_id=order[2]
                goods_id=order[3]
                cur.execute("select shop_id from goods where goods_id=?", (goods_id,))
                shop_id = cur.fetchone()[0]
                cur.execute(
                    "insert into goods_in_orders(goods_id,goods_num,actual_price,shop_id,user_id) values(?,?,?,?,?)",
                    (goods_id, num, price, shop_id, user_id))
                cur.execute("delete from shopping_cart where cart_id=?", (cart_id,))
            conn.commit()
            flash("Trade successfully")
        except:
            conn.rollback()
            flash("Trade failed")
    return redirect(url_for('orders'))


@app.route("/orders")
def orders():
    if 'email' not in session:
        return redirect(url_for('loginForm'))
    loggedIn, firstName, userId, noOfItems = getLoginDetails()
    email = session['email']
    with getConnection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT user_id FROM user_inf WHERE email = ?", (email,))
        userId = cur.fetchone()[0]
        cur.execute(
            "select order_id,goods_num,actual_price,comment,evaluate_score,goods_name, goods.goods_id from goods_in_orders, goods where goods_in_orders.goods_id=goods.goods_id and user_id = ?",
            (userId,))
        orderss = cur.fetchall()
    for i, row in enumerate(orderss):
        if row[3] is None:
            is_comment = False
        else:
            is_comment = True
        orderss[i] = (row[0], row[1], row[2], is_comment, row[3], row[4], row[5], row[6])
    existOrder = False
    if len(orderss) > 0:
        existOrder = True
    return render_template("order_comment.html", orderss=orderss, existOrder=existOrder, loggedIn=loggedIn,
                           firstName=firstName, noOfItems=noOfItems)


@app.route("/orderSearch", methods=["GET", "POST"])
def orderSearch():
    if 'email' not in session:
        return redirect(url_for('loginForm'))
    loggedIn, firstName, userId, noOfItems = getLoginDetails()
    email = session['email']
    if request.method == 'POST':
        search_content = request.form['search']
    search_content = '%' + search_content + '%'
    with getConnection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT user_id FROM user_inf WHERE email = ?", (email,))
        userId = cur.fetchone()[0]
        cur.execute(
            "select order_id,goods_num,actual_price,comment,evaluate_score,goods_name, goods.goods_id from goods_in_orders, goods where goods_in_orders.goods_id=goods.goods_id and goods_name like ? and user_id=?",
            (search_content, userId))
        orderss = cur.fetchall()
    for i, row in enumerate(orderss):
        if row[3] is None:
            is_comment = False
        else:
            is_comment = True
        orderss[i] = (row[0], row[1], row[2], is_comment, row[3], row[4], row[5], row[6])
    existOrder = False
    if len(orderss) > 0:
        existOrder = True
    return render_template("order_comment.html", orderss=orderss, existOrder=existOrder, loggedIn=loggedIn,
                           firstName=firstName, noOfItems=noOfItems)


@app.route("/commentForm", methods=["GET", "POST"])
def commentForm():
    order_id = request.args.get("order_id")
    name = request.args.get("goods_name")
    goods_id = request.args.get("goods_id")
    return render_template("comment.html", order_id=order_id, name=name, goods_id=goods_id)


@app.route("/comment", methods=["GET", "POST"])
def comment():
    if 'email' not in session:
        return redirect(url_for('loginForm'))
    if request.method == 'POST':
        score = request.form['starLevel']
        comments = request.form['customerEvaluationComment']
    order_id = request.args.get("order_id")
    goods_id = request.args.get("goods_id")
    with getConnection() as conn:
        cur = conn.cursor()
        cur.execute("update goods_in_order set evaluate_score=? where goods_id= ? and order_id = ?",
                    (score, goods_id, order_id))
        conn.commit()
        if comments is not None:
            cur.execute("update goods_in_order set comment=? where goods_id= ? and order_id = ?",
                        (comments, goods_id, order_id))
            conn.commit()
    return redirect(url_for('orders'))



##进入管理员页面
@app.route("/administrator")
def administrator():
    loggedIn, firstName,userId,noOfItems= getLoginDetails()
    email = session['email']
    with getConnection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM user_inf WHERE user_inf.user_id= ?", (userId, ))
        if_admin_true=cur.fetchone()[0]
        if if_admin_true:
            cur.execute("SELECT transaction_id,user_id,admin_id,transaction_type,transaction_status,comment,commit_time,complete_time FROM transaction_inf")
            transactionData=cur.fetchall()
            cur.execute("SELECT shop_id,shop_name,phone,address,evaluate_sum,evaluate_number FROM shop")
            shopData=cur.fetchall()
            return render_template('administrator.html', transactionData=transactionData, loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems,shopData=shopData)
        else:
            return redirect(url_for('root'))

@app.route('/sales_line/')
def draw_sales_line():
    time_range = range(1, 13)
    time_range = list(time_range)
    num_list = []
    shop_id='1'
    with getConnection() as conn:
        cur = conn.cursor()
        for i in time_range:
            cur.execute('SELECT SUM(goods_num) FROM goods_in_orders WHERE MONTH(time)=? and shop_id=? ', (i,shop_id,))
            tmp = cur.fetchone()[0]
            if (tmp != None):
                num_list.append(tmp)
            else:
                num_list.append(0)

        # cursor = conn.cursor()
        #
        # num = 0
        # shop_id = 1
        # number_list = []
        # sql = "SELECT goods_num FROM goods_in_orders WHERE goods_id in SELECT goods_id FROM goods WHERE shop_id = ?"
        # with cursor.execute(sql,[shop_id]):
        #     row = cursor.fetchone()
        #     while row:
        #         num = num+row[0]

    graph = pygal.StackedLine()  # 创建图（叠加折线图）
    graph.add('商品总销量',num_list)
    graph.x_labels = time_range
    graph.title = '商品总销量随时间变化图'
    graph.x_title = '月份'
    graph.y_title = '总销量'
    return Response(response=graph.render(), content_type='image/svg+xml')

@app.route('/profits_chart/')
def draw_profits_chart():
    goods_list=[]
    profits_list=[]
    rows=[]
    with getConnection() as conn:
        shop_id = '1'
        cur = conn.cursor()
        cur.execute('SELECT goods_id,goods_num,cost,actual_price FROM goods_in_orders WHERE shop_id=?',(shop_id,))
        rows = cur.fetchall()
    for row in rows:
        if(row[0] not in goods_list):
            goods_list.append(row[0])
            profits_list.append(row[1]*(row[3]-row[2]))
        else:
            pos = goods_list.index(row[0])
            profits_list[pos]=row[1]*(row[3]-row[2])+profits_list[pos]
    pie_chart = pygal.Pie()
    for i,j in enumerate(goods_list):
        name = '商品id：'+j
        pie_chart.add(name,profits_list[i])
    pie_chart.title='各商品利润（元）占比的饼图'
    pie_chart.render_to_file('tmp.svg')
    return Response(response=pie_chart.render(), content_type='image/svg+xml')

@app.route('/sales_chart/')
def draw_sales_chart():
    goods_list=[]
    sales_list=[]
    rows=[]
    with getConnection() as conn:
        shop_id = '1'
        cur = conn.cursor()
        cur.execute('SELECT goods_id,goods_num FROM goods_in_orders WHERE shop_id=?',(shop_id,))
        rows = cur.fetchall()
    for row in rows:
        if(row[0] not in goods_list):
            goods_list.append(row[0])
            sales_list.append(row[1])
        else:
            pos = goods_list.index(row[0])
            sales_list[pos]=sales_list[pos]+row[1]
    pie_chart = pygal.Pie()
    for i,j in enumerate(goods_list):
        name = '商品id：'+j
        pie_chart.add(name,sales_list[i])
    pie_chart.title='各商品销量占比的饼图'
    return Response(response=pie_chart.render(), content_type='image/svg+xml')

@app.route('/profits_line/')
def draw_profits_line():
    time_range = range(1, 13)
    time_range = list(time_range)
    shop_id = '1'
    profits_list = []
    with getConnection() as conn:
        cur = conn.cursor()
        for i in time_range:
            cur.execute('SELECT cost,actual_price,goods_num FROM goods_in_orders WHERE MONTH(time)=? and shop_id=? ', (i,shop_id,))
            rows = cur.fetchall()
            profit=0
            for row in rows:
                profit=(row[1]-row[0])*row[2]
            profits_list.append(profit)
        print(profits_list)



        # cursor = conn.cursor()
        #
        # num = 0
        # shop_id = 1
        # number_list = []
        # sql = "SELECT goods_num FROM goods_in_orders WHERE goods_id in SELECT goods_id FROM goods WHERE shop_id = ?"
        # with cursor.execute(sql,[shop_id]):
        #     row = cursor.fetchone()
        #     while row:
        #         num = num+row[0]

    graph = pygal.StackedLine()  # 创建图（叠加折线图）
    graph.add('商家总利润',profits_list)
    graph.x_labels = time_range
    graph.title = '商家总利润随时间变化图'
    graph.x_title = '月份'
    graph.y_title = '总利润（元）'
    return Response(response=graph.render(), content_type='image/svg+xml')

@app.route('/sales_goods/')
def draw_sales_goods():
    goods_list = []
    sales_list = []
    time_range = range(1, 13)
    shop_id = '1'
    rows = []
    graph = pygal.Bar()  # 创建图（叠加折线图）
    with getConnection() as conn:
        cur = conn.cursor()
        cur.execute('SELECT distinct(goods_id) FROM goods_in_orders WHERE shop_id=?', (shop_id,))
        rows = cur.fetchall()
        for row in rows:
            goods_list.append(row[0])
    with getConnection() as conn:
        for item in goods_list:
            for i in time_range:
                cur = conn.cursor()
                cur.execute('SELECT SUM(goods_num) FROM goods_in_orders WHERE MONTH(time)=? and shop_id=? and goods_id=?',(i,shop_id,item,))
                row = cur.fetchone()
                if(row==None):
                    sales_list.append(0)
                else:
                    sales_list.append(row[0])
            graph.add('商品id'+item,sales_list)
            sales_list=[]
    graph.x_labels = map(str,time_range)
    graph.title = '各商品销量随时间变化图'
    graph.x_title = '月份'
    graph.y_title = '销量'

    return Response(response=graph.render(), content_type='image/svg+xml')

@app.route('/profits_goods/')
def draw_profits_goods():
    goods_list = []
    sales_list = []
    time_range = range(1, 13)
    shop_id = '1'
    rows = []
    graph = pygal.Bar()  # 创建图（叠加折线图）
    with getConnection() as conn:
        cur = conn.cursor()
        cur.execute('SELECT distinct(goods_id) FROM goods_in_orders WHERE shop_id=?', (shop_id,))
        rows = cur.fetchall()
        for row in rows:
            goods_list.append(row[0])
    with getConnection() as conn:
        for item in goods_list:
            for i in time_range:
                cur = conn.cursor()
                cur.execute('SELECT SUM(goods_num) FROM goods_in_orders WHERE MONTH(time)=? and shop_id=? and goods_id=?',(i,shop_id,item,))
                row = cur.fetchone()
                if (row[0] == None):
                    sales_list.append(0)
                else:
                    cur.execute(
                        'SELECT cost,actual_price FROM goods_in_orders WHERE shop_id=? and goods_id=?',(shop_id,item,))
                    good=cur.fetchone()
                    profit = good[1]-good[0]
                    if(item=='5'):
                        print(good[1])
                        print(good[0])
                        print(row[0])
                    sales_list.append(row[0] * profit)
            graph.add('商品id'+item,sales_list)
            sales_list=[]
    graph.x_labels = map(str,time_range)
    graph.title = '各商品利润随时间变化图'
    graph.x_title = '月份'
    graph.y_title = '利润（元）'

    return Response(response=graph.render(), content_type='image/svg+xml')

if __name__=="__main__":
    app.run(debug=True)
    