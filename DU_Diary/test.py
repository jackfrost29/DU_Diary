import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import codecs

'''
mail = 'admin@cse.du.ac.bd'
department = 'Department of Computer Science and Engineering'
password = generate_password_hash('123456', method='sha256')

db = sqlite3.connect('/var/www/DU_Diary/DU_Diary/database.db')
cur = db.cursor()

cur.execute('insert into users(email, department, password) values(?, ?, ?);', (mail, department, password))
db.commit()
db.close()

s = 'sha256$d0m32bTq$b0080206d9e0c47e888da82ce6109b3150a48ec8c567ec2185634fc9ae92aef5'
'''


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def create_response():
    con = sqlite3.connect('database.db')
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

    with codecs.open('response.txt', 'w+', encoding='utf8') as file:
        file.write(s)

create_response()