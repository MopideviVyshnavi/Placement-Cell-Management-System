from flask import Flask, request, session, redirect, url_for, render_template, flash
from flask_session import Session
from flask_mail import Mail, Message
import os
import mysql.connector  # ✅ switched from psycopg2 to mysql.connector
import re
import time
from werkzeug.security import generate_password_hash, check_password_hash
from common import cache
import pyautogui as pag
import smtplib
import json
import random
from dotenv import load_dotenv

# Load environment variables from .env file (optional but recommended)
load_dotenv()

app = Flask(__name__)

# Flask Session & Mail configapp.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

# ✅ Secret Key from .env
app.secret_key = os.getenv("SECRET_KEY", "fallback-secret-key")

# MySQL Database config using dotenv
DB_NAME = os.getenv("DB_NAME", "flask_db")
DB_USER = os.getenv("DB_USERNAME", "root")
DB_PASS = os.getenv("DB_PASSWORD", "Webpass@123")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", 3307))

# MySQL Connection
conn = mysql.connector.connect(
    host=DB_HOST,
    database=DB_NAME,
    user=DB_USER,
    password=DB_PASS,
    port=DB_PORT
)
print("Connected to the database!")


Session(app)

# You can now use `conn.cursor()` as before

# ...

@app.route('/add_job', methods=('GET', 'POST'))
def add_job():
    #return str(request.form['job_Id'])
    if session.get("username") == None:
       return redirect(url_for('loginadmin'))

    if request.method == 'POST':

        session['job_id'] = request.form.get('job_Id',False)
        if session['job_id']==False:
           return render_template('job.html')
        session['company'] = request.form['Company']
        session['position'] = request.form['Position']
        eligibility = request.form.getlist('Eligibility')
        session['streligible']='#'.join(eligibility)
        strelg='#'.join(eligibility)

        finelf=""

        for c in eligibility:
            if c=="BTech-ME":
                finelf+='#Bachelor of Technology, Mechanical Engineering'
            elif c=="BTech-CE":
                finelf+='#Bachelor of Technology, Chemical Engineering'
            elif c=="BTech-CS":
                finelf+='#Bachelor of Technology, Computer Science Engineering'
            elif c=="BTech-EE":
                finelf+='#Bachelor of Technology, Electrical Engineering'
            elif c=="BTech-ECE":
                finelf+='#Bachelor of Technology, Electronics and Communication Engineering'
            elif c=="MCA":
                finelf+='#Master in Computer Applications'
            elif c=="MTech-ME":
                finelf+='#Master of Technology, Mechanical Engineering'
            elif c=="MTech-CE":
                finelf+='#Master of Technology, Chemical Engineering'
            elif c=="MTech-CS":
                finelf+='#Master of Technology, Computer Science Engineering'
            elif c=="MTech-EE":
                finelf+='#Master of Technology, Electrical Engineering'
            elif c=="MTech-ECE":
                finelf+='#Master of Technology, Electronics and Communication Engineering'

        finelf=finelf.lstrip('#')

        session['cgpa'] = float(request.form['CGPA'])
        session['loc'] = request.form['Location']
        session['type'] = request.form['type']
        cur = conn.cursor()
        #return str(request.form['job_Id'])

        try:
            cur.execute('INSERT INTO job (job_id, company, position, eligibility, cgpa, loc, type)'
                        'VALUES (%s, %s, %s, %s, %s, %s, %s)',
                        (session['job_id'], session['company'], session['position'], finelf, session['cgpa'], session['loc'], session['type']))
        except:
            flash("Job Id alreay exists")
            return redirect(url_for('add_job'))
        conn.commit()
        if session['type'] == 'Fulltime':
            return redirect(url_for('fulltime'))
        else :
            return redirect(url_for('intern'))
        return render_template('adminhome.html')
    else:
        return render_template('job.html')




@app.route('/fulltime/', methods=('GET', 'POST'))
def fulltime():
    print( request.form)
    if request.method == 'POST':
        bond = request.form['bond']
        package = request.form['package']
        cur = conn.cursor()
        job_id=session['job_id']

        cur.execute('INSERT INTO fulltime (job_id, bond, package)'
                    'VALUES (%s, %s, %s)',
                    (job_id, bond, package))
        conn.commit()
        return redirect(url_for('temp'))
        return render_template('adminhome.html')
    else:
        return render_template('fulltime.html')




