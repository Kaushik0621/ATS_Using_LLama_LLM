import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash
from process_pdf import get_answers_for_questions  # Import the PDF processing logic
from create_database import create_database  # Import the create_database function

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Secret key for session management
UPLOAD_FOLDER = 'uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

DATABASE = 'database.db'

def get_db():
    """Connect to the SQLite database."""
    conn = sqlite3.connect(DATABASE)
    return conn

def check_user(email, password=None):
    """Check if the user exists. If password is provided, also check if the password matches."""
    conn = get_db()
    cursor = conn.cursor()
    if password:
        cursor.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, password))
    else:
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    conn.close()
    return user

def add_user(email, password):
    """Add a new user to the database."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (email, password, submitted) VALUES (?, ?, 0)", (email, password))
    conn.commit()
    conn.close()

def update_submission_status(email):
    """Mark the user as having submitted an application."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET submitted = 1 WHERE email = ?", (email,))
    conn.commit()
    conn.close()

# Check if the database exists; if not, create it
if not os.path.exists(DATABASE):
    print("Database does not exist. Creating database...")
    create_database()

@app.route("/", methods=["GET", "POST"])
def login():
    """Login page for users."""
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        
        # Check user credentials
        user = check_user(email, password)
        if user:
            session['user'] = user[1]  # Store the email in the session
            if user[3] == 1:  # If the user has already submitted
                return render_template("submitted.html", email=email)  # Pass email to submitted page
            else:
                return redirect(url_for("upload_resume"))  # Redirect to resume upload page
        else:
            flash("Invalid credentials. Please try again.", "error")
            return redirect(url_for('login'))  # Show login page again with error message

    return render_template("login.html")  # Render the login page

@app.route("/create_account", methods=["GET", "POST"])
def create_account():
    """Create account page for new users."""
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']

        # Check if the user already exists
        existing_user = check_user(email)
        if existing_user:
            if existing_user[3] == 1:  # If the user has already submitted
                return render_template("submitted.html", email=email)  # Pass email to submitted page

        # Add the user to the database
        add_user(email, password)
        session['user'] = email  # Automatically log in the new user

        # Redirect to the PDF upload page after account creation
        return redirect(url_for('upload_resume'))

    return render_template("create_account.html")

@app.route("/upload_resume", methods=["GET", "POST"])
def upload_resume():
    """Page for uploading the resume, displaying the email at the top."""
    if 'user' not in session:
        return redirect(url_for('login'))  # Redirect to login if not logged in
    
    email = session['user']

    if request.method == "POST":
        file = request.files['resume']
        if file.filename == '':
            return "Please select a file."
        
        if file and file.filename.endswith('.pdf'):
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)

            # Process the PDF and get answers
            result = get_answers_for_questions(file_path)
            
            # Mark the user as having submitted
            update_submission_status(email)
            
            # Pass extracted details to the show_answers page
            return redirect(url_for('show_answers', **result))
    
    return render_template("upload_resume.html", email=email)  # Render the resume upload form with email

@app.route("/show_answers", methods=["GET", "POST"])
def show_answers():
    """Display the answers extracted from the resume."""
    if request.method == "POST":
        # Handle form submission logic here, like saving the input data
        return "Form submitted successfully!"

    # Extracted information passed as query parameters
    name = request.args.get('name', '')
    pn_number = request.args.get('pn_number', '')

    # Split education and work experience entries by semicolon for multiple institutions/experiences
    education = request.args.get('education', '').split(";")  # This will be a list of educational entries
    work_experience = request.args.get('work_experience', '').split(";")  # This will be a list of work experience entries
    skills = request.args.get('skills', '')

    return render_template("show_answers.html", name=name, pn_number=pn_number, 
                           education=education, work_experience=work_experience, skills=skills)


@app.route("/submit", methods=["POST"])
def submit_form():
    """Handle the form submission."""
    name = request.form.get('name')
    pn_number = request.form.get('pn_number')

    # Get all education data
    education_institutions = request.form.getlist('education_institution')
    education_courses = request.form.getlist('education_course')
    education_start_dates = request.form.getlist('education_start_date')
    education_end_dates = request.form.getlist('education_end_date')

    # Get all work experience data
    work_organizations = request.form.getlist('work_organization')
    work_roles = request.form.getlist('work_role')
    work_start_dates = request.form.getlist('work_start_date')
    work_end_dates = request.form.getlist('work_end_date')

    # Process the collected data here...
    # For example, saving the data to a database

    return "Form submitted successfully!"

if __name__ == "__main__":
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)
