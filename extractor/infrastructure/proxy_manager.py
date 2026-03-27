import random
from typing import List, Optional


class ProxyManager:
    def __init__(self, proxy_list: str):
        self.proxies = self._parse_proxy_list(proxy_list)
        self.current_index = 0

    def _parse_proxy_list(self, proxy_list: str) -> List[str]:
        if not proxy_list:
            return []
        return [p.strip() for p in proxy_list.split(",") if p.strip()]

    def get_next_proxy(self) -> Optional[str]:
        if not self.proxies:
            return None

        proxy = self.proxies[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.proxies)
        return proxy

    def get_random_proxy(self) -> Optional[str]:
        if not self.proxies:
            return None
        return random.choice(self.proxies)

    def has_proxies(self) -> bool:
        return len(self.proxies) > 0
