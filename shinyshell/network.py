"""Network utility methods for Shell."""

import time
import urllib.request
import json as _json
import socket


class _NetworkMixin:
    """Network utilities: http, network_ping, network_status, dns_lookup, ip_info."""

    def http(self, method: str, url: str, headers: dict | None = None,
             body: str | None = None) -> None:
        """Pretty HTTP request/response viewer. sh.http('GET', 'https://httpbin.org/json')"""
        print()
        self.info(f"{method} {url}")
        try:
            req = urllib.request.Request(url, method=method, data=body.encode() if body else None)
            if headers:
                for k, v in headers.items():
                    req.add_header(k, v)
            start = time.perf_counter()
            resp = urllib.request.urlopen(req, timeout=10)
            elapsed = (time.perf_counter() - start) * 1000
            status_color = "green" if resp.status < 300 else "red" if resp.status >= 400 else "yellow"
            self._style("", color="")
            print(f"  {self._style(f'HTTP {resp.status}', 'bold', color=status_color)} {self._style(f'{elapsed:.0f}ms', color='bright_black')}")
            print(f"  {self._style('Headers:', color='bright_black')}")
            for k, v in resp.headers.items():
                print(f"    {self._style(k, color='green')}: {v}")
            # Show first 500 chars of body
            resp_body = resp.read().decode('utf-8', errors='replace')[:500]
            if resp_body:
                print(f"  {self._style('Body (first 500 chars):', color='bright_black')}")
                for line in resp_body.split("\n"):
                    print(f"    {line}")
        except Exception as e:
            self.error(f"HTTP error: {str(e)[:80]}")
        print()

    def network_ping(self, host: str, count: int = 4) -> None:
        """Simple ping with visual output. sh.network_ping('google.com')"""
        import subprocess
        import platform
        print()
        self.info(f"Pinging {host}...")
        cmd = ["ping", "-n" if platform.system() == "Windows" else "-c", str(count), host]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            for line in result.stdout.split("\n"):
                if "time=" in line or "time<" in line or "ms" in line:
                    print(f"  {self._style('⚡', color='cyan')} {line.strip()}")
            if result.returncode == 0:
                self.success(f"{host} is reachable")
            else:
                self.error(f"{host} unreachable")
        except Exception as e:
            self.error(f"Ping failed: {e}")

    def network_status(self, url: str) -> None:
        """Check HTTP status with visual output. sh.network_status('https://api.example.com')"""
        print()
        try:
            req = urllib.request.Request(url, method="HEAD")
            resp = urllib.request.urlopen(req, timeout=5)
            status = resp.status
            if status < 300:
                self.success(f"{url} → {status} OK ({resp.headers.get('Server', '?')})")
            elif status < 400:
                self.warning(f"{url} → {status} Redirect")
            else:
                self.error(f"{url} → {status} Error")
        except Exception as e:
            self.error(f"{url} → {str(e)[:60]}")

    def dns_lookup(self, domain: str) -> None:
        """DNS lookup. sh.dns_lookup('google.com')"""
        print()
        try:
            ips = socket.getaddrinfo(domain, None)
            self.success(f"{domain}:")
            seen = set()
            for ip in ips:
                addr = ip[4][0]
                if addr not in seen:
                    seen.add(addr)
                    print(f"    {addr}")
        except Exception as e:
            self.error(f"DNS error: {e}")
        print()

    def ip_info(self, ip: str | None = None) -> None:
        """IP geolocation. sh.ip_info('8.8.8.8')"""
        import json as _json_local
        try:
            url = f"http://ip-api.com/json/{ip or ''}"
            resp = urllib.request.urlopen(url, timeout=5)
            data = _json_local.loads(resp.read())
            if data.get("status") == "success":
                self.metrics({
                    "IP": data.get("query", ""),
                    "Country": data.get("country", ""),
                    "City": data.get("city", ""),
                    "ISP": data.get("isp", ""),
                    "Org": data.get("org", ""),
                })
        except Exception as e:
            self.error(f"IP lookup: {e}")