@app.route("/temp")
def temp():

    cur=conn.cursor()
    courses=str(session['streligible']).split("#")
    #return courses
    listemails=[]
    branch=[]

    for c in courses:
       cur.execute("SELECT regNo FROM UG where branch=(%s)",(c,))
       regNo=cur.fetchall()
       branch.append(regNo)
       cur.execute("SELECT regNo FROM PG where branch=(%s)",(c,))
       regNo=cur.fetchall()
       branch.append(regNo)
    #return branch


    #for regNo in branch:
    #   for r in regNo:
    #      for i in r:
    #         if len(str(i))!=0:
    #           #return i
    #           cur.execute("SELECT * FROM Student where regNo=(%s)",(str(i),))
    #           #return str(cur.fetchall())
    #           details=cur.fetchall()
    #           listemails.append(details[0][4])

    #return listemails

    #return redirect(url_for('add_job'))


    #for m in listemails:

    #msg = Message('Hello', sender = 'mayank17.mewar@gmail.com', recipients = ['dikshant_m210670ca@nitc.ac.in'])
    #msg.body = "This is the email body"
    #mail.send(msg)
         #time.sleep(10)
    return redirect(url_for('add_job'))



@app.route('/intern/', methods=('GET', 'POST'))
def intern():
    if request.method == 'POST':
        ppo = request.form['ppo']
        duration = request.form['duration']
        salary = request.form['salary']
        cur = conn.cursor()
        job_id=session['job_id']

        cur.execute('INSERT INTO internship (job_id, duration, ppo, salary)'
                    'VALUES (%s, %s, %s, %s)',
                    (job_id, duration, ppo, salary))
        conn.commit()
        cur.close()
        return redirect(url_for('temp'))
        return render_template('adminhome.html')
    else:
        return render_template('intern.html')




@app.route('/')
def home():
    # Check if user is loggedin
    if 'loggedin' in session:

        # User is loggedin show them the home page
        return render_template('home.html', username=session['username'])
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))





@app.route('/login/', methods=['GET', 'POST'])
def login():
    #if session.get("username") == None:
     #  return "hello"
    cursor = conn.cursor(dictionary=True) 

    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        print(password)

        # Check if account exists using MySQL
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        # Fetch one record and return result
        account = cursor.fetchone()

        if account:
            password_rs = account['password']
            print(password_rs)
            # If account exists in users table in out database
            if check_password_hash(password_rs, password):
                # Create session data, we can access this data in other routes
                session['loggedin'] = True
                session.permanent = True
                #session['id'] = account['id']
                session['username'] = account['username']
                # Redirect to home page
                return redirect(url_for('home'))
            else:
                # Account doesnt exist or username/password incorrect
                flash('Incorrect username/password')
        else:
            # Account doesnt exist or username/password incorrect
            flash('Incorrect username/password')

    return render_template('login.html')




@app.route('/loginadmin/', methods=['GET', 'POST'])
def loginadmin():
    cursor = conn.cursor(dictionary=True) 
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        print(password)

        # Check if account exists using MySQL
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        # Fetch one record and return result
        account = cursor.fetchone()

        if account:
            password_rs = account['password']
            print(password_rs)
            # If account exists in users table in out database
            if check_password_hash(password_rs, password):
                # Create session data, we can access this data in other routes
                session['loggedin'] = True
                session.permanent = True
                #session['id'] = account['id']
                session['username'] = account['username']
                # Redirect to home page
                return redirect(url_for('adminHome'))
            else:
                # Account doesnt exist or username/password incorrect
                flash('Incorrect username/password')
        else:
            # Account doesnt exist or username/password incorrect
            flash('Incorrect username/password')

    return render_template('loginadmin.html')


@app.route('/delete/<string:id>', methods = ['POST','GET'])
def delete_student(id):
    cursor = conn.cursor(dictionary=True) 
    cursor.execute('DELETE FROM job WHERE job_id = %s',
                (id,))
    cursor.execute('DELETE FROM fulltime WHERE job_id = %s',
                (id,))
    cursor.execute('DELETE FROM internship WHERE job_id = %s',
                (id,))
    conn.commit()
    return redirect(url_for('index'))





