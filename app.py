from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Data Model
class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    status = db.Column(db.Integer, default=0) # 0 = Pending, 1 = Completed
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Task {self.id}>'

# Route: Dashboard (Create & Read)
@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        task_content = request.form['content']
        if not task_content:
            return redirect('/')
            
        new_task = Todo(content=task_content)
        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect('/')
        except Exception as e:
            return f"Error adding task: {e}"
    else:
        # Fetch tasks ordered by newest first
        tasks = Todo.query.order_by(Todo.date_created.desc()).all()
        return render_template('index.html', tasks=tasks)

# Route: Delete Task (Delete)
@app.route('/delete/<int:id>')
def delete(id):
    task = Todo.query.get_or_404(id)
    try:
        db.session.delete(task)
        db.session.commit()
        return redirect('/')
    except:
        return "Error deleting task"

# Route: Update Task Content (Update)
@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    task = Todo.query.get_or_404(id)
    if request.method == 'POST':
        task.content = request.form['content']
        try:
            db.session.commit()
            return redirect('/')
        except:
            return "Error updating task"
    else:
        return render_template('update.html', task=task)

# Route: Toggle Task Status (The new 'Done/Undo' logic)
@app.route('/done/<int:id>')
def done(id):
    task = Todo.query.get_or_404(id)
    # Toggles between 0 and 1
    task.status = 1 if task.status == 0 else 0
    try:
        db.session.commit()
        return redirect('/')
    except:
        return "Error updating task status"

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)