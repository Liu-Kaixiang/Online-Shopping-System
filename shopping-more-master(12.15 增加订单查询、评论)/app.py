# -*- coding: utf-8 -*-
from flask import Flask
from flask import *
from werkzeug.utils import secure_filename

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
        cur.execute('SELECT shop_id, shop_name, address, phone, shop_describe, announcement, img, sales FROM shop WHERE shop_id=?', (shop_id,))
        itemData = cur.fetchall()[0]
        print(itemData)
        cur.execute('SELECT goods.goods_id, goods_name, price, goods_describe, image_addr, inventory FROM goods, goods_image, goods_attribute WHERE goods.goods_id=goods_image.goods_id AND goods.goods_id=goods_attribute.goods_id AND goods.shop_id=?', (shop_id,))
        categoryData = cur.fetchall()
        # cur.execute('SELECT shop.shop_id, shop_name FROM shop, goods WHERE goods.goods_id=? AND goods.shop_id=shop.shop_id', (goods_id,))
        # shopData = cur.fetchall()[0]
    return render_template("store.html", itemData=itemData, categoryData=categoryData, loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems)

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
    return redirect_back()

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
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT user_id FROM user_inf WHERE email = ?", (session['email'], ))
        userId = cur.fetchone()[0]
        cur.execute("SELECT num FROM kart WHERE user_id = ? AND productId = ?", (userId, productId))
        num = cur.fetchone()[0]
        orderId = int(time.time() * 100) * 10000 + productId
        try:
            cur.execute("INSERT INTO orders (orderId, userId, productId, num) VALUES (?, ?, ?, ?)", (orderId, userId, productId, num))
            cur.execute("DELETE FROM kart WHERE userId = ? AND productId = ?", (userId, productId))
            conn.commit()
            flash("Trade successfully")
        except:
            conn.rollback()
            flash("Trade failed")
    #conn.close()
    return redirect(url_for('orders'))

@app.route("/newAllOrder")
def newAllOrder():
    if 'email' not in session:
        return redirect(url_for('loginForm'))
    with getConnection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT user_id FROM user_inf WHERE email = ?", (session['email'], ))
        userId = cur.fetchone()[0]
        cur.execute("SELECT num, productId FROM kart WHERE userId = ?", (userId, ))
        orders = cur.fetchall()
        if len(orders)==0:
            flash("No Trade")
            return redirect(url_for('cart'))
        try:
            for order in orders:
                num = order[0]
                productId = order[1]
                orderId = int(time.time() * 100) * 10000 + productId
                cur.execute("INSERT INTO orders (orderId, userId, productId, num) VALUES (?, ?, ?, ?)", (orderId, userId, productId, num))
                cur.execute("DELETE FROM kart WHERE userId = ? AND productId = ?", (userId, productId))
            conn.commit()
            flash("Trade successfully")
        except:
            conn.rollback()
            flash("Trade failed")
    #conn.close()
    return redirect(url_for('orders'))

@app.route("/orders")
def orders():
    if 'email' not in session:
        return redirect(url_for('loginForm'))
    loggedIn, firstName,userId,noOfItems = getLoginDetails()
    email = session['email']
    with getConnection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT user_id FROM user_inf WHERE email = ?", (email,))
        userId = cur.fetchone()[0]
        cur.execute(
            "select goods_order.order_id,goods_num,actual_price,comment,evaluate_score,goods_name, goods.goods_id from (goods_in_order join goods_order on goods_in_order.order_id=goods_order.order_id) join goods on goods_in_order.goods_id=goods.goods_id where user_id = ?", (userId,))
        orderss = cur.fetchall()
    for i, row in enumerate(orderss):
        # partialPrice = row[0] * row[3]
        # time_stamp = int(row[1] / 1000000)
        # time_array = time.localtime(time_stamp)
        # str_date = time.strftime("%Y-%m-%d %H:%M:%S", time_array)
        # color = random_color()
        # orderss[i] = (row[0], row[1], row[2], row[3], partialPrice, str_date, color)
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
    loggedIn, firstName,userId,noOfItems = getLoginDetails()
    email = session['email']
    if request.method == 'POST':
        search_content = request.form['search']
    search_content = '%' + search_content + '%'
    with getConnection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT user_id FROM user_inf WHERE email = ?", (email,))
        userId = cur.fetchone()[0]
        cur.execute(
            "select goods_order.order_id,goods_num,actual_price,comment,evaluate_score,goods_name, goods.goods_id from (goods_in_order join goods_order on goods_in_order.order_id=goods_order.order_id) join goods on goods_in_order.goods_id=goods.goods_id where  goods_name like ? and user_id=?",
            (search_content,userId))
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

if __name__=="__main__":
    app.run(debug=True)
    