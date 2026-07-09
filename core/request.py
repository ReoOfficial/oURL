class Request:

    def __init__(
        self,
        url,
        method="GET",
        headers="None",
        body="None",
        timeout="15",
        verbose=False
    ):
        
        self.url = url
        self.method = method
        self.headers = headers or {}
        self.body = body
        self.timeout = timeout
        self.verbose = verbose
