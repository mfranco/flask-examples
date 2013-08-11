import argparse

def syncdb(**kwargs):
    from models.base import get_engine
    from sqlalchemy.ext.declarative import declarative_base
    engine = get_engine()
    Base = declarative_base()
    CommercialActivity.metadata.create_all(engine)

def test(**kwargs):
    from test import init_test
    init_test()

def main():
    parser = argparse.ArgumentParser(description='flask user api demo')
    parser.add_argument('action', nargs='+', choices='test' )
    args = parser.parse_args()
    kwargs = {}
    task_dict = {'syncdb': syncdb, 'test': test}
    task = args.action[0]
    task_dict[task](**kwargs)

if __name__ == '__main__':
    main()
