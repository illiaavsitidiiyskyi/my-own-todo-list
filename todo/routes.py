from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import Todo, User
from datetime import datetime

todo_bp = Blueprint('todo', __name__, template_folder='templates')


def login_required(f):
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            flash('Log in first', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper


@todo_bp.route('/')
@login_required
def index():
    user_id = session['user_id']
    todos = Todo.select().where(Todo.user == user_id).order_by(Todo.weight.desc(), Todo.deadline)
    return render_template('todo/index.html', todos=todos)


@todo_bp.route('/add', methods=['POST'])
@login_required
def add_todo():
    title = request.form.get('title')
    deadline_str = request.form.get('deadline')
    weight = int(request.form.get('weight', 3))

    deadline = None
    if deadline_str:
        deadline = datetime.strptime(deadline_str, '%Y-%m-%dT%H:%M')

    Todo.create(
        title=title,
        deadline=deadline,
        weight=weight,
        user=session['user_id']
    )

    flash('Task added!', 'success')
    return redirect(url_for('todo.index'))


@todo_bp.route('/toggle/<int:todo_id>')
@login_required
def toggle_todo(todo_id):
    todo = Todo.get_by_id(todo_id)
    if todo.user.id != session['user_id']:
        flash('Access is denied', 'danger')
        return redirect(url_for('todo.index'))

    todo.done = not todo.done
    todo.save()
    return redirect(url_for('todo.index'))


@todo_bp.route('/delete/<int:todo_id>')
@login_required
def delete_todo(todo_id):
    todo = Todo.get_by_id(todo_id)
    if todo.user.id != session['user_id']:
        flash('Task deleted!', 'danger')
        return redirect(url_for('todo.index'))

    todo.delete_instance()
    flash('Task deleted!', 'success')
    return redirect(url_for('todo.index'))


@todo_bp.route('/edit/<int:todo_id>', methods=['GET', 'POST'])
@login_required
def edit_todo(todo_id):
    todo = Todo.get_by_id(todo_id)
    if todo.user.id != session['user_id']:
        flash('Access is denied', 'danger')
        return redirect(url_for('todo.index'))

    if request.method == 'POST':
        todo.title = request.form.get('title')
        deadline_str = request.form.get('deadline')
        todo.weight = int(request.form.get('weight', 3))

        if deadline_str:
            todo.deadline = datetime.strptime(deadline_str, '%Y-%m-%dT%H:%M')
        else:
            todo.deadline = None

        todo.save()
        flash('The task has been updated!', 'success')
        return redirect(url_for('todo.index'))

    return render_template('todo/edit.html', todo=todo)