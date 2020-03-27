import argparse
import subprocess
import os


def run_unit_tests() -> str:
    parser = argparse.ArgumentParser()

    parser.add_argument('--q', required=True)

    args, extra_params = parser.parse_known_args()
    return "pipenv run pytest -s -q /flask-examples/{}".format(args.q)

def connect_pg() -> str:
    return '/usr/bin/pg_ctl  restart; psql'


def main():
    description = 'Run a command inside a container '
    parser = argparse.ArgumentParser(description=description)

    parser.add_argument('command')

    args, extra_params = parser.parse_known_args()

    command_options = {
        'test': {'cmd': run_unit_tests, 'image': 'python'},
        'connect_pg': {'cmd': connect_pg, 'image': 'postgresql'}
    }


    cmd = [
        "docker-compose",
        "run",
        "--rm",
        "--volume={}/:/flask-examples/".format(os.getcwd()),
        command_options[args.command]['image'],
        "sh",
        "-c",
        command_options[args.command]['cmd']()
    ]

    subprocess.run(cmd, cwd=r'./tools')


if __name__ == '__main__':
    main()
