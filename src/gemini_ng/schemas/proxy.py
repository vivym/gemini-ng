from pydantic import Field

from httplib2 import ProxyInfo as HttpLib2ProxyInfo
from httplib2 import socks

from .base import BaseModel


class ProxyInfo(BaseModel):
    type: str = Field(..., description="Type of the proxy. E.g. 'http', 'https', 'socks5'.")

    host: str = Field(..., description="Host of the proxy.")

    port: int = Field(..., description="Port of the proxy.")

    username: str | None = Field(None, description="Username for the proxy.")

    password: str | None = Field(None, description="Password for the proxy.")

    def to_httplib2_proxy_info(self) -> HttpLib2ProxyInfo:
        socks.PROXY_TYPE_HTTP
        if self.type == "http":
            proxy_type = socks.PROXY_TYPE_HTTP
        elif self.type == "https":
            proxy_type = socks.PROXY_TYPE_HTTP
        elif self.type == "socks4":
            proxy_type = socks.PROXY_TYPE_SOCKS4
        elif self.type == "socks5":
            proxy_type = socks.PROXY_TYPE_SOCKS5
        else:
            raise ValueError(f"Invalid proxy type: {self.type}")

        return HttpLib2ProxyInfo(
            proxy_type=proxy_type,
            proxy_host=self.host,
            proxy_port=self.port,
            proxy_user=self.username,
            proxy_pass=self.password,
        )
