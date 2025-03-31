from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.exceptions import BadRequest
from datetime import date

app = Flask(__name__)


# Update this line
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', '').replace('postgres://', 'postgresql://', 1)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

@app.errorhandler(400)
def bad_request(error):
    return jsonify({'error': error.description}), 400

@app.errorhandler(500)
def server_error(error):
    return jsonify({'error': 'Internal server error'}), 500
db = SQLAlchemy(app)

class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    amount_due = db.Column(db.Float, default=0.0)

    def __repr__(self):
        return f"<Student {self.first_name} {self.last_name}>"

# CREATE
@app.route('/students', methods=['POST'])
def create_student():
    data = request.get_json()
    
    # Required fields check
    required = ['first_name', 'last_name', 'dob']
    if not all(field in data for field in required):
        raise BadRequest(f"Missing required fields: {', '.join(required)}")
    
    # Date validation
    try:
        dob = datetime.strptime(data['dob'], '%Y-%m-%d').date()
        if dob > date.today():
            raise ValueError("Date of birth cannot be in the future")
    except ValueError as e:
        raise BadRequest(f"Invalid date: {str(e)}")
    
    # Amount validation
    amount_due = float(data.get('amount_due', 0))
    if amount_due < 0:
        raise BadRequest("Amount due cannot be negative")
    
    # Create student
    student = Student(
        first_name=data['first_name'],
        last_name=data['last_name'],
        dob=dob,
        amount_due=amount_due
    )
    db.session.add(student)
    db.session.commit()
    
    return jsonify({
        'id': student.id,
        'first_name': student.first_name,
        'last_name': student.last_name,
        'dob': student.dob.isoformat(),
        'amount_due': student.amount_due
    }), 201
# READ ALL
@app.route('/students', methods=['GET'])
def get_students():
    students = Student.query.all()
    return jsonify([{
        'id': s.id,
        'first_name': s.first_name,
        'last_name': s.last_name,
        'dob': s.dob.isoformat(),
        'amount_due': s.amount_due
    } for s in students])

# READ ONE
@app.route('/students/<int:id>', methods=['GET'])
def get_student(id):
    student = Student.query.get_or_404(id)
    return jsonify({
        'id': student.id,
        'first_name': student.first_name,
        'last_name': student.last_name,
        'dob': student.dob.isoformat(),
        'amount_due': student.amount_due
    })

# UPDATE
@app.route('/students/<int:id>', methods=['PUT'])
def update_student(id):
    student = Student.query.get_or_404(id)
    data = request.get_json()
    if 'first_name' in data:
        student.first_name = data['first_name']
    if 'last_name' in data:
        student.last_name = data['last_name']
    if 'dob' in data:
        student.dob = datetime.strptime(data['dob'], '%Y-%m-%d').date()
    if 'amount_due' in data:
        student.amount_due = data['amount_due']
    db.session.commit()
    return jsonify({'message': 'Student updated successfully'})

# DELETE
@app.route('/students/<int:id>', methods=['DELETE'])
def delete_student(id):
    student = Student.query.get_or_404(id)
    db.session.delete(student)
    db.session.commit()
    return jsonify({'message': 'Student deleted successfully'})
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)