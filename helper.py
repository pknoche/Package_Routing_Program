from datetime import datetime, time, timedelta


class TimeTracking:
    def __init__(self, route_start_time: time):
        current_date = datetime.today().date()
        current_time = route_start_time
        self.current_date_time = datetime.combine(current_date, current_time)

    def get_time(self) -> datetime:
        return self.current_date_time

    def add_time(self, hours: float):
        time_delta = timedelta(hours=hours)
        self.current_date_time += time_delta
