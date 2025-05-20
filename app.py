from flask import Flask,request,redirect,url_for,render_template,flash
from flask_login import LoginManager, login_user,logout_user,current_user,login_required
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_migrate import Migrate
from flask import send_from_directory
from sqlalchemy import not_
from sqlalchemy import or_


from werkzeug.utils import secure_filename
import os
basedir = os.path.abspath(os.path.dirname(__file__))

UPLOAD_FOLDER = 'uploads/resumes'
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt'}





from models import db,User,Job,Application,SavedJob

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///job_portal.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


app.config['UPLOAD_FOLDER'] = os.path.join(basedir, 'uploads','resumes')

db.init_app(app)
migrate=Migrate(app,db)

login_manager=LoginManager()
login_manager.login_view='login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Register Route
# --------------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form['full_name']
        email = request.form['email']
        password = request.form['password']
        user_type = request.form['user_type']
        

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered')
            return redirect(url_for('register'))

        hashed_pw = generate_password_hash(password)
        new_user = User(full_name=full_name, email=email, password=hashed_pw, user_type=user_type)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! You can now log in.')
        return redirect(url_for('login'))

    return render_template('register.html')

# --------------------
# Login Route
# --------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Login successful!','success')

            user_type = user.user_type.strip().lower()


            # Redirect based on user type

            if user_type == 'job_seeker':
                return redirect(url_for('job_seeker_dashboard'))
            elif user_type == 'employer':
                return redirect(url_for('employer_dashboard'))
            elif user_type == 'admin':
                # print("USER TYPE:", user.user_type)
                # flash(f"Detected user type: {user.user_type}")


                return redirect(url_for('admin_dashboard'))


        flash('Invalid email or password.')
    return render_template('login.html')

# --------------------
#job seeker Dashboard 
# --------------------

@app.route('/job_seeker_dashboard')
@login_required
def job_seeker_dashboard():
    jobs=Job.query.all()
    user=current_user
    return render_template('job_seeker_dashboard.html', jobs=jobs,user=user)

# --------------------
#employer Dashboard 
# --------------------

@app.route('/employer_dashboard')
@login_required
def employer_dashboard():
    if current_user.user_type != 'employer':
        flash('Access denied', 'danger')
        return redirect(url_for('login'))

    selected_job_id = request.args.get('job_id', type=int)
    
    # If a job_id is selected, filter jobs by that ID and employer_id
    if selected_job_id:
        jobs = Job.query.filter_by(employer_id=current_user.id, id=selected_job_id).all()
    else:
        # Otherwise, get all jobs for this employer
        jobs = Job.query.filter_by(employer_id=current_user.id).all()
    
    return render_template('employer_dashboard.html', jobs=jobs, selected_job_id=selected_job_id)


# --------------------
# admin Dashboard 
# --------------------

@app.route('/admin_dashboard')
@login_required
def admin_dashboard():
    if current_user.user_type.strip().lower() != 'admin':
        flash('Access denied', 'danger')
        return redirect(url_for('login'))

    user_search = request.args.get('user_search', '', type=str).strip()
    job_search = request.args.get('job_search', '', type=str).strip()

    # Filter Users
    users_query = User.query
    if user_search:
        users_query = users_query.filter(
            db.or_(
                # User.full_name.ilike(f"%{user_search}%"),
                # User.email.ilike(f"%{user_search}%"),
                User.user_type.ilike(f"%{user_search}%")
            )
        )
    users = users_query.all()

    # Filter Jobs
    jobs_query = Job.query
    if job_search:
        jobs_query = jobs_query.filter(
            db.or_(
                Job.title.ilike(f"%{job_search}%"),
                # Job.company.ilike(f"%{job_search}%"),
                Job.location.ilike(f"%{job_search}%")
            )
        )
    jobs = jobs_query.all()

    return render_template('admin_dashboard.html', users=users, jobs=jobs,
                           user_search=user_search, job_search=job_search)




