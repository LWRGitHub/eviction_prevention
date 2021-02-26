from sqlalchemy_utils import URLType
from eviction_prevention_app import db
from eviction_prevention_app.utils import FormEnum

class TitleCategory(FormEnum):
    """Categories of Job Titles."""
    
    UX_UI_DESIGN = 'UI/UX Design'
    FULL_STACK_SOFTWARE_ENGINEER = 'Full Stack Software Engineer'
    FEW_SOFTWARE_ENGINEER = 'FEW Software Engineer'
    BEW_SOFTWARE_ENGINEER = 'BEW Software Engineer'
    OTHER = 'Other'

class Event(db.Model):
    """Grocery Store model."""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.PickleType)
    description = db.Column(db.String(200), nullable=False)
    address = db.Column(db.String(200), nullable=False)

     
    # who Created it
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_by = db.relationship('User')

    # Relationship
    # users_attending = db.relationship('User', secondary = 'event_list', back_populates = 'events_attending')

class Job(db.Model):
    """Job Item model."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    pay = db.Column(db.Float(precision=2), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(80), default=TitleCategory.OTHER)
    photo_url = db.Column(URLType)

    # who Created it
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_by = db.relationship('User')

    # Relationship
    # users_apllied = db.relationship('User', secondary = 'apllied_list', back_populates = 'apllied_to')
    

class User(db.Model):
    """User model."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    # password = db.Column(db.String(200), nullable=False)
    job_titles = db.Column(db.PickleType)
    # apllied_to = db.relationship('Job', secondary = 'apllied_list', back_populates = 'users_apllied')
    # events_attending = db.relationship('Event', secondary = 'event_list', back_populates = 'users_attending')
    resume = db.Column(db.String(200), nullable=False)

    #TODO remove these later & setup applied & events_attending
    jobs = db.Column(db.PickleType)

    # # Flask-Login integration
    # def is_authenticated(self):
    #     return True

    # def is_active(self): # line 37
    #     return True

    # def is_anonymous(self):
    #     return False

    # def get_id(self):
    #     return self.id

    # # Required for administrative interface
    # def __unicode__(self):
    #     return self.username


# apllied_table = db.Table('apllied_list',
#     db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
#     db.Column('job_id', db.Integer, db.ForeignKey('job.id'))
# )

# event_list_table = db.Table('event_list',
#     db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
#     db.Column('event_id', db.Integer, db.ForeignKey('event.id'))
# )