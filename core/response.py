class Response:

    def __init__(self, response, sent_headers=None):

        self.status_code = response.status_code
        self.reason = response.reason
        
        self.headers = response.headers
        self.body = response.text

        self.url = response.url,
        self.elapsed = response.elapsed

        self.cookies = response.cookies
        self.history = response.history

        self.sent_headers = sent_headers or {}

    def get_status_code(self):
        return self.status_code
    
    def get_headers(self):
        return self.headers
    
    def get_body(self):
        return self.body
    
    def get_reason(self):
        return self.reason
    
    def get_url(self):
        return self.url
    
    def get_elapsed(self):
        return self.elapsed
    
    def get_cookies(self):
        return self.cookies
    
    def get_history(self):
        return self.history
    
    def get_form_data(self):
        return self.form_data 
    
    def get_form_files(self):
        return self.form_files 
    
    def get_sent_headers(self):
        return self.sent_headers