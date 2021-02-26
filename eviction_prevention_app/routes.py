import os
from werkzeug.utils import secure_filename
from flask import Flask, flash, request, redirect, render_template, url_for, Blueprint
# from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from datetime import date, datetime
from flask_login import login_user, logout_user, login_required, current_user
from eviction_prevention_app import bcrypt

# -----models import-----
from eviction_prevention_app.models import Job, Event, User
from eviction_prevention_app import app, db
from eviction_prevention_app.forms import EventForm, JobForm, SignUpForm, LoginForm


############################################################
# SETUP
############################################################

#TODO switched from Mongo to SQL need to update file uploading
# File upload
UPLOAD_FOLDER = 'static/resumes/'
ALLOWED_EXTENSIONS = {'docx', 'pdf', 'txt', 'doc', 'docm', 'odt', 'rtf', 'epub', 'zip'}

# app = Flask(__name__)

main = Blueprint("main", __name__)
auth = Blueprint("auth", __name__)

app.config["SQL_URI"] = "mongodb://localhost:27017/eviction_provention"
# mongo = PyMongo(app)

#TODO switched from Mongo to SQL need to update file uploading
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

# file Upload func
#TODO switched from Mongo to SQL need to update file uploading
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

############################################################
# ROUTES
############################################################



@main.route('/')
def tenant_list():
    """Display the plants list page."""

    # database call 
    # tenant_data = mongo.db.tenants.find({})
    tenant_data = User.query.all()
    # jobs = mongo.db.jobs.find({})
    jobs = Job.query.all()
    # events = mongo.db.hiring_events.find({})
    events = Event.query.all()

    print("-------HERE--------",tenant_data)
    if len(tenant_data) != 0:
        tenant_id = tenant_data[0].id
    
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
        context = {
            'tenant': 'tenant_data[0]',
            'tenants': 'tenant_data',
            'tenant_id': 'tenant_id',
            'jobs': 'jobs',
            'events': 'events',
            'jobs_data': 'jobs_data'
        }
        return render_template('create.html', **context)

    

@main.route('/create', methods=['GET', 'POST'])
def create():
    """Display the tenet creation page & process data from the creation form."""

    # tenant_data = mongo.db.tenants.find({})
    tenant_data = User.query.all()
    pg_info = "Fill in the input filds and select a file to upload. For the Job Titles area you must seperate every job title with a comma."

    if request.method == 'POST':

        #TODO switched from Mongo to SQL need to update file uploading
        ### File Upload ###
        # check if the post request has the file part

        if 'file' not in request.files:
            flash('No file part')
            return redirect(url_for('main.create'))

        file = request.files['file']

        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(url_for('main.create'))
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))


            #TODO switched from Mongo to SQL need to update file uploading
            new_user = User(
                name=request.form.get('tenant_name'),
                resume='/static/resumes/' + filename,
                job_titles=request.form.get('job_titles').split(','),
                jobs=[]
            )

            # Insert the data into the DB
            db.session.add(new_user)
            db.session.commit()

            return redirect(url_for('main.detail',
                                    #TODO switched from Mongo to SQL need to update file uploading
                                    filename=filename, 
                                    tenant_id=new_user.id))
    else:

        context = {
            'tenants': tenant_data,
            'pg_info': pg_info
        }

        return render_template('create.html', **context)

@main.route('/tenant/<tenant_id>')
def detail(tenant_id):
    """Display the tenat detail page & process data from the jobs form."""

    # Database call 
    # tenant_to_show = mongo.db.tenants.find_one({'_id': ObjectId(tenant_id)})
    tenant_to_show = User.query.get(tenant_id)
    # tenant_data = mongo.db.tenants.find({})
    tenant_data = User.query.all()
    # jobs = mongo.db.jobs.find({})
    jobs = Job.query.all()
    # events = mongo.db.hiring_events.find({})
    events = Event.query.all()
    
    pg_info = "You are in a profile. On this page you can click on Resume, Job Titles, Jobs, Hiring Events, Notification, Delete & Save. If you click on the trash it will delte this profile. Alternatively when you press on the bell icon it will redirect you to the notifications page asocated with the profile you have open. All the rest will enter that specific area of this persons profile."

    jobs_data = tenant_to_show.jobs

    context = {
        'tenant' : tenant_to_show,
        'tenants': tenant_data,
        'num_jobs': len(jobs),
        'num_events': len(events),
        'jobs': jobs,
        'events': events,
        'pg_info': pg_info,
        'tenant_id': tenant_to_show.id,
        'jobs_data': jobs_data
    }
    return render_template('detail.html', **context)

