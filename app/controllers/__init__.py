from flask import Blueprint

task_bp = Blueprint('tasks', __name__, url_prefix='/tasks')
user_bp = Blueprint('users', __name__, url_prefix='/users')

from .task_controller import *
from .user_controller import *
