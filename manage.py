import argparse
import subprocess
import os


def run_unit_tests() -> str:
    parser = argparse.ArgumentParser()

    parser.add_argument('--q', required=True)

    args, extra_params = parser.parse_known_args()
    return "pipenv run pytest -s -q /flask-examples/{}".format(args.q)

def main():
    description = 'Run a command inside a container '
    parser = argparse.ArgumentParser(description=description)

    parser.add_argument('command')

    args, extra_params = parser.parse_known_args()

    command_options = {
        'test': run_unit_tests()
    }


    cmd = [
        "docker-compose",
        "run",
        "--rm",
        "--volume={}/:/flask-examples/".format(os.getcwd()),
        "python",
        "sh",
        "-c",
        command_options[args.command]
    ]

    subprocess.run(cmd, cwd=r'./tools')


if __name__ == '__main__':
    main()