@main.route('/resume/<tenant_id>', methods=['GET', 'POST'])
def resume(tenant_id):
    """Display the resume page."""

    # Database call to retrieve *one*
    # tenant from the database, whose id matches the id passed in via the URL.
    # tenant_to_show = mongo.db.tenants.find_one({'_id': ObjectId(tenant_id)})
    tenant_to_show = User.query.get(tenant_id)
    # tenant_data = mongo.db.tenants.find({})
    tenant_data = User.query.all()

    pg_info = "This is the Resume page where you can store the users resume. click the trsh button to delete the old resume & add a new one. Feel free to download the resume if you like by clicking the download button. Upload a new resume & it will atomatically delete your old one. Press the Save button to save the curent state."

    if request.method == 'POST':
    
        #TODO switched from Mongo to SQL need to update file uploading
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

            new_user = User(
                name=request.form.get('tenant_name'),
                #TODO switched from Mongo to SQL need to update file uploading
                resume='/static/resumes/' + filename,
                job_titles=request.form.get('job_titles').split(','),
                jobs=[]
            )

            # Insert the data into the DB
            db.session.add(new_user)
            db.session.commit()

            return redirect(url_for('resume', tenant_id=tenant_id))
    else:

        context = {
            #TODO switched from Mongo to SQL need to update file uploading
            'resume': tenant_to_show.resume,
            'tenants': tenant_data,
            'tenant_id': tenant_to_show.id,
            'pg_info': pg_info
        }

        return render_template('resume.html', **context)


@main.route('/job_titles/<tenant_id>', methods=['GET', 'POST'])
def job_titles(tenant_id):
    """Display the tenet creation page & process data from the creation form."""

    # tenant_data = mongo.db.tenants.find({})
    tenant_data = User.query.all()
    # tenant_to_show = mongo.db.tenants.find_one({'_id': ObjectId(tenant_id)})
    tenant_to_show = User.query.get(tenant_id)

    pg_info = "Here you can edit the job titles for this profile. press the red X to delte that title or type in the text field for add or edite a title. After you have it the way you want be sure to pres the save button so that you have all your date the way you want."

    if request.method == 'POST':

        # job_titles = list(request.form.getlist('job_titles'))
        job_titles = tenant_to_show.job_titles

        empty_str = '' in job_titles
        space_str = ' ' in job_titles
        while(empty_str):
            job_titles.remove('')
            empty_str = '' in job_titles
        while(space_str):
            job_titles.remove(' ')
            space_str = ' ' in job_titles

        user = User.query.filter_by(username=current_user.username).one()
        user.job_titles = job_titles

        return redirect(url_for('detail',tenant_id = tenant_id))

    else:

        
        context = {
            'name' : tenant_to_show.name,
            'tenants': tenant_data,
            'tenant_id': tenant_to_show.id,
            'job_titles': tenant_to_show.job_titles,
            'pg_info': pg_info
        }

        return render_template('job_titles.html', **context)

