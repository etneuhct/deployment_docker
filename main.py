import os
from pathlib import Path

import requests
from jinja2 import FileSystemLoader, Environment

APPLICATION_URL = "http://192.168.1.140:49999/api/application/"
BASE_DIR = Path(__file__).resolve().parent
NGINX_DEFAULT_CONF_URL = '/etc/nginx/http.d/default.conf'
WORKDIR = '/usr/src/app'


def get_applications():
    application = requests.get(APPLICATION_URL).json()
    return [app for app in application if app['deploy']]


def format_with_jinja(data, file_name):
    with open(os.path.join(BASE_DIR, 'templates', file_name), "r", encoding="utf-8") as f:
        template = Environment(loader=FileSystemLoader(BASE_DIR)).from_string(f.read())

    result = template.render(**data)
    return result


def create_conf_file(applications):
    confs = [format_with_jinja(application, 'default.conf') for application in applications]
    with open(f'{NGINX_DEFAULT_CONF_URL}', 'w') as f:
        f.write("\n\n".join(confs))


def print_running_cmd(commands):
    script = "\n".join(commands)
    print(f"La commande suivante va etre executée:\n\n{script}")


def clone_applications(applications):
    commands = []
    for application in applications:
        name = application['name']
        if os.path.exists(os.path.join(WORKDIR, name)):
            print(f'{name} existe déjà. Ignoré.')
            continue
        commands.append(f'git clone {application["git_url"]} {name}')
    script = " && ".join(commands)
    print_running_cmd(commands)
    os.system(script)


def install_requirements(applications):
    commands = []
    for application in applications:
        if not os.path.exists(os.path.join(WORKDIR, application['name'])):
            continue
        files = os.listdir(application['name'])
        if 'requirements.txt' in files and not os.path.exists(
                os.path.join(WORKDIR, application['name'], 'venv')):
            commands.append(f'cd {application["name"]}')
            commands.append('python -m venv venv')
            commands.append('./venv/bin/pip install -r requirements.txt')
            commands.append('cd /')
        elif 'package.json' in files:
            commands.append(f'cd {application["name"]}')
            commands.append('npm i')
            commands.append('npm run build')
            commands.append('cd /')
    print_running_cmd(commands)
    script = " && ".join(commands)
    os.system(script)


def start_application(applications):
    commands = []
    for application in applications:
        if 'run_file' in application and application['run_file']:
            command = f'cd {os.path.join(WORKDIR, application["name"])}' \
                      f'\nsource {application["run_file"]} &'

            commands.append(command)
    commands.append('nginx -g "daemon off;"')
    print_running_cmd(commands)
    scripts = "\n".join(commands)
    with open('start_service.sh', 'w') as f:
        f.write(scripts)


def main():
    applications = get_applications()
    """create_conf_file(applications)
    clone_applications(applications)
    install_requirements(applications)
    start_application(applications)"""
    print(applications)

if __name__ == '__main__':
    main()