@app.route('/register', methods=['GET', 'POST'])
def register():
    cursor = conn.cursor(dictionary=True)

    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        fullname = request.form['fullname']
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        _hashed_password = generate_password_hash(password)

        #Check if account exists using MySQL
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        account = cursor.fetchone()
        print(account)
        # If account exists show error and validation checks
        if account:
            flash('Account already exists!')
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            flash('Invalid email address!')
        elif not re.match(r'[A-Za-z0-9]+', username):
            flash('Username must contain only characters and numbers!')
        elif not username or not password or not email:
            flash('Please fill out the form!')
        else:
            # Account doesnt exists and the form data is valid, now insert new account into users table
            cursor.execute("INSERT INTO users (fullname, username, password, email) VALUES (%s,%s,%s,%s)", (fullname, username, _hashed_password, email))
            conn.commit()
            flash('You have successfully registered!')
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        flash('Please fill out the form!')
    # Show registration form with message (if any)
    return render_template('register.html')




@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   # Redirect to login page
   return redirect(url_for('login'))




@app.route('/logoutadmin')
def logoutAdmin():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   # Redirect to login page
   return redirect(url_for('loginadmin'))

@app.route('/profile')
def profile():
    if session.get("username") is None:
        return redirect(url_for('login'))

    # Create cursor
    cur = conn.cursor(dictionary=True)

    # Fetch account details based on the logged-in user's username
    cur.execute('SELECT * FROM users WHERE username = %s', (session['username'],))
    account = cur.fetchone()

    if account is None:
        return redirect(url_for('login'))  # If no account found, redirect to login

    return render_template('profile.html', account=account)



@app.route('/home')
def studentHome():
    return render_template('home.html')





@app.route('/adminhome')
def adminHome():
    return render_template('adminhome.html')





@app.route('/db/')
def index():
    if session.get("username") is None:
        return redirect(url_for('loginadmin'))

    cursor = conn.cursor(dictionary=True)

    cursor.execute('SELECT * FROM Student;')
    students = cursor.fetchall()

    cursor.execute('SELECT * FROM UG;')
    ugs = cursor.fetchall()

    cursor.execute('SELECT * FROM PG;')
    pgs = cursor.fetchall()

    cursor.execute('SELECT * FROM job;')
    job = cursor.fetchall()

    cursor.execute('SELECT * FROM fulltime;')
    fulltime = cursor.fetchall()

    cursor.execute('SELECT * FROM internship;')
    intern = cursor.fetchall()

    cursor.execute('SELECT * FROM applied;')
    applied = cursor.fetchall()

    cursor.close()

    return render_template(
        'index.html',
        students=students,
        ugs=ugs,
        pgs=pgs,
        job=job,
        fulltime=fulltime,
        intern=intern,
        applied=applied
    )



# ...