# --------------------
# Home
# --------------------

@app.context_processor
def inject_now():
    return {'current_year': datetime.now().year}

@app.route('/')
def home():
    latest_jobs = Job.query.order_by(Job.id.desc()).limit(5).all()
    return render_template('home.html', latest_jobs=latest_jobs)

# --------------------
# post jobs
# --------------------


@app.route('/post-job',methods=['POST','GET'])
@login_required
def post_job():
    if request.method == 'POST':
       title = request.form.get('title')
       description = request.form.get('description')
       salary = request.form.get('salary')
       location = request.form.get('location')
       company_name = request.form.get('company_name')
       openings = request.form.get('openings')
       
    
       new_job = Job(title=title,description=description,salary=salary,location=location,company_name=company_name,openings=openings,employer_id=current_user.id)
       db.session.add(new_job)
       db.session.commit()
       flash('the job is posted successfully','success')
       return redirect(url_for('post_job'))
    return render_template('post_job.html')

# --------------------
# view job
# --------------------

@app.route('/job/<int:job_id>')
def job_detail(job_id):
    job = Job.query.get_or_404(job_id)
    return render_template('job_detail.html', job=job)

# --------------------
# search job
# --------------------




@app.route('/search')
def search_jobs():
    title = request.args.get('title', '').strip()
    location = request.args.get('location', '').strip().lower()

    if not title and not location:
        flash("Please enter a job title or location to search.", "warning")
        return redirect(url_for('job_seeker_dashboard'))

    query = Job.query

    # Enhanced title matching: match individual keywords
    if title:
        keywords = title.lower().split()
        keyword_filters = [Job.title.ilike(f'%{kw}%') for kw in keywords]
        query = query.filter(or_(*keyword_filters))

    # Location filter
    if location == 'onsite':
        query = query.filter(
            ~Job.location.ilike('%remote%'),
            ~Job.location.ilike('%hybrid%')
        )
    elif location:
        query = query.filter(Job.location.ilike(f'%{location}%'))

    jobs = query.all()
    return render_template('search_results.html', jobs=jobs, title=title, location=location)


# --------------------
# apply for  job
# --------------------