@main.route('/jobs/<tenant_id>', methods=['GET', 'POST'])
def jobs(tenant_id):
    """Display the avalable jobs for the tenet to pice from."""

    tenant_data = User.query.all()
    tenant_to_show = User.query.get(tenant_id)
    jobs = Job.query.all()
    
    pg_info = 'On this page you will find all the jobs that are avalable for the job titles you have selected. if you press "Apply" you will be able to enter the date when you applied. The file icon alows you to save a cover letter specific for that job. As you maybe able to see when you have applied to the job the "Apply" turns into "Applied" & a calender icon pops up. When you clic on the "Applied" icon you have the option to change the date you applied. The clender button will bring you to a page that will alow you to edit the alerts for that job & schedual reminders on the calender.'

    if request.method == 'POST':

        req_json = request.get_json()

        date_applied = req_json['date_applied']

        already_before = False
        for job in tenant_to_show.jobs:
            if job['job_id'] == req_json['job_id']:
                already_before = True

        if tenant_to_show.jobs != []:
            if already_before:
                for job in tenant_to_show.jobs:
                    if job['job_id'] == req_json['job_id']:

                        job['applied'] = True
                        job['date_applied'] = date_applied

                        user = User.query.filter_by(username=current_user.username).one()
                        user.jobs = tenant_to_show.jobs

            else:
                
                for job in jobs:
                    old_job_id = str(job['_id'])
                    new_job_id = req_json['job_id']

                    if str(job['_id']) == req_json['job_id']:
                        
                        newly_applied_job = {
                            'job_id': req_json['job_id'],
                            'job_title': job['job_title'],
                            'applied': True,
                            'date_applied': date_applied
                        }

                        user = User.query.filter_by(username=current_user.username).one()
                        user.jobs = tenant_to_show.jobs
        else:
            
            for job in jobs:
                if str(job['_id']) == req_json['job_id']:
                    newly_applied_job = {
                        'job_id': req_json['job_id'],
                        'job_title': job['job_title'],
                        'applied': True,
                        'date_applied': date_applied
                    }

                    tenant_to_show.jobs.append(newly_applied_job)

                    user = User.query.filter_by(username=current_user.username).one()
                    user.jobs = tenant_to_show.jobs

        jobs_data = tenant_to_show.jobs

        context = {
            'tenant': tenant_to_show,
            'jobs': jobs,
            'tenant_id': tenant_to_show.id,
            'pg_info': pg_info,
            'jobs_data': jobs_data
        }

        return redirect(url_for('jobs', **context))

    else:

        jobs_data = tenant_to_show.jobs

        context = {
            'tenants': tenant_data,
            'tenant': tenant_to_show,
            'tenant_id': tenant_to_show.id,
            'job_titles': tenant_to_show.job_titles,
            'jobs': jobs,
            'pg_info': pg_info,
            'jobs_data': jobs_data
        }

        return render_template('jobs.html', **context)

@main.route('/hiring_events/<tenant_id>', methods=['GET', 'POST'])
def hiring_events(tenant_id):
    """Display the avalable hiring_events to pice from."""

    # call data
    tenant_data = User.query.all()
    tenant_to_show = User.query.get(tenant_id)

    pg_info = "On this page you will find all the hiring events in your area that are associated with the job tiles chosen for this profile. You can click the links to be redirected to a site that can provide more info on the specifice event. Also to the left of the event name you will see the date & time of the event."

    if request.method == 'POST':

        context = {
            'job_titles': request.form.get('job_titles').split(',')
        }

        return redirect(url_for('hiring_events', **context))

    else:

        job_titles = tenant_to_show.job_titles

        events = Event.query.all()

        context = {
            'tenants': tenant_data,
            'tenant_id': tenant_to_show.id,
            'job_titles': tenant_to_show.job_titles,
            'events': events,
            'pg_info': pg_info
        }

        return render_template('hiring_events.html', **context)

@main.route('/notification/<tenant_id>', methods=['GET', 'POST'])
def notification(tenant_id):
    """Display the notification to pice from."""

    # DB calls
    tenant_data = User.query.all()
    tenant_to_show = User.query.get(tenant_id)

    pg_info = "The Notifications page is where you can edit your calender alerts & the setting for emails."
    

    if request.method == 'POST':

        context = {
            'job_titles': request.form.get('job_titles').split(','),
            'pg_info': pg_info
        }

        return redirect(url_for('notification', **context))

    else:

        job_titles = tenant_to_show.job_titles

        jobs = Job.query.all()

        context = {
            'tenants': tenant_data,
            'tenant_id': tenant_to_show.id,
            'job_titles': tenant_to_show.job_titles,
            'jobs': jobs,
            'pg_info': pg_info
        }

        return render_template('notification.html', **context)



# Delet 
@main.route('/delete/<tenant_id>', methods=['POST'])
def delete(tenant_id):
    # Database call to delete the tenant with the given id.
    # tenant_data = User.query.all()

    # for person in tenant_data:
    #     if person.id == tenant_id:
    user_to_del = User.query.get(tenant_id)
    db.session.delete(user_to_del)
    db.session.commit()

    return redirect(url_for('main.tenant_list'))