@app.route('/create/', methods=('GET', 'POST'))
def create():
    if session.get("username") is None:
        return redirect(url_for('login'))

    if request.method == 'POST':
        try:
            regno = request.form['regno']
            fname = request.form['fname']
            lname = request.form['lname']
            dob_raw = request.form['year']
            dob = time.strptime(dob_raw, "%Y-%m-%d")
            dob_formatted = f"{dob.tm_year}-{dob.tm_mon:02d}-{dob.tm_mday:02d}"

            email = request.form['email']
            phone = request.form['phone']
            address = request.form['address']
            gender = request.form['gender']
            typee = request.form['type']
            cgpa = request.form['cgpa']
            fa = request.form['fa']
            sem = request.form['cursem']

            cursor = conn.cursor(dictionary=True)

            # Insert into Student
            cursor.execute(
                '''INSERT INTO Student (regNo, firstName, lastName, dob, email, phoneNo, address, gender, type, cgpa, fa)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''',
                (regno, fname, lname, dob_formatted, email, phone, address, gender, typee, cgpa, fa)
            )

            # Insert into Applied
            cursor.execute(
                'INSERT INTO Applied (regno, companies) VALUES (%s, %s)',
                (regno, "")
            )

            # Determine branch
            ch1 = regno[0]
            ch2 = regno[-2]
            ch3 = regno[-1]
            branch_code = ch1 + ch2 + ch3

            branch_map = {
                # UG Branches
                "BME": "Bachelor of Technology, Mechanical Engineering",
                "BCE": "Bachelor of Technology, Chemical Engineering",
                "BCS": "Bachelor of Technology, Computer Science Engineering",
                "BEE": "Bachelor of Technology, Electrical Engineering",
                "BEC": "Bachelor of Technology, Electronics and Communication Engineering",

                # PG Branches
                "MCA": "Master in Computer Applications",
                "MME": "Master of Technology, Mechanical Engineering",
                "MCE": "Master of Technology, Chemical Engineering",
                "MCS": "Master of Technology, Computer Science Engineering",
                "MEE": "Master of Technology, Electrical Engineering",
                "MEC": "Master of Technology, Electronics and Communication Engineering"
            }

            branch = branch_map.get(branch_code, "Unknown Branch")

            if typee == 'UG':
                cursor.execute(
                    'INSERT INTO UG (regNo, branch, semester) VALUES (%s, %s, %s)',
                    (regno, branch, sem)
                )
            else:
                cursor.execute(
                    'INSERT INTO PG (regNo, branch, semester) VALUES (%s, %s, %s)',
                    (regno, branch, sem)
                )

            conn.commit()
            cursor.close()
            flash("Student registered successfully!")
            return render_template('home.html')

        except mysql.connector.Error as err:
            flash(f"MySQL Error: {err}")
        except Exception as e:
            flash("Already existing user or invalid input!")

    return render_template('create.html')

@app.route('/my-link/')
def my_link():
   cururl = request.url
   s2="?"
   regno=cururl[cururl.index(s2) + len(s2):]
   regno=str(regno)

   #conn = get_db_connection()
   cursor = conn.cursor(dictionary=True)
   cur = conn.cursor()
   cur.execute("SELECT 1")

   cur.execute('SELECT type from Student WHERE regNo = (%s)',(regno,))
   typee=cur.fetchall()
   #return typee
   typ=typee[0][0]

   if typ=='UG':
      cur.execute('DELETE FROM UG WHERE regNo = (%s)',
                (regno,))
   else:
      cur.execute('DELETE FROM PG WHERE regNo = (%s)',
                (regno,))

   cur.execute('DELETE FROM Student WHERE regNo = (%s)',
                (regno,))
   cur.execute('DELETE FROM applied WHERE regNo = (%s)',
                (regno,))

   conn.commit()
   return redirect(url_for('index'))




@app.route('/view/')
def view():
    if session.get("username") is None:
        return redirect(url_for('login'))

    cur = conn.cursor(buffered=True)  # Added buffered=True to handle multiple queries safely

    # Fetch details of the student using their regNo (username)
    cur.execute('SELECT * FROM Student WHERE regNo = %s', (session['username'],))
    details = cur.fetchall()

    # If no record found, redirect to 'create' route
    if len(details) == 0:
        return redirect(url_for('create'))

    # Fetch the student type (UG/PG)
    cur.execute('SELECT type FROM Student WHERE regNo = %s', (session['username'],))
    typ = cur.fetchone()[0]  # Fetch the first result and get the type

    # Handle UG or PG details based on the type
    if typ == 'UG':
        cur.execute('SELECT * FROM UG WHERE regNo = %s', (session['username'],))
        ugdetails = cur.fetchall()
        return render_template('view.html', details=details, ugdetails=ugdetails)
    else:
        cur.execute('SELECT * FROM PG WHERE regNo = %s', (session['username'],))
        pgdetails = cur.fetchall()
        return render_template('view.html', details=details, pgdetails=pgdetails)

