import os
from werkzeug.utils import secure_filename
from flask import Flask, flash, request, redirect, render_template, url_for
from flask_pymongo import PyMongo
from bson.objectid import ObjectId



############################################################
# SETUP
############################################################

# File upload
UPLOAD_FOLDER = 'static/resumes/'
ALLOWED_EXTENSIONS = {'docx', 'pdf', 'txt', 'doc', 'docm', 'odt', 'rtf', 'epub', 'zip'}

app = Flask(__name__)

app.config["MONGO_URI"] = "mongodb://localhost:27017/eviction_provention"
mongo = PyMongo(app)

# Config File Upload
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

############################################################
# ROUTES
############################################################

# file Upload func
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def tenant_list():
    """Display the plants list page."""

    # database call to retrieve *all*
    # tenats from the Mongo database's `tenats` collection.
    tenant_data = mongo.db.tenants.find({})

    print("----------------------")
    print(tenant_data.count())
    print("----------------------")

    if tenant_data.count() != 0:
        tenant_id = tenant_data[0]['_id']

        context = {
            'tenants': tenant_data,
            'tenant_id': tenant_id
        }
    else:
        context = {
            'tenants': '',
            'tenant_id': ''
        }

    return render_template('detail.html', **context)

@app.route('/create', methods=['GET', 'POST'])
def create():
    """Display the tenet creation page & process data from the creation form."""

    tenant_data = mongo.db.tenants.find({})

    if request.method == 'POST':
        #New tenant's name, resume, Job Titles
        # stored in the object below.

        ### File Upload ###
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(url_for('detail', tenant_id=results_id))
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(url_for('detail', tenant_id=results_id))
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            print('-------------------')
            print(filename)
            print('-------------------')
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            new_tenant = {
                'name': request.form.get('tenant_name'),
                'resume': '/static/resumes/' + filename,
                'job_titles': request.form.get('job_titles').split(',')
            }
            # `insert_one` database call to insert the object into the
            # database's `tenant` collection, and get its inserted id. Passes the 
            # inserted id into the redirect call below.

            results = mongo.db.tenants.insert_one(new_tenant)
            results_id = results.inserted_id 

            return redirect(url_for('detail',
                                    filename=filename, 
                                    tenant_id=results_id))
    else:

        context = {
            'tenants': tenant_data,
        }

        return render_template('create.html', **context)

@app.route('/tenant/<tenant_id>')
def detail(tenant_id):
    """Display the tenat detail page & process data from the jobs form."""

    # Database call to retrieve *one*
    # tenant from the database, whose id matches the id passed in via the URL.
    print("----------------------")
    tenant_to_show = mongo.db.tenants.find_one({'_id': ObjectId(tenant_id)})
    
    # `find` database operation to find all jobs for the
    # tenants's id.
    # jobs = list(mongo.db.tenatns.find({'tenat_id':tenant_id}))

    tenant_data = mongo.db.tenants.find({})
    jobs = mongo.db.jobs.find({})
    events = mongo.db.hiring_events.find({})

    print("----------------------")
    print(tenant_to_show, 'here')
    print("----------------------")

    context = {
        'tenant' : tenant_to_show['name'],
        'resume' : tenant_to_show['resume'],
        'job_titles' : tenant_to_show['job_titles'],
        'tenants': tenant_data,
        'tenant_id': tenant_to_show['_id'],
        'num_jobs': jobs.count(),
        'num_events': events.count(),
        'jobs': jobs,
        'events': events
    }
    return render_template('detail.html', **context)

@app.route('/resume/<tenant_id>')
def resume(tenant_id):
    """Display the resume page."""

    # Database call to retrieve *one*
    # tenant from the database, whose id matches the id passed in via the URL.
    tenant_to_show = mongo.db.tenants.find_one({'_id': ObjectId(tenant_id)})

    print(tenant_to_show)

    tenant_data = mongo.db.tenants.find({})

    if request.method == 'POST':
     ### File Upload ###
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(url_for('resume', tenant_id=results_id))
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(url_for('resume', tenant_id=results_id))
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            print('-------------------')
            print(filename)
            print('-------------------')
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            new_tenant = {
                    'tenants': tenant_data,
                    'name': request.form.get('tenant_name'),
                    'resume': '/static/resumes/' + filename,
                    'tenant_id': tenant_to_show['_id']
            }
            # `insert_one` database call to insert the object into the
            # database's `tenant` collection, and get its inserted id. Passes the 
            # inserted id into the redirect call below.

            results = mongo.db.tenants.insert_one(new_tenant)
            results_id = results.inserted_id 

            return redirect(url_for('resume',
                                    filename=filename, 
                                    tenant_id=results_id))
    else:

        context = {
            'resume' : tenant_to_show['resume'],
            'tenants': tenant_data,
            'tenant_id': tenant_to_show['_id']
        }

        return render_template('resume.html', **context)