@app.route('/resumes/<filename>')
def uploaded_resume(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/apply/<int:job_id>',methods=['GET','POST'])
def apply_job(job_id):


    job = Job.query.get_or_404(job_id)

    # Prevent applying if job is closed
    if not job.accepting_applications:
        flash("This job is no longer accepting applications.", "warning")
        return redirect(url_for('job_detail', job_id=job.id))

    if request.method == 'POST':
        # Check if the post request has the file part
        if 'resume' not in request.files:
            flash('No resume file part', 'danger')
            return redirect(request.url)

        file = request.files['resume']
        cover_letter = request.form.get('cover_letter')

        # If user does not select file, browser may submit empty part
        if file.filename == '':
            flash('No selected file', 'danger')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            file.save(save_path)

            # Save the application to database
            new_application = Application(
                resume=filename,  
                cover_letter=cover_letter,
                job_seeker_id=current_user.id,
                job_id=job_id
            )
            db.session.add(new_application)

            saved = SavedJob.query.filter_by(job_id=job_id, job_seeker_id=current_user.id).first()
            if saved:
               db.session.delete(saved)

            db.session.commit()

            flash('Application submitted successfully!', 'success')
            return redirect(url_for('job_seeker_dashboard'))
        else:
            flash('Invalid file type. Allowed types: pdf, doc, docx, txt', 'danger')
            return redirect(request.url)

    return render_template('apply_job.html', job_id=job_id)


# --------------------
# view applicants for  job
# --------------------

@app.template_filter('basename')
def basename_filter(path):
    return os.path.basename(path)

@app.route('/employer/applicants')
@login_required
def view_applicants():
    if current_user.user_type != 'employer':
        return "Unauthorized", 403

    # Get all jobs posted by the current employer
    jobs = Job.query.filter_by(employer_id=current_user.id).all()

    # Optional job_id filter from query parameters
    job_id = request.args.get('job_id', type=int)

    if job_id:
        applications = Application.query.filter_by(job_id=job_id).all()
    else:
        job_ids = [job.id for job in jobs]
        applications = Application.query.filter(Application.job_id.in_(job_ids)).all()

    return render_template('view_applicants.html', applications=applications, jobs=jobs, selected_job_id=job_id)

# --------------------
# delete users from admin page
# --------------------

@app.route('/delete_user/<int:user_id>')
@login_required
def delete_user(user_id):
    if current_user.user_type.strip().lower() != 'admin':
        flash('Access denied', 'danger')
        return redirect(url_for('login'))

    user = User.query.get_or_404(user_id)

    #  prevent admin from deleting themselves
    if user.id == current_user.id:
        flash("You can't delete yourself.", 'warning')
        return redirect(url_for('admin_dashboard'))
     #  prevent admin from deleting other admins

    if user.user_type.strip().lower() == 'admin':
        flash("Cannot delete another admin account.", 'danger')
        return redirect(url_for('admin_dashboard'))
    

    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully.', 'success')
    return redirect(url_for('admin_dashboard'))

# --------------------
# delete jobs from admin page
# --------------------


@app.route('/delete_job/<int:job_id>')
@login_required
def delete_job(job_id):
    if current_user.user_type.strip().lower() != 'admin':
        flash('Access denied', 'danger')
        return redirect(url_for('login'))

    job = Job.query.get_or_404(job_id)
    db.session.delete(job)
    db.session.commit()
    flash('Job deleted successfully.', 'success')
    return redirect(url_for('admin_dashboard'))


# --------------------
# view 'my applications' on job seeker dashboard
# --------------------

@app.route('/my-applications')
@login_required
def my_applications():
    applications = Application.query.filter_by(job_seeker_id=current_user.id).all()

    for app in applications:
        if app.status == 'pending':
            app.status = 'received'

    db.session.commit()
    return render_template('my_applications.html', applications=applications,user=current_user)

# --------------------
# save a job on job seeker dashboard
# --------------------

@app.route('/save-job/<int:job_id>', methods=['POST'])
@login_required
def save_job(job_id):
    existing = SavedJob.query.filter_by(job_id=job_id, user_id=current_user.id).first()
    if existing:
        flash('Job already saved.', 'info')
    else:
        saved = SavedJob(job_id=job_id, user_id=current_user.id)
        db.session.add(saved)
        db.session.commit()
        flash('Job saved successfully.', 'success')
    return redirect(url_for('job_seeker_dashboard'))   

# --------------------
# view saved jobs
# --------------------

@app.route('/saved-jobs')
@login_required
def saved_jobs():
    jobs = SavedJob.query.filter_by(user_id=current_user.id).all()
    return render_template('saved_jobs.html', saved_jobs=jobs)

# --------------------
# checklist for job status
# --------------------

@app.route('/toggle_accepting_applications/<int:job_id>', methods=['POST'])
@login_required
def toggle_accepting_applications(job_id):
    job = Job.query.get_or_404(job_id)
    job.accepting_applications = 'accepting_applications' in request.form
    db.session.commit()
    return redirect(url_for('employer_dashboard'))


#  --------------------
# job details in employer dashboard
# --------------------

@app.route('/employer/job/<int:job_id>')
def employer_job_detail(job_id):
    job = Job.query.get_or_404(job_id)
    return render_template('job_detail_employer.html', job=job)



#  --------------------
# add profile
# --------------------



@app.route('/profile')
@login_required
def profile():
    user = current_user
    return render_template('profile.html', user=user)










    
   





        

# --------------------
# Logout
# --------------------
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('login'))

# --------------------
# Run the App
# --------------------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  
    app.run(debug=True)    