@app.route('/edit/')
def edit():
    cur = conn.cursor()
    cur.execute("SELECT 1")

    cur.execute('SELECT * from Student WHERE regNo = (%s)',(session['username'],))
    details=cur.fetchall()

    cur.execute('SELECT type from Student WHERE regNo = (%s)',(session['username'],))
    typee=cur.fetchall()
    #return typee
    typ=typee[0][0]

    if typ=='UG':
       cur.execute('SELECT * from UG WHERE regNo = (%s)',(session['username'],))
       ugdetails=cur.fetchall()
       return render_template('editprofile.html',details=details,ugdetails=ugdetails)
    else:
       cur.execute('SELECT * from PG WHERE regNo = (%s)',(session['username'],))
       pgdetails=cur.fetchall()
       return render_template('editprofile.html',details=details,pgdetails=pgdetails)





@app.route('/update/', methods=('GET', 'POST'))
def update():

    if session.get("username") == None:
       return redirect(url_for('login'))

    cur = conn.cursor()
    #return request.method
    if request.method == 'POST':
        cgpa = request.form['cgpa']
        cursem = request.form['cursem']

        #return cgpa+cursem

        cur.execute('SELECT type from Student WHERE regNo = (%s)',(session['username'],))
        typee=cur.fetchall()
        typ=typee[0][0]

        #conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cur = conn.cursor()
        cur.execute("SELECT 1")

        cur.execute("Update Student set cgpa = %s where regNo = %s",(cgpa,session['username'],))

        if typ=='UG':
           cur.execute("Update UG set semester = %s where regNo = %s",(cursem,session['username'],))

        else:
           cur.execute("Update PG set semester = %s where regNo = %s",(cursem,session['username'],))

        conn.commit()

    cur.execute('SELECT * from Student WHERE regNo = (%s)',(session['username'],))
    details=cur.fetchall()

    cur.execute('SELECT type from Student WHERE regNo = (%s)',(session['username'],))
    typee=cur.fetchall()
    #return typee
    typ=typee[0][0]

    if typ=='UG':
       cur.execute('SELECT * from UG WHERE regNo = (%s)',(session['username'],))
       ugdetails=cur.fetchall()
       flash("Profile Updated")
       return render_template('view.html',details=details,ugdetails=ugdetails)
    else:
       cur.execute('SELECT * from PG WHERE regNo = (%s)',(session['username'],))
       pgdetails=cur.fetchall()
       flash("Profile Updated")
       return render_template('view.html',details=details,pgdetails=pgdetails)



@app.route('/placed')
def placed():
    return render_template('placed.html')



