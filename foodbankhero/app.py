import re
import sqlite3

from flask import Flask, request, render_template, g, abort, flash, redirect
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired
from elasticapm.contrib.flask import ElasticAPM

app = Flask(__name__)
app.config['ELASTIC_APM'] = {
  'SERVICE_NAME': 'foodbankhero',

  # Set custom APM Server URL (default: http://localhost:8200)
  'SERVER_URL': 'http://apm-server:8200',
}
apm = ElasticAPM(app)

app.config['SECRET_KEY'] = 'verysecret'
ZIP_CODE_PATTERN = re.compile('^([\\d]+){5}(?:-([\\d]+){4})?$')
DATABASE = './db.db' # in docker that should end up /app/db.db


##### DATABASE UTILITIES

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

init_db()



##### APPLICATION CODE

class EditForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    items_needed = StringField('Items Needed', validators=[])
    address = StringField('Address', validators=[])
    zipcode = StringField('Zip Code', validators=[])

@app.route('/')
def home():
    return render_template('home.html', foodbanks=query_db('select * from foodbanks'))

@app.route('/edit/<int:foodbank_id>', methods=['POST', 'GET'])
def edit(foodbank_id):
    fb = query_db('select * from foodbanks where FoodBankId = ?', [foodbank_id], one=True)
    fb = fb if fb else abort(404)

    formdata = {}
    formdata['name'] = fb['Name']
    formdata['address'] = fb['Address']
    formdata['zipcode'] = fb['ZipCode']
    formdata['items_needed'] = fb['ItemsNeeded']

    form = EditForm(**formdata)

    if form.validate_on_submit():
        upd = {}
        upd['id'] = fb['FoodBankId']
        upd['name'] = form.name.data
        upd['address'] = form.address.data
        upd['zipcode'] = form.zipcode.data
        upd['items_needed'] = form.items_needed.data

        cur = get_db()
        cur.execute('''
update foodbanks set
Name = '{name}',
Address = '{address}',
ZipCode = '{zipcode}',
ItemsNeeded = '{items_needed}'
where FoodBankId = {id}'''.format(**upd))
        cur.commit()
        cur.close()

        flash("You've successfully updated {}".format(fb['Name']), 'success')
        return redirect('/')
    else:
        return render_template('edit.html', fb=fb, form=form)

@app.route('/validate_zip_code/<zip_code>')
def validate_zip_code(zip_code):
    return 'Seems correct' if ZIP_CODE_PATTERN.match(zip_code) else 'Seems wrong'
    #
    # validate_zip_code('28140')
    # validate_zip_code('28104a')
    # validate_zip_code('2810411111-111111111a')
    # validate_zip_code('111111111111111111112222111-1111331111111444111111111111a')
