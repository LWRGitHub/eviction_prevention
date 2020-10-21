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
# Functions Used 
############################################################

def get_jobs_data(jobs, tenant_to_show):
    jobs_data = []
    jobs_list = list(jobs)
    for job_from_jobs in jobs_list:
        job = {}

        if len(job_from_jobs['job_title']) > 25:
            job['job_title'] = job_from_jobs['job_title'][0:25] + "..."
        else:
            job['job_title'] = job_from_jobs['job_title']
        job['description'] = job_from_jobs['description'][0:100] + '...'
        job['job_id'] = str(job_from_jobs['_id'])
        job['url'] = job_from_jobs['url']
        job['applied'] = False

        if tenant_to_show['jobs'] != []:
            for profile_job in tenant_to_show['jobs']:
                if str(job_from_jobs['_id']) == profile_job['job_id']:
                    if profile_job['applied']:
                        job['applied'] = True
        
        jobs_data.append(job)
    return jobs_data

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
    jobs = mongo.db.jobs.find({})
    events = mongo.db.hiring_events.find({})

    if tenant_data.count() != 0:
        tenant_id = tenant_data[0]['_id']
    
        jobs_data = get_jobs_data(jobs, tenant_data[0])

        context = {
            'tenant': tenant_data[0],
            'tenants': tenant_data,
            'tenant_id': tenant_id,
            'jobs': jobs,
            'events': events,
            'jobs_data': jobs_data
        }
        return render_template('detail.html', **context)
    else:
        return render_template('create.html', **context)

    

@app.route('/create', methods=['GET', 'POST'])
def create():
    """Display the tenet creation page & process data from the creation form."""

    tenant_data = mongo.db.tenants.find({})
    pg_info = "Fill in the input filds and select a file to upload. For the Job Titles area you must seperate every job title with a comma."

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
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            new_tenant = {
                'name': request.form.get('tenant_name'),
                'resume': '/static/resumes/' + filename,
                'job_titles': request.form.get('job_titles').split(','),
                'jobs': []
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
            'pg_info': pg_info
        }

        return render_template('create.html', **context)

@app.route('/tenant/<tenant_id>')
def detail(tenant_id):
    """Display the tenat detail page & process data from the jobs form."""

    # Database call to retrieve *one*
    # tenant from the database, whose id matches the id passed in via the URL.
    tenant_to_show = mongo.db.tenants.find_one({'_id': ObjectId(tenant_id)})
    
    # `find` database operation to find all jobs for the
    # tenants's id.
    # jobs = list(mongo.db.tenatns.find({'tenat_id':tenant_id}))

    tenant_data = mongo.db.tenants.find({})
    jobs = mongo.db.jobs.find({})
    events = mongo.db.hiring_events.find({})
    pg_info = "You are in a profile. On this page you can click on Resume, Job Titles, Jobs, Hiring Events, Notification, Delete & Save. If you click on the trash it will delte this profile. Alternatively when you press on the bell icon it will redirect you to the notifications page asocated with the profile you have open. All the rest will enter that specific area of this persons profile."

    jobs_data = get_jobs_data(jobs, tenant_to_show)

    print('-----------------')
    print(jobs_data)
    print('-----------------')

    context = {
        'tenant' : tenant_to_show,
        'tenants': tenant_data,
        'num_jobs': jobs.count(),
        'num_events': events.count(),
        'jobs': jobs,
        'events': events,
        'pg_info': pg_info,
        'tenant_id': tenant_to_show['_id'],
        'jobs_data': jobs_data
    }
    return render_template('detail.html', **context)

@app.route('/resume/<tenant_id>', methods=['GET', 'POST'])
def resume(tenant_id):
    """Display the resume page."""

    # Database call to retrieve *one*
    # tenant from the database, whose id matches the id passed in via the URL.
    tenant_to_show = mongo.db.tenants.find_one({'_id': ObjectId(tenant_id)})
    tenant_data = mongo.db.tenants.find({})
    pg_info = "This is the Resume page where you can store the users resume. click the trsh button to delete the old resume & add a new one. Feel free to download the resume if you like by clicking the download button. Upload a new resume & it will atomatically delete your old one. Press the Save button to save the curent state."

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
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            tenant = {
                    'name': tenant_to_show['name'],
                    'resume': '/static/resumes/' + filename,
                    'job_titles': tenant_to_show['job_titles']
            }
            # `insert_one` database call to insert the object into the
            # database's `tenant` collection, and get its inserted id. Passes the 
            # inserted id into the redirect call below.

            results = mongo.db.tenants.update_one( {'_id': ObjectId(tenant_id)}, {'$set': tenant})
            # results_id = results.inserted_id 

            return redirect(url_for('resume', tenant_id=tenant_id))
    else:

        context = {
            'resume' : tenant_to_show['resume'],
            'tenants': tenant_data,
            'tenant_id': tenant_to_show['_id'],
            'pg_info': pg_info
        }

        return render_template('resume.html', **context)


