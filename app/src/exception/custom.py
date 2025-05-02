class AttendanceError(Exception):
    def __init__(self, message: str, data: dict):
        self.message = message
        self.data = data
