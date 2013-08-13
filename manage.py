import argparse
from users.views import run_app


def syncdb(**kwargs):
    from common.models import get_engine
    from sqlalchemy.ext.declarative import declarative_base
    from users.models import User
    engine = get_engine()
    Base = declarative_base()
    User.metadata.create_all(engine)

def runserver():
    run_app()

def test(**kwargs):
    from test import init_test
    init_test()


def main():
    parser = argparse.ArgumentParser(description='flask user api demo')
    parser.add_argument('action', nargs='+', choices=['test', 'runserver', 'syncdb'] )
    args = parser.parse_args()
    kwargs = {}
    task_dict = {'syncdb': syncdb, 'test': test, 'runserver': runserver}
    task = args.action[0]
    task_dict[task](**kwargs)

if __name__ == '__main__':
    main()
