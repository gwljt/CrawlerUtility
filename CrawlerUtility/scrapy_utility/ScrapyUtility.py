import base64


class NoProxyConfigError(Exception):
    pass


class FormatError(Exception):
    pass


class AbuyunProxyMiddleware(object):
    def __init__(self, proxy_server: str='',
                 proxy_user: str='',
                 proxy_password: str='',
                 spider_behind_proxy: list=None,
                 skip_proxy_keyword=None):
        if not all([proxy_server, proxy_user, proxy_password]):
            raise NoProxyConfigError('[Error] can not find the config of abuyun from settings.py,'
                                     'the KEYs are ABUYUN_PROXY_SERVER, ABUYUN_PROXY_USER, ABUYUN_PROXY_PASSWORD')

        if spider_behind_proxy is not None and not isinstance(spider_behind_proxy, list):
            raise FormatError('[Error] SPIDER_BEHIND_PROXY should be a list.')

        if skip_proxy_keyword is not None and not isinstance(skip_proxy_keyword, list):
            raise FormatError('[Error] SKIP_PROXY_KEYWORD should be a list.')

        self.proxy_server = proxy_server
        self.spider_under_proxy = spider_behind_proxy
        self.skip_proxy_keyword = skip_proxy_keyword if skip_proxy_keyword else []
        self.proxy_auth = "Basic " + base64.urlsafe_b64encode(bytes((proxy_user + ":" + proxy_password),
                                                                    "ascii")).decode("utf8")

    @classmethod
    def from_crawler(cls, crawler):
        return cls(proxy_server=crawler.settings['ABUYUN_PROXY_SERVER'],
                   proxy_user=crawler.settings['ABUYUN_PROXY_USER'],
                   proxy_password=crawler.settings['ABUYUN_PROXY_PASSWORD'],
                   spider_behind_proxy=crawler.settings['SPIDER_BEHIND_PROXY'],
                   skip_proxy_keyword=crawler.settings['SKIP_PROXY_KEYWORD'])

    def process_request(self, request, spider):
        for pattern in self.skip_proxy_keyword:
            if pattern in str(request.url):
                return
        if not self.spider_under_proxy or spider.name in self.spider_under_proxy:
            request.meta["proxy"] = self.proxy_server
            request.headers["Proxy-Authorization"] = self.proxy_auth