@app.route('/view_jobs')
def view_jobs():
    if session.get("username") == None:
       return redirect(url_for('login'))


    cur = conn.cursor()
    cur.execute('SELECT regno FROM stats WHERE regno = %s',
                  (session['username'],))
    a=cur.fetchone()


    if a is not None:
        return redirect(url_for('placed'))


    cur = conn.cursor()

    cur.execute('SELECT * from Student WHERE regNo= (%s)', (str(session['username']),))
    x=cur.fetchall()

    if len(x)==0:
        return redirect(url_for('create'))




    cur.execute('SELECT type from Student WHERE regNo = (%s)',(session['username'],))
    typee=cur.fetchall()
    typ=typee[0][0]

    if typ=='UG':
       cur.execute('SELECT branch from UG WHERE regNo = (%s)',(session['username'],))
       branch=cur.fetchall()
       #return branch
       cur.execute('SELECT * from Job')
       jobs=cur.fetchall()
       #return jobs
       cur.execute('SELECT cgpa from Student WHERE regNo = (%s)',(session['username'],))
       cgpa=cur.fetchall()
       cur.execute('SELECT branch from UG WHERE regNo = (%s)',(session['username'],))
       branch=cur.fetchall()
     #  return str(branch[0][0])
       cur.execute('SELECT companies from applied WHERE regno = %s',(session['username'],))
       companies=cur.fetchall()

       #return str(companies[0][0])

       complist=companies[0][0].split(' ')


       #return jobs
       ejobs=[]

       for jb in jobs:
           #return str(jb)
           strcourses=jb[3].split("#")
           #returnstrcourses))
           l=[]
           flag=0
           for c in strcourses:
             # return c
              if str(c)==str(branch[0][0]) and float(cgpa[0][0])>=jb[4]:
                 # return "hello"
                  flag=1
                  break
           if flag==1:
              cur.execute('SELECT package from fulltime WHERE job_Id = (%s)',(jb[0],))
              ft=cur.fetchall()

              if ft:
                jb=list(jb)
                jb.append(str(ft[0][0]))
                jb=tuple(jb)
                ejobs.append(jb)
              else:
                cur.execute('SELECT salary,duration from internship WHERE job_Id = (%s)',(jb[0],))
                it=cur.fetchall()
                if it:
                  jb=list(jb)
                  jb.append(str(it[0][0]))
                  jb.append(str(it[0][1]))
                  jb=tuple(jb)
                  ejobs.append(jb)

       #return ejobs
       return render_template('viewjobs.html',ejobs=ejobs,complist=complist)

    else:
       cur.execute('SELECT branch from PG WHERE regNo = (%s)',(session['username'],))
       branch=cur.fetchall()
       cur.execute('SELECT * from Job')
       jobs=cur.fetchall()
       cur.execute('SELECT cgpa from Student WHERE regNo = (%s)',(session['username'],))
       cgpa=cur.fetchall()
       cur.execute('SELECT branch from PG WHERE regNo = (%s)',(session['username'],))
       branch=cur.fetchall()
       cur.execute('SELECT companies from applied WHERE regno = %s',(session['username'],))
       companies=cur.fetchall()

       complist=""
       if companies[0][0] is not None:
          complist=companies[0][0].split(' ')



      # return jobs

       ejobs=[]

       for jb in jobs:
           strcourses=jb[3].split("#")
           l=[]
           flag=0
           for c in strcourses:
              if str(c)==str(branch[0][0]) and float(cgpa[0][0])>=jb[4]:
                  flag=1
                  break
           if flag==1:
              cur.execute('SELECT package from fulltime WHERE job_Id = (%s)',(jb[0],))
              ft=cur.fetchall()

              if ft:
                jb=list(jb)
                jb.append(str(ft[0][0]))
                jb=tuple(jb)
                ejobs.append(jb)
              else:
                cur.execute('SELECT salary,duration from internship WHERE job_Id = (%s)',(jb[0],))
                it=cur.fetchall()
                if it:
                  jb=list(jb)
                  jb.append(str(it[0][0]))
                  jb.append(str(it[0][1]))
                  jb=tuple(jb)
                  ejobs.append(jb)

       #return ejobs
       return render_template('viewjobs.html',ejobs=ejobs,complist=complist)




@app.route('/applied/<string:id>', methods = ['POST','GET'])
def applied(id):
    cur=conn.cursor()



    cur.execute('SELECT companies from applied WHERE regno = %s',(session['username'],))
    companies=cur.fetchall()

    comps=""
    temp=" "

    for s in companies:
        comps=comps+" "
        if s[0] is not None:
           comps=comps+s[0]
        #return comps
    comps=comps+" ";
    comps=comps+str(id)

    #return comps

    cur.execute('UPDATE applied SET companies = %s WHERE regno = %s',(comps,session['username'],))

    cur.execute('SELECT companies from applied WHERE regno = %s',(session['username'],))
    companies=cur.fetchall()

    #return str(companies[0][0])

    complist=companies[0][0].split(' ')
    #return complist

    return redirect(url_for('view_jobs'))



@app.route('/go_to_view_jobs')
def go_to_view_jobs():
    cursor = conn.cursor(dictionary=True)

    # Fetch the companies from the 'applied' table where regno matches the session's username
    cursor.execute('SELECT companies FROM applied WHERE regno = %s', (session['username'],))
    companies = cursor.fetchall()

    if companies:
        # Extract the list of companies by splitting the stored string
        complist = companies[0]['companies'].split('#')  # Assuming companies are stored as a # separated string

        # Pass the list of companies to the template to render them
        return render_template('view_jobs.html', companies=complist)
    else:
        flash("No applied companies found.")
        return redirect(url_for('home'))  # Redirect to home or another relevant page

    cursor.close()