@app.route('/job_titles/<tenant_id>', methods=['GET', 'POST'])
def job_titles(tenant_id):
    """Display the tenet creation page & process data from the creation form."""

    tenant_data = mongo.db.tenants.find({})
    tenant_to_show = mongo.db.tenants.find_one({'_id': ObjectId(tenant_id)})

    if request.method == 'POST':

        job_titles = list(request.form.getlist('job_titles'))

        tenant = {
            'name' : tenant_to_show['name'],
            'resume' : tenant_to_show['resume'],
            'job_titles': job_titles
        }

        mongo.db.tenants.update_one( {'_id': ObjectId(tenant_id)}, {'$set': tenant})

        print(job_titles)

        return redirect(url_for('detail',tenant_id = tenant_id))

    else:

        context = {
            'name' : tenant_to_show['name'],
            'tenants': tenant_data,
            'tenant_id': tenant_to_show['_id'],
            'job_titles': tenant_to_show['job_titles']
        }

        return render_template('job_titles.html', **context)

@app.route('/jobs/<tenant_id>', methods=['GET', 'POST'])
def jobs(tenant_id):
    """Display the avalable jobs for the tenet to pice from."""

    tenant_data = mongo.db.tenants.find({})
    tenant_to_show = mongo.db.tenants.find_one({'_id': ObjectId(tenant_id)})
    

    if request.method == 'POST':

        context = {
            'job_titles': request.form.get('job_titles').split(',')
        }

        return redirect(url_for('jobs', **context))

    else:

        job_titles = tenant_to_show['job_titles']

        jobs = mongo.db.jobs.find({})
        
        # small_description = ""
        # num = 0
        # for job in jobs:
        #     for l in job.description:
        #         if num > 20:
        #             break
        #         else:
        #             small_description += l


        context = {
            'tenants': tenant_data,
            'tenant_id': tenant_to_show['_id'],
            'job_titles': tenant_to_show['job_titles'],
            'jobs': jobs
        }

        return render_template('jobs.html', **context)

@app.route('/hiring_events/<tenant_id>', methods=['GET', 'POST'])
def hiring_events(tenant_id):
    """Display the avalable hiring_events to pice from."""

    tenant_data = mongo.db.tenants.find({})
    tenant_to_show = mongo.db.tenants.find_one({'_id': ObjectId(tenant_id)})
    

    if request.method == 'POST':

        context = {
            'job_titles': request.form.get('job_titles').split(',')
        }

        return redirect(url_for('hiring_events', **context))

    else:

        job_titles = tenant_to_show['job_titles']

        events = mongo.db.hiring_events.find({})
        print(jobs)

        context = {
            'tenants': tenant_data,
            'tenant_id': tenant_to_show['_id'],
            'job_titles': tenant_to_show['job_titles'],
            'events': events
        }

        return render_template('hiring_events.html', **context)

@app.route('/notification/<tenant_id>', methods=['GET', 'POST'])
def notification(tenant_id):
    """Display the notification to pice from."""

    tenant_data = mongo.db.tenants.find({})
    tenant_to_show = mongo.db.tenants.find_one({'_id': ObjectId(tenant_id)})
    

    if request.method == 'POST':

        context = {
            'job_titles': request.form.get('job_titles').split(',')
        }

        return redirect(url_for('notification', **context))

    else:

        job_titles = tenant_to_show['job_titles']

        jobs = mongo.db.jobs.find({})
        print(jobs)

        context = {
            'tenants': tenant_data,
            'tenant_id': tenant_to_show['_id'],
            'job_titles': tenant_to_show['job_titles'],
            'jobs': jobs
        }

        return render_template('notification.html', **context)



# Delet 
@app.route('/delete/<tenant_id>', methods=['POST'])
def delete(tenant_id):
    # `delete_one` database call to delete the tenant with the given
    # id.
    mongo.db.tenants.delete_one({'_id': ObjectId(tenant_id)})

    return redirect(url_for('tenant_list'))


if __name__ == '__main__':
    app.run(debug=True)