import re
from datetime import datetime
from models import AccessLog, create_tables


def parse_logs(log_file):
    with open(log_file, 'r') as file:
        logs = file.readlines()

    log_pattern = r'(\d+\.\d+\.\d+\.\d+) - - \[(.*?)\] "(.*?)" (\d+) (\d+) "(.*?)" "(.*?)"'

    create_tables()


    for log in logs:
        match = re.match(log_pattern, log)
        if match:
            ip_address = match.group(1)
            date_str = match.group(2)
            http_method = match.group(3)
            response_code = int(match.group(4))
            content_length = int(match.group(5))
            user_agent = match.group(7)

            # Преобразуем строку даты в объект datetime
            date = datetime.strptime(date_str, "%d/%b/%Y:%H:%M:%S %z")

            # Создаем запись в базе данных
            AccessLog.create(ip_address=ip_address, date=date, http_method=http_method,
                            response_code=response_code, user_agent=user_agent)

    print("Логи успешно сохранены в базе данных.")


# Точка входа в программу
if __name__ == '__main__':
    log_file = 'access_logs.txt'  # Укажите путь к файлу с логами
    parse_logs(log_file)
