from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'supersecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///vssutConfession.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
bcrypt = Bcrypt()

with app.app_context():
    db.create_all()

date= '{dt.day}/{dt.month}/{dt.year}'.format(dt = datetime.now())

class Confessions(db.Model):
    Id = db.Column(db.Integer, primary_key=True)
    Confession = db.Column(db.String(1000), nullable=False)
    Name = db.Column(db.String(100),nullable=False)
    Date = db.Column(db.String,default=date)
    Approved = db.Column(db.Boolean, default=False)

class Admin(db.Model):
    Id = db.Column(db.Integer, primary_key=True)
    Username = db.Column(db.String(80), unique=True, nullable=False)
    Password = db.Column(db.String(200), nullable=False)

    @staticmethod
    def create_admin(username, password):
        hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
        return Admin(Username=username, Password=hashed_pw)

# @app.before_first_request
# def init_db():
#     db.create_all()
#     if not Admin.query.filter_by(Username='admin').first():
#         admin = Admin.create_admin('BitMik', 'Super_hard_password')
#         db.session.add(admin)
#         db.session.commit()

@app.route('/')
def index():
    confessions = Confessions.query.filter_by(Approved=True).order_by(Confessions.Id.desc()).all()
    return render_template('index.html', confessions=confessions)
    


@app.route('/submit', methods=['POST'])
def submit_comment():
    confession_text = request.form['confession']
    name = request.form['name']
    if not name :
        name="Bhisutian"
    comment = Confessions(Confession=confession_text,Name=name)
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        admin = Admin.query.filter_by(Username=username).first()
        if admin and password == admin.Password:
            session['admin'] = username
            return redirect(url_for('admin'))
            
        else:
            flash('Invalid username or password', 'danger')
    return render_template('loginPage.html')

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    # username=Admin.query.filter_by(Username='admin').first()
    if 'admin' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        if 'approve' in request.form:
            comment_id = request.form['approve']
            comment = Confessions.query.get(comment_id)
            if comment:
                comment.Approved = True
                db.session.commit()
        elif 'delete' in request.form:
            comment_id = request.form['delete']
            comment = Confessions.query.get(comment_id)
            if comment:
                db.session.delete(comment)
                db.session.commit()
    
    allConfessions = Confessions.query.filter_by(Approved=False).order_by(Confessions.Id.desc()).all()
    allApprovedConfessions = Confessions.query.filter_by(Approved=True).order_by(Confessions.Id.desc()).all()
    return render_template('admin.html', admin=session['admin'],allConfessions=allConfessions,a_allConfession=allApprovedConfessions)
    
@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    # init_db()
    app.run(debug=True)