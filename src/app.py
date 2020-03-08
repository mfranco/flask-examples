from flask import Flask, current_app

import os
import typing



def get_or_create_app(name: str, routes: typing.Tuple=tuple()) -> Flask:

    def init_config(app: Flask) -> None:
        """Looks for the environment variable FLASK_BH_CONFIG_PREFIXES it's
        default value is FLASK_BH
        Multiple prefixes can be defined as comma separated values
        Example 1:
        DB,AWS
        Flask_BH will load in the flask configuration object values from
        environment variables such as DB_USER, DB_PASSAWORD, AWS_REGION
        """
        prefixes = set(os.environ.get(
            'FLASK_CONFIG_PREFIXES', 'FLASK').split(','))

        if 'FLASK' not in prefixes:
            prefixes.add('FLASK')

        if 'FLASK_TESTING' not in os.environ:
            os.environ['FLASK_TESTING'] = 'False'

        if 'FLASK_LOG_LEVEL' not in os.environ:
            os.environ['FLASK_LOG_LEVEL'] = 'INFO'


        for k in os.environ.keys():
            for prefix in prefixes:
                if prefix in k:
                    app.config[k] = os.environ[k]


    def init_routing(app: Flask) -> None:
        """Looks for the environment variable FLASK_BH_ROUTES it's default
        value is routes.py
        This variable should point to a python file that contains a
        variable name ROUTES
        The ROUTES variable should be a tuple where each route is a dictionary
        Example:
        ROUTES = (
           {
                'rule': '/messages', 'endpoint': 'home',
                'view_func': MessageView.as_view('home')
            },
            {
                'rule': '/', 'view_func': simple_func_view
            },
            {
                'rule': '/post-func', 'endpoint': 'post_endpoint',
                'view_func': post_func_view, 'methods': ['POST']
            },
        )
        See: http://flask.pocoo.org/docs/1.0/api/#flask.Flask.add_url_rule
        """
        app.logger.debug('Initializing routes')
        try:
            for record in routes:
                route = record.copy()
                rule = route.pop('rule')
                app.add_url_rule(rule, **route)
        except Exception as e:
            app.logger.info(e)

    try:
        app = current_app._get_current_object()
    except Exception:
        app = Flask(name)
        init_config(app)
        init_routing(app)

    return app
