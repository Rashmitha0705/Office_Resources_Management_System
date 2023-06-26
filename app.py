from flask import Flask, render_template,request,flash,redirect,url_for,session
import sqlite3
from flask import url_for
import base64
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from io import BytesIO
from flask import jsonify

app = Flask(__name__, static_url_path='/static')
app.secret_key="123"

def create_database():
    # Connect to the SQLite database (if it exists) or create it
    conn = sqlite3.connect("database.db")
    conn.close()

create_database()

def create_tables():
    con = sqlite3.connect("database.db")
    print("Connected to database")

    con.execute("CREATE TABLE IF NOT EXISTS customer (pid INTEGER PRIMARY KEY, name TEXT, address TEXT, contact INTEGER, mail TEXT)")
    con.execute("CREATE TABLE IF NOT EXISTS requisitions (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, need_date TEXT, return_date TEXT, description TEXT, resources TEXT, quantity INTEGER, project_name TEXT, skills TEXT, customer_id INTEGER, status TEXT DEFAULT 'Pending', solved_requisition INTEGER)")
    con.execute("CREATE TABLE IF NOT EXISTS complaints (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, date TEXT, complaint TEXT, remarks TEXT, customer_id INTEGER)")
    con.close()
   

create_tables()


@app.route('/')
def Home():
    return render_template('Home.html')

@app.route('/index',methods=["GET","POST"])
def index():
    return render_template("index.html")

@app.route('/login',methods=["GET","POST"])
def login():
    if request.method=='POST':
        name=request.form['name']
        password=request.form['password']
        con=sqlite3.connect("database.db")
        con.row_factory=sqlite3.Row
        cur=con.cursor()
        cur.execute("select * from customer where name=? and mail=?",(name,password))
        data=cur.fetchone()

        if data:
            session["name"]=data["name"]
            session["mail"]=data["mail"]
            return redirect("customer")
        else:
            flash("Username and Password Mismatch","danger")
    return redirect(url_for("index"))


@app.route('/customer',methods=["GET","POST"])
def customer():
    return render_template("customer.html")

@app.route('/register',methods=['GET','POST'])
def register():
    if request.method=='POST':
        try:
            name=request.form['name']
            address=request.form['address']
            contact=request.form['contact']
            mail=request.form['mail']
            con=sqlite3.connect("database.db")
            cur=con.cursor()
            cur.execute("insert into customer(name,address,contact,mail)values(?,?,?,?)",(name,address,contact,mail))
            con.commit()
            flash("Record Added  Successfully","success")
        except:
            flash("Error in Insert Operation","danger")
        finally:
            return redirect(url_for("index"))
            con.close()

    return render_template('register.html')

