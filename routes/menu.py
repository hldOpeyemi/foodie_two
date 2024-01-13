from flask import Blueprint;

menu_bp = Blueprint('menu', __name__)

@menu_bp.route('/test')
def menu_test():
  return "This is a test"  