@app.route('/viewstat')
def viewstat():
    cur = conn.cursor(dictionary=True)

    s = "SELECT Student.regNo, Student.firstName, Student.lastName, job.job_Id, job.company, job.type, job.position,fulltime.package FROM job,Student,stats,fulltime where Student.regNo=stats.regNo and fulltime.job_Id=stats.job_Id and job.job_Id=stats.job_Id;"
    cur.execute(s) # Execute the SQL
    list_users = cur.fetchall()
    s = "SELECT Student.regNo, Student.firstName, Student.lastName, job.job_Id, job.company, job.type, job.position, internship.salary FROM job,Student,stats,internship where Student.regNo=stats.regNo and internship.job_Id=stats.job_Id and job.job_Id=stats.job_Id;"
    cur.execute(s) # Execute the SQL
    intern = cur.fetchall()
    s="SELECT avg(package) from fulltime,stats where fulltime.job_Id=stats.job_Id;"
    cur.execute(s)
    avg=cur.fetchone()
    s="SELECT min(package) from fulltime,stats where fulltime.job_Id=stats.job_Id;"
    cur.execute(s)
    lowest=cur.fetchone()
    s="SELECT max(package) from fulltime,stats where fulltime.job_Id=stats.job_Id;"
    cur.execute(s)
    highest=cur.fetchone()
    s="SELECT count(stats.job_Id) from stats,UG,fulltime where stats.regNo=UG.regNo and stats.job_id=fulltime.job_Id;"
    cur.execute(s)
    btech=cur.fetchone()
    s="SELECT count(stats.job_Id) from stats,PG,fulltime where stats.regNo=PG.regNo and  stats.job_id=fulltime.job_Id  and Not PG.branch='Master in Computer Applications';"
    cur.execute(s)
    mtech=cur.fetchone()
    s="SELECT count(stats.job_Id) from stats,PG,fulltime where stats.regNo=PG.regNo and PG.branch='Master in Computer Applications' and stats.job_id=fulltime.job_Id;"
    cur.execute(s)
    mca=cur.fetchone()
    s="SELECT count(stats.job_Id) from stats,fulltime where stats.job_Id=fulltime.job_id;"
    cur.execute(s)
    full=cur.fetchone()
    s="SELECT count(stats.job_Id) from stats,internship where stats.job_Id=internship.job_id;"
    cur.execute(s)
    inter=cur.fetchone()
    s="SELECT count(student.regno) from student;"
    cur.execute(s)
    noplace=cur.fetchone()
    ft=full[0]
    i=inter[0]
    np=noplace[0]
    np=np-ft-i
    m=mca[0]
    mt=mtech[0]
    bt=btech[0]
    low=lowest[0]
    high=highest[0]
    if avg:
        ave=avg[0]
        ave=str(ave)
    else:
        ave=0
    return render_template('stats.html', list_users = list_users,intern =intern,average=ave,lowest=low,highest=high,bt=bt,mt=mt,m=m,ft=ft,np=np,i=i)




@app.route('/add_stats', methods=['POST'])
def add_stats():
    if request.method == 'POST':
        session['job_id'] = request.form['job_Id']
        session['regno'] = request.form['regNo']
        cur = conn.cursor(dictionary=True)

        cur.execute('SELECT regNo FROM Student WHERE regNo = %s',
                      (session['regno'],))
        ab=cur.fetchone()
        cur.execute('SELECT job_Id FROM Job WHERE job_Id = %s',
                      (session['job_id'],))
        jb=cur.fetchone()
        if jb:
            if ab:
                cur.execute('SELECT regno FROM stats WHERE regno = %s',
                            (session['regno'],))
                a=cur.fetchone()
                if a:
                    flash("Student already exists")
                else:
                    cur.execute('INSERT INTO stats (job_id, regno)'
                                    'VALUES (%s, %s)',
                                    (session['job_id'], session['regno']))
                    conn.commit()
                    flash("Student Added Successfully")
            else:
                flash("Student Doesn't Exist")
        else:
                flash("Job Doesn't Exist")
    return redirect(url_for('viewstat'))





@app.route('/deletestat/<string:id>', methods = ['POST','GET'])
def delete_stat(id):
    cur = conn.cursor()

    cur.execute('DELETE FROM stats WHERE regno = %s',
                (id,))
    conn.commit()
    flash('Student Removed Successfully')
    return redirect(url_for('viewstat'))
if __name__ == '__main__':
    app.run(debug=True)

