#https://www.digitalocean.com/community/tutorials/how-to-set-up-django-with-postgres-nginx-and-gunicorn-on-ubuntu-18-04
#https://hackernoon.com/deploy-django-app-with-nginx-gunicorn-postgresql-supervisor-9c6d556a25ac
#https://mhsiddiqui.github.io/2018/12/27/Part-3-Deploy-Django-using-Nginx-and-Gunicorn-uWSGI-Automation-with-Fabric/
from fabric.api import *
PACKAGE_LIST= [
'python3.6',
'python3.6-dev',
'python3.6-venv',
'python3.6-pip'
'build-essential',
'libpq-dev',
'postgresql'
'postgresql-contrib',
'python3.6-venv'
'nginx',
'gettext',
'supervisor'
]

DB_USER = "admin" #define your user here
DB_PASS = "BURNsegmentation01" #define your password here
DB_NAME = "burnwebdb" #define your database name here

def restart_supervisor():
    sudo("supervisorctl reread")
    sudo("supervisorctl update")
    sudo("supervisorctl reload")

def restart_nginx():
    sudo("systemctl restart nginx")

def install_package():
    sudo('apt-get update')
    sudo('apt-get install %s' % (' '.join(PACKAGE_LIST)))
    sudo('python3.6 -m pip install --upgrade pip')


def setup_database_postgresql():
    sudo('psql -c "CREATE USER %s WITH NOCREATEDB NOCREATEUSER " \
         "ENCRYPTED PASSWORD E\'%s\'"' % (DB_USER, DB_PASS), user='postgres')
    sudo('psql -c "CREATE DATABASE %s WITH OWNER %s"' % (
         DB_NAME, DB_USER), user='postgres')

def update_code():
    branch = local("git symbolic-ref --short -q HEAD", capture=True)
    local('git pull origin %s' % branch)


def install_virtualenv():
    local("cd .. ")
    sudo("mkdir myproject")
    sudo("mv burnweb_with_admin/ myproject/burnweb_with_admin")
    sudo("python3.6 -m venv myenv")
    sudo("source myenv/bin/activate")
    local("cd myproject/burnweb_with_admin")
    local("pip install -r requirements.txt")


def setup_gunicorn():
    local("cp gunicorn_setup/gunicorn.conf /etc/supervisor/conf.d/gunicorn.conf")
    sudo("mkdir /var/log/gunicorn/")
    sudo("touch /var/log/gunicorn/gunicorn.out.log")
    sudo("touch /var/log/gunicorn/gunicorn.err.log")

    local("cp gunicorn_setup/process_tasks.conf /etc/supervisor/conf.d/process_tasks.conf")
    sudo("mkdir /var/log/process_tasks/")
    sudo("touch /var/log/process_tasks/process_tasks.out.log")
    sudo("touch /var/log/process_tasks/process_tasks.err.log")


def setup_nginx():
    local("cp nginx_setup/burnweb_with_admin /etc/nginx/site-availabe/burnweb_with_admin")
    sudo("ln -s /etc/nginx/sites-available/burnweb_with_admin /etc/nginx/sites-enabled")
    sudo("nginx -t")
    restart_nginx()


def migrate():
    local('python manage.py makemigrations main')
    local('python manage.py makemigrations demo')
    local('python manage.py migrate')

def collectstatic():
    local('python manage.py collectstatic')

@task
def setup():
    install_package()
    setup_database_postgresql()
    update_code()
    install_virtualenv()
    migrate()
    collectstatic()
    setup_gunicorn()
    restart_supervisor()
    setup_nginx()
    restart_nginx()

@task
def restart():
    restart_supervisor()
    restart_nginx()
