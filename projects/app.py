""" This file contains your app, routes and blueprints """
from projects import create_app

if __name__ == '__main__':
    """ Init flask app from __init__.py """
    APP = create_app()

    """ debug=True => Detected change """
    APP.run(debug=True)
    # APP.run()
