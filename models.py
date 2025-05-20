from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime


db=SQLAlchemy()

class User(UserMixin,db.Model):
    id=db.Column(db.Integer,primary_key=True)
    email=db.Column(db.String(100),unique=True,nullable=False)
    password=db.Column(db.String(128),nullable=False)
    full_name=db.Column(db.String(100))
    user_type=db.Column(db.String(20),nullable=False)
    created_at=db.Column(db.DateTime,default=datetime.utcnow)

    jobs=db.relationship('Job',backref='employer',lazy=True)
    applications=db.relationship('Application',backref='applicant',lazy=True)



class Job(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    employer_id=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    title=db.Column(db.String(100),nullable=False)
    description=db.Column(db.Text,nullable=False)
    salary=db.Column(db.Numeric(10,2))
    location=db.Column(db.String(100))
    category=db.Column(db.String(100))
    company_name=db.Column(db.String(100)) 
    posted_at=db.Column(db.DateTime,default=datetime.utcnow) 
    openings=db.Column(db.Integer, nullable=True)
    accepting_applications=db.Column(db.Boolean,default=True)

     


    applications=db.relationship('Application',backref='job',lazy=True,cascade="all, delete-orphan")


class Application(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    job_id=db.Column(db.Integer,db.ForeignKey('job.id'),nullable=False)
    job_seeker_id=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    resume=db.Column(db.Text)
    cover_letter=db.Column(db.Text)
    applied_at=db.Column(db.DateTime,default=datetime.utcnow)
    status=db.Column(db.String(20),default='pending')

    
    job_seeker = db.relationship('User', backref='job_applications', lazy=True)
    


    __table_args__=(db.UniqueConstraint('job_id','job_seeker_id',name='unique_application'),)



class SavedJob(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    saved_at = db.Column(db.DateTime, default=datetime.utcnow)

    job = db.relationship('Job', backref='saved_by')
    user = db.relationship('User', backref='saved_jobs')

    __table_args__ = (db.UniqueConstraint('job_id', 'user_id', name='unique_saved_job'),)

