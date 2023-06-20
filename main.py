import asyncio
import pprint
import subprocess

import hues
from flask import Flask, jsonify, request, render_template
from peewee import fn

import deskui
import models
import schedule

import schedulescript
import settings
from models import AccessLog, User,create_table


app = Flask(__name__)

@app.route('/', methods=['GET'])
def get_home_page():
    return render_template('index.html')



@app.route('/api/logs', methods=['GET'])
def get_logs():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    ip_address = request.args.get('ip_address')

    query = AccessLog.select()

    if start_date:
        query = query.where(AccessLog.date >= start_date)

    if end_date:
        query = query.where(AccessLog.date <= end_date)

    if ip_address:
        query = query.where(AccessLog.ip_address == ip_address)

    logs = [log.to_dict() for log in query]

    return jsonify(logs)


@app.route('/api/logs/group_by_ip', methods=['GET'])
def get_logs_group_by_ip():
    logs = (
        AccessLog
        .select(AccessLog.ip_address, fn.COUNT(AccessLog.id).alias('count'))
        .group_by(AccessLog.ip_address)
    )

    return jsonify([{'ip_address': log.ip_address, 'count': log.count} for log in logs])



@app.route('/api/logs/group_by_date', methods=['GET'])
def get_logs_group_by_date():
    logs = (
        AccessLog
        .select(AccessLog.date, fn.COUNT(AccessLog.id).alias('count'))
        .group_by(AccessLog.date)
    )

    return jsonify([{'date': log.date, 'count': log.count} for log in logs])

@app.route('/api', methods=['GET'])
def get_api_routes():
    routes = [
        {'route': '/api/logs', 'description': 'Retrieve logs based on filters (start_date, end_date, ip_address)'},
        {'route': '/api/logs/group_by_ip', 'description': 'Group logs by IP address'},
        {'route': '/api/logs/group_by_date', 'description': 'Group logs by date'}
    ]

    return jsonify(routes)
@app.route('/api/logs/get_by_ip', methods=['GET'])
def get_logs_by_ip():
    ip_address = request.args.get('ip_address')

    if not ip_address:
        return jsonify({'error': 'IP address is required.'}), 400

    with app.app_context():
        query = AccessLog.select().where(AccessLog.ip_address == ip_address)
        logs = [log.to_dict() for log in query]

    return jsonify(logs)



@app.route('/api/search', methods=['GET'])
def search_logs():
    search_query = request.args.get('query')

    query = AccessLog.select().where(AccessLog.api_url.contains(search_query))

    logs = [log.to_dict() for log in query]

    return jsonify(logs)

@app.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Bad request'}), 400


@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({'error': 'Internal server error'}), 500

def powersell_execute():
    command = f"{settings.power_shell_script_path}"


    process = subprocess.Popen(['powershell.exe', '-Command', command], stdout=subprocess.PIPE)
    result = process.communicate()[0].decode('utf-8')

    # Вывод результата
    print(result)

if __name__ == '__main__':
    log_file = settings.log_file  # Specify the path to the log file
    create_table()
    models.parse_logs(log_file)


    while True:
        print('Please select an option:')
        print('1) Group logs by IP address')
        print('2) Group logs by date')
        print('3) List API routes')
        print('4) Get logs by IP')
        print('5) Create user')
        print('6) Start GUI')
        print('7) Refresh Access Log')
        print('8) Add schedule task (windows)')
        print('0) Flask start')

        option = input('Enter your choice: ')

        if option == '1':
            with app.app_context():
                result = get_logs_group_by_ip()
                logs = result.json
                for log in logs:
                    print()
                    hues.info(f"IP Address: {log['ip_address']}")
                    hues.info(f"Count: {log['count']}")
                    print()
        elif option == '2':
            with app.app_context():
                result = get_logs_group_by_date()
                logs = result.json
                for log in logs:
                    print()
                    hues.info(f"Date: {log['date']}")
                    hues.info(f"Count: {log['count']}")
                    print()
        elif option == '3':
            with app.app_context():
                result = get_api_routes()
                routes = result.json
                for route in routes:
                    print()
                    hues.info(f"Route: {route['route']}")
                    hues.info(f"Description: {route['description']}")
                    print()
        elif option == '4':
            ip_address = input("Enter IP address: ")
            with app.app_context():
                query = AccessLog.select().where(AccessLog.ip_address == ip_address)
                logs = [log.to_dict() for log in query]

                for log in logs:
                    print()
                    hues.info(f"IP Address: {log['ip_address']}")
                    hues.info(f"Date: {log['date']}")
                    hues.info(f"Method: {log['method']}")
                    print()
        elif option == '5':
            login = input("Enter the login for the new user: ")
            password = input("Enter the password for the new user: ")

            with app.app_context():
                existing_user = User.select().where(User.login == login).first()
                if existing_user:
                    print("User with the same login already exists.")
                else:
                    new_user = User(login=login, password=password)
                    new_user.save()
                    print("User created successfully.")
        elif option == '6':
            deskui.run_app()
        elif option == '7':
            models.parse_logs(settings.log_file)
        elif option == '8':
            schedulescript.main()
            powersell_execute()
        elif option == '0':
            app.run()
        else:
            print('Invalid option. Please try again.')

        print('Exiting the application.')
