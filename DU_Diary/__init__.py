import codecs
from flask import Flask, request, redirect, url_for, render_template, flash
from flask_api import status
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_required, current_user, login_user, LoginManager, UserMixin, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
import logging
from logging.handlers import RotatingFileHandler
import sqlite3
# import io
from .forms import LoginForm
# from .modules import User

# import sqlite3
app = Flask(__name__)
handler = RotatingFileHandler('/var/www/DU_Diary/DU_Diary/myapp.log', maxBytes=10000, backupCount=1)
handler.setLevel(logging.INFO)
# handler.setFormatter(Formatter('[%(levelname)s][%(asctime)s] %(message)s'))
app.logger.setLevel(logging.INFO)
app.logger.addHandler(handler)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////var/www/DU_Diary/DU_Diary/database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
db = SQLAlchemy(app)
sqlite_db_path = '/var/www/DU_Diary/DU_Diary/database.db'


# DATABASE = 'database.db'

class User(UserMixin, db.Model):

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True)
    department = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(200))

    def set_password(self, password):
        """Create hashed password."""
        self.password = generate_password_hash(password, method='sha256')

    def check_password(self, password):
        """Check hashed password."""
        return check_password_hash(self.password, password)

    def __repr__(self):
        return '<Email {}, Department {}>'.format(self.email, self.department)


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def create_response():
    con = sqlite3.connect(sqlite_db_path)
    con.row_factory = dict_factory
    cur = con.cursor()
    contact_list = cur.execute('select * from contacts;').fetchall()
    cur.close()
    con.close()
    s = "INSERT INTO contacts(name, designation, phone, email, department, faculty_institute) VALUES"

    for idx, _contact in enumerate(contact_list):

        s += "("

        s = s + "'" + _contact['name'] + "',"
        s = s + "'" + _contact['designation'] + "',"
        s = s + "'" + _contact['phone'] + "',"
        s = s + "'" + _contact['email'] + "',"
        s = s + "'" + _contact['department'] + "',"
        s = s + "'" + _contact['faculty_institute'] + "'"

        s += ")"

        if idx != len(contact_list)-1:
            s += ","

    s += ";"

    with codecs.open('/var/www/DU_Diary/DU_Diary/response.txt', 'w+', encoding='utf8') as file:
        file.write(s)


@login_manager.user_loader
def loadUser(id):
    return User.query.get(int(id))


@app.route('/', methods=['GET'])
def testing_get():
    return 'Connected...'


@app.route('/', methods=['POST'])
def testing():

    if request.form['key'] == '2015-816-782':
        data = ''
        with codecs.open('/var/www/DU_Diary/DU_Diary/response.txt', 'r', encoding='utf8') as file:
            data = file.read()
        return data
    else:
        return 'That\'s Illegal!', status.HTTP_401_UNAUTHORIZED


@app.route('/login', methods=['GET', 'POST'])
def login():

    # print >> environ['wsgi.errors'], "application debug #1"

    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    login_form = LoginForm()

    if request.method == 'POST' and login_form.validate_on_submit():

        email = login_form.email.data
        password = login_form.password.data
        app.logger.info(email)
        app.logger.info(password)
        user = User.query.filter_by(email=email).first()
        app.logger.info(user)
        if user and user.check_password(password):
            # login attempt successful
            app.logger.info("logged in successfully!")
            login_user(user)
            return redirect(url_for('dashboard'))

        flash('Invalid email/password combination.')
        return render_template('login.html', form=login_form)

    return render_template('login.html', form=login_form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You need to log-in for viewing the \'dashboard\'.')
    return redirect(url_for('login'))


# for now, show a header and give log out option
# well not anymore
@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    app.logger.info('waiting for dashboard...Entry point of function')
    if request.method == 'POST':
        con = sqlite3.connect(sqlite_db_path)
        con.row_factory = dict_factory
        app.logger.info(request.form)

        if 'update' in request.form:
            app.logger.info(request.form['update'])
            entry = request.form['update']
            values = entry.split(',')
            if int(values[0]) == -1:
                # then it's a new member
                _dept = current_user.department
                _fac = con.cursor().execute('select distinct faculty_institute from contacts where department = ?;', \
                    (current_user.department, )).fetchone()['faculty_institute']
                con.cursor().execute('insert into contacts(name, designation, phone, email, department, faculty_institute) values(?,?,?,?,?,?);',\
                    (values[1], values[2], values[3], values[4], _dept, _fac))

            else:
                # it's an existing member
                con.cursor().execute("update contacts set name = ?, designation = ?, phone = ?, email = ? where _id = ?;",\
                    (values[1], values[2], values[3], values[4], int(values[0])))
                # _id,name,designation,phone,email

            # after updating the datbase
            con.commit()
            con.close()
            create_response()
            return redirect(url_for('dashboard'))

        elif 'delete' in request.form:
            app.logger.info(request.form['delete'])
            _id = int(request.form['delete'])
            con = sqlite3.connect(sqlite_db_path)
            con.row_factory = dict_factory
            con.cursor().execute("delete from contacts where _id = ?;", (_id, ))
            con.commit()
            con.close()
            create_response()
            return redirect(url_for('dashboard'))

        elif 'cur_pass' in request.form:
            # it's a request for password change
            user = User.query.filter_by(id=current_user.id).first()
            if user.check_password(request.form['cur_pass']) and request.form['new_pass'] == request.form['retype_pass']:
                user.set_password(request.form['new_pass'])
                # password change attempt successful
                db.session.commit() # necessary to update the changed password, i was missing this line
                con.close()
                flash('Password change attempt succesfull.')
                return redirect(url_for('logout'))
            else:
                # invalid combination, alert the user
                contact_list = con.cursor().execute('select * from contacts where department = ?;', (current_user.department, )).fetchall()
                con.close()
                return render_template('dashboard.html', department=current_user.department, contacts=contact_list, flag="False")

        else:
            con.close()
            return 'Bad Request...', status.HTTP_400_BAD_REQUEST

    con = sqlite3.connect(sqlite_db_path)
    con.row_factory = dict_factory
    cur = con.cursor()
    contact_list = cur.execute('select * from contacts where department = ?;', (current_user.department, )).fetchall()
    cur.close()
    con.close()

    return render_template('dashboard.html', department=current_user.department, contacts=contact_list, flag="True")


if __name__ == "__main__":
    app.run()


# looks done
# 01-05-2020
# Alhamdulillah!

# looks like it's complete, including change password facility
# Alhamdulillah!