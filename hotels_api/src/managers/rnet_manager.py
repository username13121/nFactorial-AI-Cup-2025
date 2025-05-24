import random

import rnet
from src import tools

class RnetManager:
    def __init__(self, proxy: str | None = None):
        self.proxy = proxy
        rnet_init_kwargs = {}
        if proxy != "":
            username, password, host, port = proxy.replace('@', ':').split(':')
            rnet_init_kwargs["proxies"] = [
                rnet.Proxy.https(
                    url=f"{host}:{port}",
                    username=username,
                    password=password
                ),
                rnet.Proxy.http(
                    url=f"{host}:{port}",
                    username=username,
                    password=password
                )
            ]

        self.rnet_client = rnet.Client(impersonate=random.choice(tools.rnet_impersonations), **rnet_init_kwargs)
    @classmethod
    def init_random_proxy(cls):
        proxy = random.choice(tools.proxies)
        return cls(proxy=proxy)