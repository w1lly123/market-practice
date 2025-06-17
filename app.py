from flask import*
from flask_sqlalchemy import SQLAlchemy
import requests


app = Flask(
    __name__,
    static_folder="static",
    static_url_path="/"
)
#使用session一定要設定
app.secret_key="any string but secret"

# 格式：postgresql://使用者:密碼@主機:port/資料庫名稱
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:root@localhost:5432/myshop'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# 定義資料模型
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    price = db.Column(db.Numeric)
    image_url = db.Column(db.String(200))
#定義用戶模型
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

# 建立資料表
with app.app_context():
    db.create_all()


#處理路由
@app.route('/')
def index():
    return render_template("home.html", nickname=session.get("nickname"))


#/error?msg=錯誤訊息
@app.route("/error")
def error():
    msg= request.args.get("msg","發生錯誤，請重新")
    return render_template("error.html",msg = msg)

@app.route("/register")
def register():
    return render_template("registers.html")

@app.route("/signup" ,methods=["POST"])
def signup():
    #從前端接收資料
    nickname =request.form.get("nickname")
    email = request.form.get("email")
    password = request.form.get("password")

    #檢查是否有相同email資料
    existing_user = User.query.filter_by(email = email).first()
    if existing_user:
        return redirect("/error?msg=信箱已被註冊")
    new_user = User(nickname=nickname,email=email,password=password)
    db.session.add(new_user)
    db.session.commit()
    #註冊後自動登入
    session["user_id"] = new_user.id
    session["nickname"] = new_user.nickname
    
    return redirect("/")
@app.route("/login",methods=["GET","POST"])
def login():
    if request.method =="GET":
        return render_template("login.html")
    #驗證reCAPTCHA
    recaptcha_response = request.form.get("g-recaptcha-response")
    secret_key = "6LfqkGMrAAAAAHFYqppJcGtMxrxhsHrlb-GnUFV7"
    verify_url = "https://www.google.com/recaptcha/api/siteverify"

    response = requests.post(verify_url, data={
        "secret": secret_key,
        "response": recaptcha_response
    })

    result = response.json()
    if not result.get("success"):
        return redirect("/error?msg=驗證碼失敗，請再試一次")
    
    #前端取得使用者輸入
    email = request.form.get("email")
    password = request.form.get("password")
    
    if not email or not password:
        return redirect("/error?msg=帳號或密碼輸入錯誤") 
    
    #和資料庫作互動
    user = User.query.filter_by(email=email,password = password).first()
    if user is None:
        return redirect("/error?msg=帳號或密碼輸入錯誤")
    session["user_id"] = user.id
    session["nickname"] = user.nickname
    return redirect("/")
@app.route("/logout")
def logout():
    session.pop("nickname","")
    session.pop("user_id","")
    session.pop("cart","")
    return  redirect("/")
#商品頁路由
@app.route("/product")
def product_page():
    products = Product.query.all()
    return render_template("product.html", nickname=session.get("nickname"),products=products)

@app.route("/cart")
def cart():
    if "user_id" not in session:
        return redirect("/login")

    cart_items = session.get("cart", [])
    
    # 計算總金額
    total = sum(item["price"] * item["quantity"] for item in cart_items)

    return render_template("cart.html", cart_items=cart_items, total=total)


if __name__ == '__main__':
    app.run(debug=True, port=3000)