@app.route('/job_titles/<tenant_id>', methods=['GET', 'POST'])
def job_titles(tenant_id):
    """Display the tenet creation page & process data from the creation form."""

    tenant_data = mongo.db.tenants.find({})
    tenant_to_show = mongo.db.tenants.find_one({'_id': ObjectId(tenant_id)})
    pg_info = "Here you can edit the job titles for this profile. press the red X to delte that title or type in the text field for add or edite a title. After you have it the way you want be sure to pres the save button so that you have all your date the way you want."

    if request.method == 'POST':

        job_titles = list(request.form.getlist('job_titles'))

        empty_str = '' in job_titles
        space_str = ' ' in job_titles
        while(empty_str):
            job_titles.remove('')
            empty_str = '' in job_titles
        while(space_str):
            job_titles.remove(' ')
            space_str = ' ' in job_titles

        tenant = {
            'name' : tenant_to_show['name'],
            'resume' : tenant_to_show['resume'],
            'job_titles': job_titles,
        }

        mongo.db.tenants.update_one( {'_id': ObjectId(tenant_id)}, {'$set': tenant})

        print(job_titles)

        return redirect(url_for('detail',tenant_id = tenant_id))

    else:

        
        context = {
            'name' : tenant_to_show['name'],
            'tenants': tenant_data,
            'tenant_id': tenant_to_show['_id'],
            'job_titles': tenant_to_show['job_titles'],
            'pg_info': pg_info
        }

        return render_template('job_titles.html', **context)

