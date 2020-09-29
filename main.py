from flask import Flask, request, redirect, render_template, url_for
from flask_pymongo import PyMongo
from bson.objectid import ObjectId

############################################################
# SETUP
############################################################

app = Flask(__name__)

app.config["MONGO_URI"] = "mongodb://localhost:27017/evictionProvention"
mongo = PyMongo(app)

############################################################
# ROUTES
############################################################

@app.route('/')
def tenant_list():
    """Display the plants list page."""

    # database call to retrieve *all*
    # tenats from the Mongo database's `tenats` collection.
    tenant_data = mongo.db.plants.find({})

    context = {
        'tenants': tenant_data,
    }
    return render_template('detail.html', **context)

@app.route('/create', methods=['GET', 'POST'])
def create():
    """Display the tenet creation page & process data from the creation form."""
    if request.method == 'POST':
        #New tenant's name, resume, Job Titles
        # stored in the object below.
        new_tenant = {
            'name': request.form.get('tenant_name'),
            'resume': request.form.get('resume'),
            'job_titles': request.form.get('job_titles'),
            'date_planted': request.form.get('date_planted')
        }
        # `insert_one` database call to insert the object into the
        # database's `tenant` collection, and get its inserted id. Passes the 
        # inserted id into the redirect call below.

        results = mongo.db.tenant.insert_one(new_tenant)
        results_id = results.inserted_id 

        return redirect(url_for('detail', plant_id=results_id))

    else:
        return render_template('create.html')

@app.route('/plant/<plant_id>')
def detail(tenant_id):
    """Display the tenat detail page & process data from the jobs form."""

    # Database call to retrieve *one*
    # tenant from the database, whose id matches the id passed in via the URL.
    tenant_to_show = mongo.db.tenants.find_one({'_id': ObjectId(tenant_id)})
    
    # `find` database operation to find all jobs for the
    # tenants's id.
    # jobs = list(mongo.db.tenatns.find({'tenat_id':tenant_id}))

    context = {
        'tenant' : tenant_to_show['name'],
        'resume' : tenant_to_show['resume'],
        'job_titles' : tenant_to_show['job_titles']
    }
    return render_template('detail.html', **context)

@app.route('/resume')
def about(tenatn_id):
    """Display the resume page."""

    # Database call to retrieve *one*
    # tenant from the database, whose id matches the id passed in via the URL.
    tenant_to_show = mongo.db.tenants.find_one({'_id': ObjectId(tenant_id)})

    context = {
        'resume' : tenant_to_show['resume']
    }

    return render_template('resume.html')