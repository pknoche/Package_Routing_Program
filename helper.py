import datetime


def get_time() -> str:
    current_time = datetime.datetime.now()
    formatted_time = current_time.strftime('%H:%M:%S')
    return formatted_time
