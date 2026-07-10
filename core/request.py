class Request:
    def __init__(
        self,
        method,
        url,
        headers=None,
        body=None,
        timeout=15,

        verbose=False,
        follow_redirects=False,
        insecure=False,

        auth=None,
        user_agent=None,

        output=None,
        head=False,

        cookies=None,
        cookie_jar=None,

        form_data=None,
        form_files=None,
    ):
        self.method = method
        self.url = url
        self.headers = headers or {}
        self.body = body
        self.timeout = timeout

        self.verbose = verbose
        self.follow_redirects = follow_redirects
        self.insecure = insecure

        self.auth = auth
        self.user_agent = user_agent

        self.output = output
        self.head = head

        self.cookies = cookies
        self.cookie_jar = cookie_jar

        self.form_data = form_data
        self.form_files = form_files or {}

        