class YahooResponseError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class NewsResponseError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class TimeFrameError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)