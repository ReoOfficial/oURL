class Response:

    def __init__(self, response):
        self.status_code = response.status_code
        self.headers = response.headers
        self.body = response.text

    def get_status_code(self):
        return self.status_code
    
    def get_headers(self):
        return self.headers
    
    def get_body(self):
        return self.body