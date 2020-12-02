from application import init_app

# from flask import Flask

# app = Flask(__name__)

manage = init_app('application.settings.dev')

# @manage.app.route("/")
# def index():
#     return "index"

if __name__ == '__main__':
    manage.run()
