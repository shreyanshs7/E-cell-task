from flask import Flask,render_template,request
from flask_mail import Mail, Message
import MySQLdb
from werkzeug import secure_filename
import hashlib
import os

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = 'start-up-icon/'
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'tmail6336@gmail.com'
app.config['MAIL_PASSWORD'] = 'testmail12345'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

db = MySQLdb.connect(host="localhost",user="root",passwd="abcd",db="task")

cursor = db.cursor()

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/push-panel')	
def panel():
	return render_template('adminlogin.html')
	

@app.route('/admin-login',methods=['GET','POST'])
def admin():
	if request.method=='POST':
		adminuser = request.form['adminuser']
		adminpass = request.form['adminpass']

		if adminuser=='admin' and adminpass=='admin':
			return render_template('pushpanel.html')	
		else:
			return("Wrong Credentials")
	return("Not allowed") 	


@app.route('/register',methods=['GET','POST'])
def register():
	if request.method=='POST':
		startupname = request.form['startupname']
		yourname = request.form['name']
		email = request.form['email']
		password = request.form['password']
		phoneno = request.form['phoneno']
		f=request.files['file']
		nameoffile=(f.filename)
		ext=nameoffile.split('.')
		ext=ext[len(ext)-1]
		f.filename=email+"."+ext
		f.save(os.path.join(app.config['UPLOAD_FOLDER'],secure_filename(f.filename)))

		password=(hashlib.md5(password.encode('utf-8')).hexdigest())

		cursor.execute("""INSERT INTO register(startupname,yourname,email,password,phoneno) VALUES (%s,%s,%s,%s,%s)""",[startupname,yourname,email,password,phoneno])
        que = "select activate from register where email=%s"
        cursor.execute(que,[email])
        activate=cursor.fetchone()
        activate=activate[0]
        if activate==1:
        	return("User already registered")
        else:	        
			db.commit()
		

			uniq=email+password
			h=(hashlib.md5(uniq.encode('utf-8')).hexdigest())

			msg = Message('Confirmation mail',sender='shreyanshss7@gmail.com',recipients=['%s' % (email)])	
			msg.body = "localhost:5000/confirm?email="+email+"&hash="+h
			mail.send(msg)
			return("check mail for confirmation")
	db.close()
	


@app.route('/confirm',methods=['GET','POST'])
def confirm():
	email=request.args.get('email')
	h1=request.args.get('hash')
	query="select password from register where email=%s"
	cursor.execute(query,[email])
	password=cursor.fetchone()
	password=password[0]

	uniq=email+password
	
	h2=(hashlib.md5(uniq.encode('utf-8')).hexdigest())
	if h1==h2:
		cursor.execute("""update register set activate= %s where email=%s""",['1',email])
		db.commit()
		return("user confirmed")


if __name__ == '__main__':
		app.run(debug=True)	
