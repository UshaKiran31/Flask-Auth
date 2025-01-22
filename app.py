from flask import Flask,render_template,redirect,request,session,url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash,check_password_hash
from flask_scss import Scss


app = Flask(__name__)
#your secret key
app.secret_key="3110"
Scss(app)

# Configure SQL Alchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# Database Model ~ Single Row with our DB
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


# Route
# home
@app.route("/")
def home():
    if "username" in session:
        return redirect(url_for('dashboard'))
    return render_template("index.html")


# Login
@app.route("/login",methods=["POST"])
def login():
    #Collect info from the form
    #Check if its in the db / login
    #otherwise show home page
    username = request.form['username']
    password = request.form['password']
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        session['username'] = username
        return redirect(url_for('dashboard'))
    else:
        return render_template("index.html",error="Invalid username or password")


# Register
@app.route("/register", methods=["POST"])
def register():
    #Collect info from the form
    #Check if Username already exists! / login
    #otherwise create new user and login
    username = request.form['username']
    password = request.form['password']
    user = User.query.filter_by(username=username).first()
    if user:
        return render_template("index.html",error="Username already exists!")
    else:
        new_user = User(username=username)
        new_user.set_password(password)
        #add the user and commit
        db.session.add(new_user)
        db.session.commit()
        #creating new user for this username
        session['username'] = username
        return redirect(url_for('dashboard'))
    

# Dashboard
@app.route("/dashboard")
def dashboard():
    #check if user is logged in
    if "username" in session:
        return render_template("dashboard.html", username=session['username'])
    return redirect(url_for('home'))


# LOgout
@app.route("/logout")
def logout():
    #remove the user from the session
    session.pop('username', None)
    return redirect(url_for('home'))




if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