@app.route('/jobs/<tenant_id>', methods=['GET', 'POST'])
def jobs(tenant_id):
    """Display the avalable jobs for the tenet to pice from."""

    tenant_data = mongo.db.tenants.find({})
    tenant_to_show = mongo.db.tenants.find_one({'_id': ObjectId(tenant_id)})
    jobs = mongo.db.jobs.find({})
    
    pg_info = 'On this page you will find all the jobs that are avalable for the job titles you have selected. if you press "Apply" you will be able to enter the date when you applied. The file icon alows you to save a cover letter specific for that job. As you maybe able to see when you have applied to the job the "Apply" turns into "Applied" & a calender icon pops up. When you clic on the "Applied" icon you have the option to change the date you applied. The clender button will bring you to a page that will alow you to edit the alerts for that job & schedual reminders on the calender.'

    if request.method == 'POST':

        # date_applied = request.form.get('date_applied')
        req_json = request.get_json()
        # print("-----------")
        # print(req_json)
        # print(req_json['job_id'])
        # print("-----------")
        date_applied = req_json['date_applied']

        already_before = False
        for job in tenant_to_show['jobs']:
            if job['job_id'] == req_json['job_id']:
                already_before = True

        # print("-----------")
        # print(date_applied)
        # print("-----------")

        if tenant_to_show['jobs'] != []:
            if already_before:
                for job in tenant_to_show['jobs']:
                    if job['job_id'] == req_json['job_id']:
                        print("-----------")
                        print('1')
                        print("-----------")

                        job['applied'] = True
                        job['date_applied'] = date_applied
                        tenant = {
                            'name': tenant_to_show['name'],
                            'resume': tenant_to_show['resume'],
                            'job_titles': tenant_to_show['job_titles'],
                            'jobs': tenant_to_show['jobs'],
                        }

                        results = mongo.db.tenants.update_one( {'_id': ObjectId(tenant_id)}, {'$set': tenant})
            else:
                print("-----------")
                print('2')
                print("-----------")
                for job in jobs:
                    old_job_id = str(job['_id'])
                    new_job_id = req_json['job_id']

                    print("-----------")
                    print('2: for')
                    print(old_job_id)
                    print(new_job_id)
                    print(type(str(job['_id'])))
                    print(type(req_json['job_id']))
                    print("-----------")

                    if str(job['_id']) == req_json['job_id']:
                        print("-----------")
                        print('2: if')
                        print("-----------")
                        newly_applied_job = {
                            'job_id': req_json['job_id'],
                            'job_title': job['job_title'],
                            'applied': True,
                            'date_applied': date_applied
                        }
                        
                        print("-----------")
                        print(tenant_to_show['jobs'])
                        print("-----------")
                        tenant_to_show['jobs'].append(newly_applied_job)
                        print("-----------")
                        print(tenant_to_show['jobs'])
                        print("-----------")

                        tenant = {
                            'name': tenant_to_show['name'],
                            'resume': tenant_to_show['resume'],
                            'job_titles': tenant_to_show['job_titles'],
                            'jobs': tenant_to_show['jobs'],
                        }
                        results = mongo.db.tenants.update_one( {'_id': ObjectId(tenant_id)}, {'$set': tenant})
        else:
            print("-----------")
            print('3')
            print("-----------")
            for job in jobs:
                if str(job['_id']) == req_json['job_id']:
                    newly_applied_job = {
                        'job_id': req_json['job_id'],
                        'job_title': job['job_title'],
                        'applied': True,
                        'date_applied': date_applied
                    }

                    tenant_to_show['jobs'].append(newly_applied_job)

                    tenant = {
                        'name': tenant_to_show['name'],
                        'resume': tenant_to_show['resume'],
                        'job_titles': tenant_to_show['job_titles'],
                        'jobs': tenant_to_show['jobs'],
                    }
                    results = mongo.db.tenants.update_one( {'_id': ObjectId(tenant_id)}, {'$set': tenant})



        # tenant = {
        #     'name': tenant_to_show['name'],
        # }

        jobs_data = get_jobs_data(jobs, tenant_to_show)

        context = {
            'tenant': tenant_to_show,
            'jobs': jobs,
            'tenant_id': tenant_to_show['_id'],
            'pg_info': pg_info,
            'jobs_data': jobs_data
        }

        return redirect(url_for('jobs', **context))

    else:

        jobs_data = get_jobs_data(jobs, tenant_to_show)

        context = {
            'tenants': tenant_data,
            'tenant': tenant_to_show,
            'tenant_id': tenant_to_show['_id'],
            'job_titles': tenant_to_show['job_titles'],
            'jobs': jobs,
            'pg_info': pg_info,
            'jobs_data': jobs_data
        }

        return render_template('jobs.html', **context)

@app.route('/hiring_events/<tenant_id>', methods=['GET', 'POST'])
def hiring_events(tenant_id):
    """Display the avalable hiring_events to pice from."""

    tenant_data = mongo.db.tenants.find({})
    tenant_to_show = mongo.db.tenants.find_one({'_id': ObjectId(tenant_id)})
    pg_info = "On this page you will find all the hiring events in your area that are associated with the job tiles chosen for this profile. You can click the links to be redirected to a site that can provide more info on the specifice event. Also to the left of the event name you will see the date & time of the event."

    if request.method == 'POST':

        context = {
            'job_titles': request.form.get('job_titles').split(',')
        }

        return redirect(url_for('hiring_events', **context))

    else:

        job_titles = tenant_to_show['job_titles']

        events = mongo.db.hiring_events.find({})

        context = {
            'tenants': tenant_data,
            'tenant_id': tenant_to_show['_id'],
            'job_titles': tenant_to_show['job_titles'],
            'events': events,
            'pg_info': pg_info
        }

        return render_template('hiring_events.html', **context)

@app.route('/notification/<tenant_id>', methods=['GET', 'POST'])
def notification(tenant_id):
    """Display the notification to pice from."""

    tenant_data = mongo.db.tenants.find({})
    tenant_to_show = mongo.db.tenants.find_one({'_id': ObjectId(tenant_id)})
    pg_info = "The Notifications page is where you can edit your calender alerts & the setting for emails."
    

    if request.method == 'POST':

        context = {
            'job_titles': request.form.get('job_titles').split(','),
            'pg_info': pg_info
        }

        return redirect(url_for('notification', **context))

    else:

        job_titles = tenant_to_show['job_titles']

        jobs = mongo.db.jobs.find({})

        context = {
            'tenants': tenant_data,
            'tenant_id': tenant_to_show['_id'],
            'job_titles': tenant_to_show['job_titles'],
            'jobs': jobs,
            'pg_info': pg_info
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