@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'admin@123':
            # Redirect to admin dashboard if login is successful
            
            return redirect(url_for('admin_dashboard'))
        else:
            # Display error message if login fails
            
            return redirect(url_for('admin_login'))
    return render_template('admin_login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for("index"))

@app.route('/admin_dashboard')
def admin_dashboard():
    #num_notifications = get_num_notifications()
    # return render_template('admin_dashboard.html', num_notifications=num_notifications)
    
    return render_template('admin_dashboard.html')

def create_tables():
    con = sqlite3.connect("database.db")
    con.execute("CREATE TABLE IF NOT EXISTS customer (pid INTEGER PRIMARY KEY, name TEXT, address TEXT, contact INTEGER, mail TEXT)")
    con.execute("CREATE TABLE IF NOT EXISTS requisitions (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, need_date TEXT, return_date TEXT, description TEXT, resources TEXT, quantity INTEGER, project_name TEXT, skills TEXT, customer_id INTEGER, status TEXT DEFAULT 'Pending', solved_requisition INTEGER)")
    con.execute("CREATE TABLE IF NOT EXISTS complaints (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, date TEXT, complaint TEXT, remarks TEXT, customer_id INTEGER)")
    con.close()


@app.route('/request_resource', methods=["GET", "POST"])
def request_resource():
    if request.method == 'POST':
        name = request.form['name']
        need_date = request.form['need_date']
        return_date = request.form['return_date']
        description = request.form['description']
        resources = request.form['resources']
        quantity = request.form['quantity']
        project_name = request.form['project_name']
        skills = request.form['skills']
        customer_id = get_customer_id(session["mail"])  # Replace with your logic to get customer ID from session or database

        con = sqlite3.connect("database.db")
        cur = con.cursor()
        cur.execute("INSERT INTO requisitions (name, need_date, return_date, description, resources, quantity, project_name, skills, customer_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (name, need_date, return_date, description, resources, quantity, project_name, skills, customer_id))
        con.commit()
        con.close()

        
        return redirect(url_for("customer"))

    return render_template('request_resource.html')


@app.route('/edit_requisition/<int:id>', methods=["GET", "POST"])
def edit_requisition(id):
    
    if request.method == 'POST':
        name = request.form['name']
        need_date = request.form['need_date']
        return_date = request.form['return_date']
        description = request.form['description']
        resources = request.form['resources']
        quantity = request.form['quantity']
        project_name = request.form['project_name']
        skills = request.form['skills']
        
        con = sqlite3.connect("database.db")
        cur = con.cursor()
        cur.execute("UPDATE requisitions SET name=?, need_date=?, return_date=?, description=?, resources=?, quantity=?, project_name=?, skills=? WHERE id=?",
                    (name, need_date, return_date, description, resources, quantity, project_name, skills, id))
        con.commit()
        con.close()

        flash("Requisition Updated Successfully", "success")
        return redirect(url_for("my_requisitions"))

    con = sqlite3.connect("database.db")
    cur = con.cursor()
    cur.execute("SELECT * FROM requisitions WHERE id=?", (id,))
    requisition = cur.fetchone()
    con.close()

    return render_template('edit_requisition.html', requisition=requisition)


@app.route('/my_requisitions')
def my_requisitions():
    customer_id = get_customer_id(session["mail"])  # Replace with your logic to get customer ID from session or database

    con = sqlite3.connect("database.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("SELECT * FROM requisitions WHERE customer_id=?", (customer_id,))
    requisitions = cur.fetchall()
    con.close()

    return render_template('my_requisitions.html', requisitions=requisitions)


@app.route('/complaint', methods=["GET", "POST"])
def complaint():
    if request.method == 'POST':
        name = request.form['name']
        date = request.form['date']
        complaint = request.form['complaint']
        remarks = request.form['remarks']
        customer_id = get_customer_id(session["mail"])  # Replace with your logic to get customer ID from session or database

        con = sqlite3.connect("database.db")
        cur = con.cursor()
        cur.execute("INSERT INTO complaints (name, date, complaint, remarks, customer_id) VALUES (?, ?, ?, ?, ?)",
                    (name, date, complaint, remarks, customer_id))
        con.commit()
        con.close()

        
        return redirect(url_for("customer"))

    return render_template('complaint.html')


@app.route('/my_complaints')
def my_complaints():
    customer_id = get_customer_id(session["mail"])  # Replace with your logic to get customer ID from session or database

    con = sqlite3.connect("database.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("SELECT * FROM complaints WHERE customer_id=?", (customer_id,))
    complaints = cur.fetchall()
    con.close()

    return render_template('my_complaints.html', complaints=complaints)


def get_customer_id(mail):
    con = sqlite3.connect("database.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("SELECT pid FROM customer WHERE mail=?", (mail,))
    customer = cur.fetchone()
    con.close()

    if customer:
        return customer["pid"]
    else:
        return None
import sqlite3

# Connect to database


conn = sqlite3.connect('meeting_rooms.db')

# create a cursor object
c = conn.cursor()

# create the table if it does not exist
c.execute('''CREATE TABLE IF NOT EXISTS schedules
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              room_number INTEGER,
              start_time TEXT,
              end_time TEXT,
              event_type TEXT,
              title TEXT,
              content TEXT)''')

# close the cursor and the connection
c.close()
conn.close()


@app.route('/create_event', methods=['GET', 'POST'])
def create_event():
    if request.method == 'POST':
        # get the form data
        room_number = request.form['room_number']
        start_time = datetime.strptime(request.form['start_time'], '%Y-%m-%dT%H:%M')
        end_time = datetime.strptime(request.form['end_time'], '%Y-%m-%dT%H:%M')
        event_type = request.form['event_type']
        title = request.form['title']
        content = request.form['content']

        # check if the room is available during the requested time period
        conn = sqlite3.connect('meeting_rooms.db')
        c = conn.cursor()
        c.execute('''SELECT id FROM schedules
                     WHERE room_number = ?
                     AND ((start_time BETWEEN ? AND ?) OR (end_time BETWEEN ? AND ?))
                     AND strftime('%s', end_time) > strftime('%s', ?)
                     AND strftime('%s', start_time) < strftime('%s', ?)''',
                  (room_number, start_time, end_time, start_time, end_time, start_time, end_time))
        result = c.fetchone()
        if result:
            # room is already booked during the requested time period
            flash('Room is not available during the requested time period')
            return redirect(url_for('create_event'))

        # check if the start and end time exceed more than 3 days
        if (end_time - start_time) > timedelta(days=3):
            flash('Event duration cannot exceed more than 3 days')
            return redirect(url_for('create_event'))

        # add the event to the database
        c.execute('''INSERT INTO schedules (room_number, start_time, end_time, event_type, title, content)
                     VALUES (?, ?, ?, ?, ?, ?)''', (room_number, start_time, end_time, event_type, title, content))
        conn.commit()
        c.close()
        conn.close()

        # redirect to the manage meeting rooms page
       
        return redirect(url_for('manage_meeting_rooms'))

    # if GET request, render the create event form
   
    return render_template('create_event.html')

from datetime import datetime, timedelta



@app.route('/manage_meeting_rooms', methods=['GET', 'POST'])
def manage_meeting_rooms():
    # Get the filter options
    month = request.args.get('month')
    room_number = request.args.get('room_number')

    # Create a connection to the database
    conn = sqlite3.connect('meeting_rooms.db')
    c = conn.cursor()

    # Fetch all meeting room data based on filter options
    if month and room_number:
        # Filter by both month and room number
        c.execute('''SELECT id, room_number,start_time, end_time, event_type
                     FROM schedules
                     WHERE strftime('%m', start_time) = ?
                     AND room_number = ?''', (month, room_number))
    elif month:
        # Filter by month only
        c.execute('''SELECT id, room_number,start_time, end_time, event_type
                     FROM schedules
                     WHERE strftime('%m', start_time) = ?''', (month,))
    elif room_number:
        # Filter by room number only
        c.execute('''SELECT id,room_number, start_time, end_time, event_type
                     FROM schedules
                     WHERE room_number = ?''', (room_number,))
    else:
        # No filters, fetch all meeting room data
        c.execute('''SELECT id,room_number,start_time, end_time, event_type
                     FROM schedules''')

    # Fetch all rows
    rows = c.fetchall()

    # Close the cursor and the connection
    c.close()
    conn.close()

    if request.method == 'POST':
        
        if 'delete' in request.form:
            meeting_id = request.form['delete']
            # Check if the meeting has already started
            conn = sqlite3.connect('meeting_rooms.db')
            c = conn.cursor()
            c.execute('''SELECT start_time FROM schedules WHERE id = ?''', (meeting_id,))
            start_time_str = c.fetchone()[0]
            current_time = datetime.now()
            start_time = datetime.strptime(start_time_str, '%Y-%m-%d %H:%M:%S')
            if start_time < current_time:
                # Meeting has already started, cannot delete
                flash('Cannot delete a meeting that has already started')
            else:
                # Delete the meeting
                c.execute('''DELETE FROM schedules WHERE id = ?''', (meeting_id,))
                conn.commit()
                flash('Meeting deleted successfully')
            c.close()
            conn.close()
            return redirect(url_for('manage_meeting_rooms'))

    return render_template('manage_meeting_rooms.html', rows=rows)


@app.route('/edit_event/<int:event_id>', methods=['GET', 'POST'])
def edit_event(event_id):
    # Fetch the meeting event details from the database
    conn = sqlite3.connect('meeting_rooms.db')
    c = conn.cursor()
    c.execute('''SELECT room_number, start_time, end_time, event_type, title, content
                 FROM schedules
                 WHERE id = ?''', (event_id,))
    event_data = c.fetchone()
    c.close()
    conn.close()

    if request.method == 'POST':
        # Get the form data
        room_number = request.form['room_number']
        start_time = datetime.strptime(request.form['start_time'], '%Y-%m-%dT%H:%M')
        end_time = datetime.strptime(request.form['end_time'], '%Y-%m-%dT%H:%M')
        event_type = request.form['event_type']
        title = request.form['title']
        content = request.form['content']

        # Check if the room is available during the requested time period
        conn = sqlite3.connect('meeting_rooms.db')
        c = conn.cursor()
        c.execute('''SELECT id FROM schedules
                     WHERE room_number = ?
                     AND ((start_time BETWEEN ? AND ?) OR (end_time BETWEEN ? AND ?))
                     AND strftime('%s', end_time) > strftime('%s', ?)
                     AND strftime('%s', start_time) < strftime('%s', ?)
                     AND id != ?''',
                  (room_number, start_time, end_time, start_time, end_time, start_time, end_time, event_id))
        result = c.fetchone()
        if result:
            # Room is already booked during the requested time period
            flash('Room is not available during the requested time period')
            return redirect(url_for('edit_event', event_id=event_id))

        # Check if the start and end time exceed more than 3 days
        if (end_time - start_time) > timedelta(days=3):
            flash( 'Room booking cannot exceed 3 days')
            return redirect(url_for('edit_event', event_id=event_id))

        # Update the event details in the database
        c.execute('''UPDATE schedules SET room_number = ?, start_time = ?, end_time = ?, event_type = ?, 
                     title = ?, content = ? WHERE id = ?''',
                  (room_number, start_time, end_time, event_type, title, content, event_id))
        conn.commit()
        c.close()
        conn.close()

        # Redirect to the manage meeting rooms page
        
        return redirect(url_for('manage_meeting_rooms'))

    # Convert the start_time and end_time strings to datetime objects
    event_data = list(event_data)
    event_data[1] = datetime.strptime(event_data[1], '%Y-%m-%d %H:%M:%S')
    event_data[2] = datetime.strptime(event_data[2], '%Y-%m-%d %H:%M:%S')

    return render_template('edit_event.html', event_data=event_data)
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///projects.db'
db = SQLAlchemy(app)

@app.template_filter('split')
def split_filter(value, delimiter):
    return value.split(delimiter)

class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    manager = db.Column(db.String(100))
    employees = db.relationship('Employee', backref='department', lazy=True)

    def __init__(self, name, manager):
        self.name = name
        self.manager = manager

class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    address = db.Column(db.String(200))
    date_of_joining = db.Column(db.String(20))
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=False)
    designation = db.Column(db.String(100))
    skills = db.Column(db.String(200))
    projects = db.relationship('Project', secondary='employee_project', backref='employees')

    def __init__(self, name, email, address, date_of_joining, department_id, designation, skills):
        self.name = name
        self.email = email
        self.address = address
        self.date_of_joining = date_of_joining
        self.department_id = department_id
        self.designation = designation
        self.skills = skills

employee_project = db.Table('employee_project',
    db.Column('employee_id', db.Integer, db.ForeignKey('employee.id'), primary_key=True),
    db.Column('project_id', db.Integer, db.ForeignKey('project.id'), primary_key=True)
)

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_name = db.Column(db.String(100))
    objectives = db.Column(db.String(200))
    start_time = db.Column(db.String(20))
    deadlines = db.Column(db.String(20))
    equipment_resources = db.Column(db.String(200))
    software_resources = db.Column(db.String(200))
    skill_requirements = db.Column(db.String(200))
    budget = db.Column(db.Integer)

    def __init__(self, project_name, objectives, start_time, deadlines, equipment_resources,
                 software_resources, skill_requirements, budget):
        self.project_name = project_name
        self.objectives = objectives
        self.start_time = start_time
        self.deadlines = deadlines
        self.equipment_resources = equipment_resources
        self.software_resources = software_resources
        self.skill_requirements = skill_requirements
        self.budget = budget


@app.route('/add_employee', methods=['GET', 'POST'])
def add_employee():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        address = request.form.get('address')
        date_of_joining = request.form.get('date_of_joining')
        department_id = request.form.get('department_id')
        designation = request.form.get('designation')
        skills = request.form.get('skills')
        project_ids = request.form.getlist('projects')  # Get a list of selected project IDs

        employee = Employee(
            name=name,
            email=email,
            address=address,
            date_of_joining=date_of_joining,
            department_id=department_id,
            designation=designation,
            skills=skills
        )

        for project_id in project_ids:
            project = Project.query.get(project_id)
            employee.projects.append(project)

        db.session.add(employee)
        db.session.commit()

        return redirect('/view_employee')

    departments = Department.query.all()
    projects = Project.query.all()
    return render_template('add_employee.html', departments=departments, projects=projects)



@app.route('/add_department', methods=['GET', 'POST'])
def add_department():
    if request.method == 'POST':
        name = request.form.get('name')
        manager = request.form.get('manager')

        department = Department(
            name=name,
            manager=manager
        )

        db.session.add(department)
        db.session.commit()

        return redirect('/view_department')

    return render_template('add_department.html')

@app.route('/view_employee', methods=['GET', 'POST'])
def view_employee():
    if request.method == 'POST':
        employee_id = request.form.get('employee_id')
        name = request.form.get('name')
        project_name = request.form.get('project_name')  # Updated variable name

        employees = Employee.query
        if employee_id:
            employees = employees.filter(Employee.id == employee_id)
        if name:
            employees = employees.filter(Employee.name.ilike(f'%{name}%'))
        if project_name:  # Filter by project name
            employees = employees.filter(Employee.projects.any(Project.project_name.ilike(f'%{project_name}%')))

        employees = employees.all()

        return render_template('view_employee.html', employees=employees)

    employees = Employee.query.all()
    return render_template('view_employee.html', employees=employees)


@app.route('/update_project_status/<int:project_id>', methods=['POST'])
def update_project_status(project_id):
    status = request.json.get('status')

    # Update project status in the database
    project = Project.query.get(project_id)
    if project:
        project.status = status
        db.session.commit()

        if status == 'Submitted':
            # Delete the project from the employee's projects list
            employee_id = project.employee_id
            employee = Employee.query.get(employee_id)
            if employee:
                employee.projects = [p for p in employee.projects if p.id != project_id]
                db.session.commit()

        return jsonify({'message': 'Project status updated successfully.'}), 200

    return jsonify({'error': 'Project not found.'}), 404

@app.route('/delete_project/<int:employee_id>/<int:project_id>', methods=['POST'])
def delete_project(employee_id, project_id):
    # Delete the project from the employee's projects list
    employee = Employee.query.get(employee_id)
    if employee:
        employee.projects = [p for p in employee.projects if p.id != project_id]
        db.session.commit()

        return jsonify({'message': 'Project deleted successfully.'}), 200

    return jsonify({'error': 'Employee not found.'}), 404


@app.route('/view_department', methods=['GET', 'POST'])
def view_department():
    if request.method == 'POST':
        name = request.form.get('name')

        departments = Department.query
        if name:
            departments = departments.filter(Department.name.ilike(f'%{name}%'))

        departments = departments.all()

        return render_template('view_department.html', departments=departments)

    departments = Department.query.all()
    return render_template('view_department.html', departments=departments)


@app.route('/update_employee/<int:employee_id>', methods=['GET', 'POST'])
def update_employee(employee_id):
    employee = Employee.query.get(employee_id)
    if not employee:
        return "Employee not found"

    if request.method == 'POST':
        employee.name = request.form.get('name')
        employee.email = request.form.get('email')
        employee.address = request.form.get('address')
        employee.date_of_joining = request.form.get('date_of_joining')

        department_id = request.form.get('department_id')
        if department_id:
            employee.department_id = int(department_id)

        employee.designation = request.form.get('designation')
        employee.skills = request.form.get('skills')
        project_ids = request.form.getlist('projects')

        employee.projects.clear()  # Remove all existing projects associated with the employee

        for project_id in project_ids:
            project = Project.query.get(project_id)
            if project:
                employee.projects.append(project)

        db.session.commit()

        return redirect('/view_employee')

    departments = Department.query.all()
    projects = Project.query.all()
    return render_template('update_employee.html', employee=employee, departments=departments, projects=projects)

@app.route('/delete_employee/<int:employee_id>', methods=['GET', 'POST'])
def delete_employee(employee_id):
    employee = Employee.query.get(employee_id)
    db.session.delete(employee)
    db.session.commit()
    return redirect('/view_employee')

@app.route('/home_proj')
def home_proj():
    projects = Project.query.all()
    return render_template('home_proj.html', projects=projects)


@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        search_query = request.form['search_query']
        projects = Project.query.filter(Project.project_name.ilike(f'%{search_query}%')).all()
        return render_template('home_proj.html', projects=projects)
    return redirect('/home_proj')


@app.route('/add', methods=['GET', 'POST'])
def add_project():
    if request.method == 'POST':
        project_name = request.form.get('project_name')
        objectives = request.form.get('objectives')
        start_time = request.form.get('start_time')
        deadlines = request.form.get('deadlines')
        equipment_resources = request.form.get('equipment_resources')
        software_resources = request.form.get('software_resources')
        skill_requirements = request.form.get('skill_requirements')
        budget = request.form.get('budget')

        # Create a new Project object
        project = Project(
            project_name=project_name,
            objectives=objectives,
            start_time=start_time,
            deadlines=deadlines,
            equipment_resources=equipment_resources,
            software_resources=software_resources,
            skill_requirements=skill_requirements,
            budget=budget
        )

        # Add the project to the database
        db.session.add(project)
        db.session.commit()

        return redirect('/home_proj')

    return render_template('add.html')


@app.route('/edit/<int:project_id>', methods=['GET', 'POST'])
def edit(project_id):
    project = Project.query.get(project_id)
    if request.method == 'POST':
        project.project_name = request.form['project_name']
        project.objectives = request.form['objectives']
        project.start_time = request.form['start_time']
        project.deadlines = request.form['deadlines']
        project.equipment_resources = ', '.join(request.form.getlist('equipment_resources'))
        project.software_resources = ', '.join(request.form.getlist('software_resources'))
        project.skill_requirements = ', '.join(request.form.getlist('skill_requirements'))
        project.budget = request.form['budget']
        db.session.commit()

        return redirect('/home_proj')
    return render_template('edit.html', project=project)


@app.route('/delete/<int:project_id>', methods=['GET', 'POST'])
def delete(project_id):
    project = Project.query.get(project_id)
    db.session.delete(project)
    db.session.commit()
    return redirect('/home_proj')





@app.route('/manage_requisitions')
def manage_requisitions():
    con = sqlite3.connect("database.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    # Fetch all requisitions from the database
    cur.execute("SELECT * FROM requisitions")
    requisitions = cur.fetchall()

    con.close()
    return render_template("manage_requisitions.html", requisitions=requisitions)



@app.route('/reject_requisition/<int:id>')
def reject_requisition(id):
    con = sqlite3.connect("database.db")
    cur = con.cursor()

    # Update the requisition status to 'Rejected'
    cur.execute("UPDATE requisitions SET status='Rejected' WHERE id=?", (id,))
    con.commit()
    

    con.close()
    return redirect(url_for('manage_requisitions'))

import difflib

import sqlite3
from flask import redirect, url_for
from flask import render_template_string
con = sqlite3.connect("database.db")
con.row_factory = sqlite3.Row
cur = con.cursor()

    # Create the solved_requisitions table if it doesn't exist
cur.execute("""
        CREATE TABLE IF NOT EXISTS solved_requisitions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            resource_id INTEGER,
            department TEXT,
            project TEXT,
            required_date TEXT,
            return_date TEXT,
            status TEXT
        )
    """)
    
    # Fetch all solved requisitions from the database
con.close()


trigger_sql = """
CREATE TRIGGER IF NOT EXISTS move_to_solved_requisitions
AFTER DELETE ON requisitions
FOR EACH ROW
BEGIN
    INSERT INTO solved_requisitions(name, resource_id, department, project, required_date, return_date, status)
    VALUES (OLD.name, OLD.resource_id, OLD.department, OLD.project, OLD.required_date, OLD.return_date, OLD.status);
END;
"""

# Create a route to create the trigger
@app.route('/create_trigger')
def create_trigger():
    con = sqlite3.connect("database.db")
    cur = con.cursor()

    cur.executescript(trigger_sql)
    cur.execute(trigger_sql)
    con.commit()

    con.close()

    return 'Trigger created successfully'


from flask import redirect, url_for, flash

import sqlite3
from flask import redirect, url_for
from flask import render_template_string

@app.route('/approve_requisition/<int:id>')
def approve_requisition(id):
    con = sqlite3.connect("database.db")
    cur = con.cursor()

    # Fetch the requisition from the database
    cur.execute("SELECT * FROM requisitions WHERE id=? ORDER BY id ASC", (id,))

    requisition = cur.fetchone()

    # Compare employee skills with the required skills for the resource
    employee_skills = requisition[8]  # Access the skills using index 8
    resource = requisition[5]  # Access the resource name using index 5

    required_skills = {
        'Integrated Development Environments (IDEs)': 'Proficiency in programming languages, code debugging, version control (Git), build and deployment tools, understanding of IDE features and plugins.',
        'Version Control Systems (VCS)': 'Repository management, branch management, merging and conflict resolution, familiarity with command-line interface (CLI) or GUI clients, understanding of version control workflows.',
        'Project Management Tools': 'Task and issue tracking, project planning, collaboration and communication, agile methodologies, familiarity with project management concepts and workflows.',
        'Documentation Tools': 'Technical writing' ,
        'Testing and Quality Assurance Tools': 'Test case design and execution, automated testing, familiarity with testing frameworks and tools, knowledge of quality assurance principles and methodologies.',
        'Continuous Integration and Deployment (CI/CD) Tools': 'Building and packaging software, continuous integration and deployment pipelines, automation scripts, familiarity with containerization technologies (e.g., Docker), understanding of software release processes.',
        'Collaboration and Communication Tools': 'Effective communication, remote collaboration, file sharing and collaboration, video conferencing, understanding of project management and team collaboration workflows.',
        'Cloud Platforms': 'Cloud computing concepts, infrastructure-as-code (IaC), deploying and managing applications in the cloud, familiarity with cloud services and APIs.',
        'Data Visualization and Analytics Tools': 'Data analysis and visualization, understanding of data structures and algorithms, proficiency in relevant programming languages, familiarity with statistical analysis and visualization techniques.',
        'Development Frameworks and Libraries': 'Proficiency in relevant programming languages, understanding of software design patterns, familiarity with the framework or library\'s features and best practices.'
    }

    if resource in required_skills:
        required_skills_for_resource = required_skills[resource]
        required_skills_list = required_skills_for_resource.lower().split(', ')
        employee_skills_list = employee_skills.lower().split(', ')

        match_scores = []
        for required_skill in required_skills_list:
            match_scores.append(max(difflib.SequenceMatcher(None, required_skill, employee_skill).ratio() for employee_skill in employee_skills_list))

        average_score = sum(match_scores) / len(match_scores)

        if average_score >= 0.7:  # Adjust the matching threshold as needed
            # Delete the requisition from the database
            cur.execute("DELETE FROM requisitions WHERE id=?", (id,))
            con.commit()
            
            con.close()

            return render_template_string("""
                <script>
                    alert('Requisition approved and deleted from the database.');
                    window.location.href = "{{ url_for('manage_requisitions') }}";
                </script>
            """)
        else:
            # Update the requisition status to 'Rejected'
            cur.execute("UPDATE requisitions SET status='Rejected' WHERE id=?", (id,))
            con.commit()

            con.close()

            return render_template_string("""
                <script>
                    alert('Requisition rejected.');
                    window.location.href = "{{ url_for('manage_requisitions') }}";
                </script>
            """)
    con.close()

    return redirect(url_for('manage_requisitions'))

@app.route('/solved_requisitions')
def solved_requisitions():
    con = sqlite3.connect("database.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    # Fetch all solved requisitions from the database
    cur.execute("SELECT * FROM solved_requisitions")
    requisitions = cur.fetchall()

    con.close()

    return render_template("solved_requisitions.html", requisitions=requisitions)

# Existing code

@app.route('/incoming_complaints')
def incoming_complaints():

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Retrieve all complaints from the table
    cursor.execute("SELECT * FROM complaints")
    complaints = cursor.fetchall()

    conn.close()

    return render_template('incoming_complaints.html', complaints=complaints)


@app.route('/solve_complaint/<int:complaint_id>', methods=['POST'])
def solve_complaint(complaint_id):

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Delete the complaint with the provided ID
    cursor.execute("DELETE FROM complaints WHERE id=?", (complaint_id,))

    conn.commit()
    conn.close()

    
    return redirect(url_for('incoming_complaints'))

def get_pending_requisitions_count():
    con = sqlite3.connect("database.db")
    cur = con.cursor()
    cur.execute("SELECT COUNT(*) FROM requisitions WHERE status='Pending'")
    count = cur.fetchone()[0]
    con.close()
    return count

def get_solved_requisitions_count():
    con = sqlite3.connect("database.db")
    cur = con.cursor()
    cur.execute("SELECT COUNT(*) FROM requisitions WHERE status='Solved'")
    count = cur.fetchone()[0]
    con.close()
    return count


from datetime import datetime
import matplotlib.pyplot as plt



conn = sqlite3.connect("resources.db")
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS resources
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              resource_type TEXT NOT NULL,
              floor TEXT NOT NULL,
              room TEXT NOT NULL,
              quantity INTEGER NOT NULL,
              availability INTEGER NOT NULL,
              condition TEXT,
              maintenance_history TEXT,
              last_maintenance_date TEXT NOT NULL,
              next_maintenance_date TEXT NOT NULL,
              total_usage INTEGER NOT NULL)''')


conn.commit()

c.execute('''CREATE TABLE IF NOT EXISTS resource_availability
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              resource_id INTEGER NOT NULL REFERENCES resources(id),
              available_quantity INTEGER NOT NULL)''')
conn.commit()

c.execute('''CREATE TABLE IF NOT EXISTS office_resource_request
             (reqisition_id INTEGER PRIMARY KEY AUTOINCREMENT,
              name TEXT NOT NULL,
              resource_id INTEGER NOT NULL REFERENCES resources(id),
              quantity INTEGER,
              description TEXT,
              department TEXT,
              project TEXT,
              required_date TEXT,
              return_date TEXT,
              status TEXT)''')
conn.commit()

c.execute('''CREATE TABLE IF NOT EXISTS resource_allocation (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                reqisition_id INTEGER,
                resource_id INTEGER,
                allocated_quantity INTEGER,
                allocation_date TEXT,
                status TEXT,
                FOREIGN KEY (reqisition_id) REFERENCES office_resource_request(reqisition_id),
                FOREIGN KEY (resource_id) REFERENCES resources(id)
            )''')
conn.commit()

conn.close()




@app.route("/index_resources", methods=["GET", "POST"])
def index_resources():
    if request.method == "POST":
        # Get form data
        resource_type = request.form["resource_type"]
        floor = request.form["floor"]
        room = request.form["room"]
        quantity = request.form["quantity"]
        availability = request.form["availability"]
        condition = request.form["condition"]
        maintenance_history = request.form["maintenance_history"]
        last_maintenance_date = request.form["last_maintenance_date"]
        next_maintenance_date = request.form["next_maintenance_date"]
        total_usage = request.form["total_usage"]

        # Insert data into resources table
        conn = sqlite3.connect("resources.db")
        c = conn.cursor()
        c.execute(
            "INSERT INTO resources (resource_type, floor, room, quantity, availability, condition, maintenance_history, last_maintenance_date, next_maintenance_date, total_usage) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                resource_type,
                floor,
                room,
                quantity,
                availability,
                condition,
                maintenance_history,
                last_maintenance_date,
                next_maintenance_date,
                total_usage,
            ),
        )
        resource_id = c.lastrowid  # Get the ID of the inserted resource
        conn.commit()

        # Insert data into resource_availability table
        c.execute(
            "INSERT INTO resource_availability (resource_id, available_quantity) VALUES (?, ?)",
            (resource_id, availability),
        )
        conn.commit()
        conn.close()

        # Display success message
        
        return redirect(url_for("view_resources"))  # Redirect to the view_resources page

    return render_template("index_resources.html")


@app.route('/view_resources')
def view_resources():
    conn = sqlite3.connect("resources.db")
    c = conn.cursor()

    # Fetch all resource details from the database
    c.execute('SELECT * FROM resources')
    details = c.fetchall()

    conn.close()

    # Organize resource details by resource type
    resource_details = {}
    for detail in details:
        resource_type = detail[1]
        if resource_type not in resource_details:
            resource_details[resource_type] = []
        resource_details[resource_type].append(detail)

    return render_template('view_resources.html', resource_details=resource_details)


@app.route('/update_resource/<int:resource_id>', methods=['GET', 'POST'])
def update_resource(resource_id):
    conn = sqlite3.connect("resources.db")
    c = conn.cursor()

    if request.method == 'POST':
        
        floor = request.form['floor']
        quantity = request.form['quantity']
        availability = request.form['availability']
        condition = request.form['condition']
        maintenance_history = request.form['maintenance_history']
        last_maintenance_date = request.form['last_maintenance_date']
        next_maintenance_date = request.form['next_maintenance_date']
        total_usage = request.form['total_usage']

        # Update the resource details in the database
        c.execute('''UPDATE resources
                     SET  floor=?, quantity=?, availability=?, condition=?,
                         maintenance_history=?, last_maintenance_date=?, next_maintenance_date=?, total_usage=?
                     WHERE id=?''',
                  ( floor, quantity, availability, condition,
                   maintenance_history, last_maintenance_date, next_maintenance_date, total_usage, resource_id))
        conn.commit()
        conn.close()

        return redirect('/view_resources')

    # Fetch the existing resource details from the database
    c.execute('SELECT * FROM resources WHERE id=?', (resource_id,))
    details = c.fetchone()

    conn.close()

    return render_template('update_resource.html', details=details)



@app.route("/resource_requests", methods=["GET", "POST"])
def resource_requests():
    conn = sqlite3.connect("resources.db")
    c = conn.cursor()

    # Retrieve the resource names from the database
    c.execute("SELECT DISTINCT resource_type FROM resources")
    resource_names = [row[0] for row in c.fetchall()]

    conn.close()

    if request.method == "POST":
        # Retrieve form data
        employee_name = request.form["employee_name"]
        resource_name = request.form["resource_name"]
        quantity = request.form["quantity"]
        description = request.form["description"]
        project = request.form["project"]
        department = request.form["department"]
        required_date = request.form["required_date"]
        return_date = request.form["return_date"]

        # Insert the request into the office_resource_request table
        conn = sqlite3.connect("resources.db")
        c = conn.cursor()
        c.execute(
            '''INSERT INTO office_resource_request
                     (name, resource_id, quantity, description, department, project, required_date, return_date, status)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (
                employee_name,
                resource_name,
                quantity,
                description,
                department,
                project,
                required_date,
                return_date,
                "",
            ),
        )

        conn.commit()
        conn.close()

        # Redirect to a success page or perform additional actions

        return redirect(url_for("customer"))

    # Render the resource request form template for GET requests
    return render_template("resource_requests.html", resource_names=resource_names)



@app.route("/view_request_resources", methods=["GET", "POST"])
def view_request_resources():
    conn = sqlite3.connect("resources.db")
    c = conn.cursor()

    c.execute("SELECT * FROM office_resource_request")
    
    requests = c.fetchall()

    conn.close()

    return render_template("view_request_resources.html", requests=requests)

from flask import Flask, render_template, redirect, url_for, flash


# Your other routes and functions
@app.route("/approve_request/<int:req_id>", methods=["GET", "POST"])
def approve_request(req_id):
    if request.method == "POST":
        conn = sqlite3.connect("resources.db")
        c = conn.cursor()
        c.execute("SELECT * FROM office_resource_request WHERE reqisition_id=?", (req_id,))
        request_data = c.fetchone()

        if request_data is None:
            return "<script>alert('Invalid request ID.'); window.location.href='/view_request_resources'</script>"

        resource_name = request_data[2]
        quantity_requested = request_data[3]

        c.execute("SELECT * FROM resources WHERE resource_type=?", (resource_name,))
        resource_data = c.fetchone()

        if resource_data is None:
            return "<script>alert('Requested resource not found.'); window.location.href='/view_request_resources'</script>"

        resource_id = resource_data[0]
        availability = resource_data[5]

        if quantity_requested > availability:
            return "<script>alert('Insufficient quantity available for allocation.'); window.location.href='/view_request_resources'</script>"

        # Perform the resource allocation here

        # Update the availability of the resource
        new_availability = availability - quantity_requested
        c.execute("UPDATE resources SET availability=? WHERE id=?", (new_availability, resource_id))

        # Update the status of the request
        c.execute("UPDATE office_resource_request SET status='Approved' WHERE reqisition_id=?", (req_id,))

        conn.commit()
        conn.close()

        return "<script>alert('Resource request approved.'); window.location.href='/view_request_resources'</script>"

    return "<script>window.location.href='/view_request_resources'</script>"




@app.route("/return_resources")
def return_resources():
    conn = sqlite3.connect("resources.db")
    c = conn.cursor()

    # Get today's date
    today = datetime.now().date().strftime("%Y-%m-%d")

    # Retrieve resource requests that have today as the return date and are not yet processed
    c.execute("SELECT * FROM office_resource_request WHERE return_date=? AND status=?", (today, ""))
    requests = c.fetchall()

    for request in requests:
        req_id = request[0]
        resource_id = request[2]
        quantity = request[3]

        # Update the availability of the resource
        c.execute("SELECT availability FROM resources WHERE id=?", (resource_id,))
        availability = c.fetchone()[0]
        new_availability = availability + quantity
        c.execute("UPDATE resources SET availability=? WHERE id=?", (new_availability, resource_id))

        # Update the status of the request to "Returned"
        c.execute("UPDATE office_resource_request SET status='Returned' WHERE reqisition_id=?", (req_id,))

        # Insert the resource allocation data into resource_allocation table
        c.execute("INSERT INTO resource_allocation (reqisition_id, resource_id, allocated_quantity, allocation_date, status) VALUES (?, ?, ?, ?, ?)", (req_id, resource_id, quantity, today, "Returned"))

    conn.commit()
    conn.close()

    return "Resources returned and availability updated."

import os
import matplotlib.pyplot as plt
from flask import Flask, make_response, send_from_directory
import sqlite3


@app.route("/view", methods=["GET", "POST"])
def view():
    # Connect to the database
    conn = sqlite3.connect("resources.db")
    c = conn.cursor()

    # Get the resource types from the database
    c.execute("SELECT DISTINCT resource_type FROM resources")
    resource_types = c.fetchall()

    # Get the floors from the database
    c.execute("SELECT DISTINCT floor FROM resources")
    floors = c.fetchall()

    # Get the selected form data
    selected_resource_type = request.form.get("resource_type")
    selected_floor = request.form.get("floor")

    # Query the database for the selected data
    if selected_floor == "All":
        c.execute("SELECT resource_type, floor, room, SUM(quantity) AS room_total, \
            (SELECT SUM(quantity) FROM resources WHERE resource_type = ?) AS total \
            FROM resources WHERE resource_type = ? GROUP BY room",
            (selected_resource_type, selected_resource_type))
        data = c.fetchall()
    else:
        c.execute("SELECT resource_type, floor, room, quantity AS room_total, \
            (SELECT SUM(quantity) FROM resources WHERE floor = ? AND resource_type = ?) AS total \
            FROM resources WHERE floor = ? AND resource_type = ?",
            (selected_floor, selected_resource_type, selected_floor, selected_resource_type))
        data = c.fetchall()

    # Close the database connection
    conn.close()

    return render_template("view.html", resource_types=resource_types, floors=floors,
                           selected_resource_type=selected_resource_type, selected_floor=selected_floor, data=data)

import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from flask import Flask, render_template, jsonify
import base64
from io import BytesIO

def generate_quantity_graph():
    conn = sqlite3.connect("resources.db")
    c = conn.cursor()

    # Query the database to fetch the necessary data
    c.execute("SELECT resource_type, SUM(quantity) AS total_quantity FROM resources GROUP BY resource_type")
    quantity_data = c.fetchall()

    # Create a DataFrame from the fetched data
    df_quantity = pd.DataFrame(quantity_data, columns=['resource_type', 'total_quantity'])

    # Generate the quantity graph
    plt.figure()
    plt.bar(df_quantity['resource_type'], df_quantity['total_quantity'])
    plt.title('Resource Quantity')
    plt.xlabel('Resource Type')
    plt.ylabel('Total Quantity')
    plt.tight_layout()
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    graph_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    plt.close()

    return graph_base64

def generate_total_usage_pie():
    conn = sqlite3.connect("resources.db")
    c = conn.cursor()

    # Query the database to fetch the necessary data
    c.execute("SELECT resource_type, SUM(total_usage) AS total_usage FROM resources GROUP BY resource_type")
    total_usage_data = c.fetchall()

    # Create a DataFrame from the fetched data
    df_total_usage = pd.DataFrame(total_usage_data, columns=['resource_type', 'total_usage'])

    # Generate the total usage pie chart
    plt.figure()
    plt.pie(df_total_usage['total_usage'], labels=df_total_usage['resource_type'], autopct='%1.1f%%')
    plt.title('Total Resource Usage')
    plt.tight_layout()
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    graph_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    plt.close()

    return graph_base64

def generate_table_data():
    conn = sqlite3.connect("resources.db")
    c = conn.cursor()

    # Query the database to fetch the necessary data
    c.execute("SELECT resource_type, SUM(total_usage) AS total_usage FROM resources GROUP BY resource_type")
    table_data = c.fetchall()

    # Create a DataFrame from the fetched data
    df_table_data = pd.DataFrame(table_data, columns=['resource_type', 'total_usage'])

    # Find total utilization
    total_utilization = df_table_data['total_usage'].sum()

    # Calculate utilization percentage
    df_table_data['utilization'] = df_table_data['total_usage'] / total_utilization

    # Find overutilized and underutilized resources
    overutilized = df_table_data[df_table_data['utilization'] > 0.5]
    underutilized = df_table_data[df_table_data['utilization'] < 0.5]

    return overutilized, underutilized


@app.route('/graphs')
def graphs():
    # Generate the quantity graph
    quantity_graph_base64 = generate_quantity_graph()

    # Generate the total usage pie chart
    total_usage_pie_base64 = generate_total_usage_pie()

    # Generate the table data
    overutilized, underutilized = generate_table_data()

    # Prepare the response data
    response = {
        'quantity_graph': quantity_graph_base64,
        'total_usage_pie': total_usage_pie_base64,
        'overutilized': overutilized.to_dict(orient='records'),
        'underutilized': underutilized.to_dict(orient='records')
    }

    # Return the rendered HTML template
    return render_template('graphs.html', data=response)

@app.route('/update_graph')
def update_graph():
    # Generate the quantity graph
    quantity_graph_base64 = generate_quantity_graph()

    # Generate the total usage pie chart
    total_usage_pie_base64 = generate_total_usage_pie()

    # Generate the table data
    overutilized, underutilized = generate_table_data()

    # Prepare the response data
    response = {
        'quantity_graph': quantity_graph_base64,
        'total_usage_pie': total_usage_pie_base64,
        'overutilized': overutilized.to_dict(orient='records'),
        'underutilized': underutilized.to_dict(orient='records')
    }

    return jsonify(response)



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)


