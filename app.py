from flask import*
from flask_sqlalchemy import SQLAlchemy

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
    return render_template("index.html")

@app.route("/member")
def member():
    #權限控管
    if "nickname" in session:
        return render_template("member.html")
    else:
        return redirect("/")

#/error?msg=錯誤訊息
@app.route("/error")
def error():
    msg= request.args.get("msg","發生錯誤，請重新")
    return render_template("error.html",msg = msg)


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
    
    return redirect("/")
@app.route("/login",methods=["POST"])
def login():
    #前端取得使用者輸入
    email = request.form.get("email")
    password = request.form.get("password")
    #和資料庫作互動
    user = User.query.filter_by(email=email,password = password).first()
    if user is None:
        return redirect("/error?msg=帳號或密碼輸入錯誤")
    session["user_id"] = user.id
    session["nickname"] = user.nickname
    return redirect("/member")
@app.route("/logout")
def logout():
    del session["nickname"]
    return  redirect("/")
        
if __name__ == '__main__':
    app.run(debug=True, port=3000)
