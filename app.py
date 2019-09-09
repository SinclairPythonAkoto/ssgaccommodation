import os

from flask import Flask, render_template, g, url_for, request, redirect, flash, session
from functools import wraps
from flask_mail import Mail, Message

app = Flask(__name__)

app.config.update(dict(
    DEBUG = True,
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = 587,
    MAIL_USE_TLS = True,
    MAIL_USE_SSL = False,
    MAIL_USERNAME = os.getenv("SSGA_GMAIL"), # jonny email
    MAIL_PASSWORD = os.getenv("SSGA_GMAIL_PW") , # email password
    MAIL_DEFAULT_SENDER = ('SSG Accommodation', os.getenv("SSGA_GMAIL")), #('NAME OR TITLE OF SENDER', 'SENDER EMAIL ADDRESS')
    MAIL_MAX_EMAILS = 5
))

mail = Mail(app)



app.secret_key = os.getenv("SECRET_KEY")


def login_required(f):
	@wraps(f)
	def wrap(*args, **kwargs):
		if 'logged_in' in session:
			return f(*args, **kwargs)
		else:
			flash('You need to sign in first')
			return redirect(url_for('login'))
	return wrap

from sqlalchemy.orm import sessionmaker, relationship

# # this part is needed to create session to query database.  this should be JUST BELOW app.config..
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, ForeignKey, select
meta = MetaData()
engine = create_engine(os.getenv("DATABASE_URL"), echo = True)
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()


class SSG_Contact(Base):
	__tablename__ = 'ssg_contact'
	id = Column('id', Integer, primary_key=True)
	name = Column('name', String(30))
	age = Column('age', Integer)
	sex = Column('sex', String(6))
	email = Column('email', String(50))
	interest = Column('interest_in', String(6))
	questions = Column('questions', String(360))

	def __init__(self, name, age, sex, email, interest, questions):
		self.name = name
		self.age = age
		self.sex = sex
		self.email = email
		self.interest = interest
		self.questions = questions


Session = sessionmaker(bind=engine)
db_session = Session()


@app.route('/', methods=['GET', 'POST'])
def home():
	title = "SSGA Home"
	return render_template('home.html', title=title)

@app.route('/rooms')
def rooms():
	title = "SSGA Romms"
	return render_template('rooms.html', title=title)

@app.route('/contact', methods=['GET','POST'])
def contact():
	title = "Contact SSG"
	if request.method == 'GET':
		return render_template('contact.html', title=title)
	else:
		user = request.form.get("username")
		age = request.form.get("age")
		gender = request.form.get("select_sex")
		email = request.form.get("email")
		interest = request.form.get("interest")
		enquiry = request.form.get("questions")

		db_entry = SSG_Contact(user, age, gender, email, interest, enquiry)
		db_session.add(db_entry)
		db_session.commit()
		data = db_session.query(SSG_Contact).all()
		flash(f'Thank you {user} for your enquiry, SSG Accommodation will get back to you shortly.')
		return render_template('contact.html', title=title)


@app.route('/login', methods=['GET', 'POST'])
def login():
	title = "SSGA Login"
	error = None
	if request.method == 'GET':
		return render_template('login.html', title=title)
	else:
		admin = request.form.get("username")
		admin_pw = request.form.get("password")
		if admin == os.getenv("SGGA_ADMIN") and admin_pw == os.getenv("SSGA_ADMIN_PW"):
			session['logged_in'] = True
			flash('Welcome back Gloria, you have just logged in!')
			return redirect(url_for('admin'))
		else:
			error = "Invalid username and/or password.  You must be management of SSG Accommodation to login."
	return render_template('login.html', error=error, title=title)

@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
	title = "SSGA Admin"
	data = db_session.query(SSG_Contact).all()
	return render_template('admin.html', title=title, data=data)


@app.route('/send_email', methods=['GET', 'POST'])
@login_required
def send_email():
	title = "SSG Accommodation"
	sendTo = request.form.get("emailReciever")
	sub = request.form.get("emailSubject")
	content = request.form.get("emailContent")
	if request.method =='GET':
		return render_template('send_email.html', title=title)
	else:
		msg = Message(f'{sub}', recipients=[sendTo])
		msg.body = f'{content}\nKind regards\n\nGloria Pinket\nSSG Accommodation'
		mail.send(msg)
		flash(f'Your message has been sent!')
		return redirect(url_for('admin'))

@app.route('/logout')
@login_required
def logout():
	session.pop('logged_in', None)
	flash('See you soon Gloria!')
	return redirect(url_for('home'))


if __name__ == '__main__':
	app.run(debug=True)