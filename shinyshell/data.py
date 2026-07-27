"""Data format methods for Shell."""

import json as _json
import base64
import re


from contextlib import contextmanager
class _DataMixin:
    """Data format viewers: json, markdown, xml, yaml_view, csv, sql_table, hexdump, jwt_decode, url_parse, base64_encode, base64_decode, uuid_gen, dict_diff."""

    def json(self, data, title: str | None = None) -> None:
        """Pretty-print JSON data with syntax colors."""
        print()
        if title:
            print(self._style(f"  {title}", "bold"))
        formatted = _json.dumps(data, indent=2, ensure_ascii=False, default=str)
        for line in formatted.split("\n"):
            # Color keys, strings, numbers, booleans
            colored = re.sub(r'"(.*?)"', lambda m: self._style(f'"{m.group(1)}"', color="green"), line)
            colored = re.sub(r': (".*?")', lambda m: f': {self._style(m.group(1), color="yellow")}', colored)
            colored = re.sub(r'\b(true|false|null)\b', lambda m: self._style(m.group(1), color="magenta"), colored)
            colored = re.sub(r'\b(\d+\.?\d*)\b', lambda m: self._style(m.group(1), color="cyan"), colored)
            print(f"  {colored}")
        print()

    def markdown(self, text: str) -> None:
        """Render basic markdown in the terminal."""
        from .icons import _ICONS

        lines = text.strip().split("\n")
        print()
        for line in lines:
            if line.startswith("# "):
                print(f"  {self._style(line[2:], 'bold', color='cyan')}")
            elif line.startswith("## "):
                print(f"  {self._style(line[3:], 'bold', color='blue')}")
            elif line.startswith("### "):
                print(f"  {self._style(line[4:], 'bold', color='magenta')}")
            elif line.startswith("- "):
                print(f"    {self._style(_ICONS['bullet'], color='cyan')} {line[2:]}")
            elif line.startswith("> "):
                print(f"  {self._style(f'│ {line[2:]}', color='bright_black')}")
            elif line.startswith("```"):
                continue
            elif line.strip().startswith("**") and line.strip().endswith("**"):
                print(f"  {self._style(line.strip()[2:-2], 'bold')}")
            else:
                print(f"  {line}")
        print()

    def xml(self, data: str, title: str | None = None) -> None:
        """Pretty XML viewer with syntax colors. sh.xml('<root><item>hello</item></root>')"""
        import xml.dom.minidom
        try:
            dom = xml.dom.minidom.parseString(data) if data.strip().startswith("<") else xml.dom.minidom.parse(data)
            pretty = dom.toprettyxml(indent="  ")
            print()
            if title:
                print(self._style(f"  {title}", "bold"))
            for line in pretty.split("\n"):
                if line.strip():
                    # Color tags and content
                    colored = re.sub(r'(</?)(\w+)([^>]*>)',
                                     lambda m: m.group(1) + self._style(m.group(2), color="cyan") + self._style(m.group(3), color="bright_black"),
                                     line)
                    colored = re.sub(r'>([^<]+)<', lambda m: '>' + self._style(m.group(1), color="yellow") + '<', colored)
                    print(f"  {colored}")
            print()
        except Exception as e:
            self.error(f"XML parse error: {e}")

    def yaml_view(self, text: str, title: str | None = None) -> None:
        """YAML viewer (basic). sh.yaml_view(yaml_string)"""
        print()
        if title:
            print(self._style(f"  {title}", "bold"))
        for line in text.strip().split("\n"):
            if ":" in line and not line.strip().startswith("#"):
                k, v = line.split(":", 1)
                print(f"  {self._style(k.strip(), color='green')}: {self._style(v.strip(), color='yellow')}")
            elif line.strip().startswith("#"):
                print(f"  {self._style(line, color='bright_black')}")
            else:
                print(f"  {line}")
        print()

    def csv(self, data, title: str | None = None) -> None:
        """Pretty CSV viewer. sh.csv('data.csv') or sh.csv(list_of_dicts)"""
        import csv as _csv
        import io
        if isinstance(data, str):
            try:
                with open(data) as f:
                    reader = _csv.DictReader(f)
                    rows = list(reader)
            except Exception as e:
                self.error(f"Cannot read CSV: {e}")
                return
        else:
            rows = data
        if rows:
            self.table(rows, title=title or "CSV Data")

    def sql_table(self, rows: list, title: str | None = None) -> None:
        """Pretty SQL query output. sh.sql_table([{'id':1,'name':'Alice'},...])"""
        self.table(rows, title=title or "Query Result", style="double")

    def hexdump(self, data: bytes, title: str | None = None, max_lines: int = 20) -> None:
        """Hex dump viewer. sh.hexdump(b'hello world')"""
        print()
        if title:
            print(self._style(f"  {title}", "bold"))
        for i in range(0, min(len(data), max_lines * 16), 16):
            chunk = data[i:i + 16]
            hex_part = " ".join(f"{b:02x}" for b in chunk)
            ascii_part = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
            print(f"  {i:08x}  {hex_part:48s}  {ascii_part}")
        print()

    def jwt_decode(self, token: str) -> None:
        """JWT decoder. sh.jwt_decode('eyJ...')"""
        import json as _json_local
        try:
            parts = token.split(".")
            if len(parts) >= 2:
                for i, part in enumerate(parts[:2]):
                    padded = part + "=" * (4 - len(part) % 4)
                    decoded = _json_local.loads(base64.urlsafe_b64decode(padded))
                    label = ["Header", "Payload"][i]
                    print(f"\n  {self._style(label, 'bold', color='cyan')}:")
                    self.json(decoded)
        except Exception as e:
            self.error(f"JWT decode: {e}")

    def url_parse(self, url: str) -> None:
        """URL parser. sh.url_parse('https://user:pass@example.com:8080/path?q=1#frag')"""
        from urllib.parse import urlparse, parse_qs
        p = urlparse(url)
        self.metrics({
            "Scheme": p.scheme,
            "Host": p.hostname or "",
            "Port": p.port or "default",
            "Path": p.path or "/",
            "Query": str(parse_qs(p.query)),
            "Fragment": p.fragment or "",
        })

    def base64_encode(self, text: str) -> str:
        """Base64 encode. sh.base64_encode('hello')"""
        return base64.b64encode(text.encode()).decode()

    def base64_decode(self, encoded: str) -> str:
        """Base64 decode"""
        return base64.b64decode(encoded).decode()

    def uuid_gen(self, count: int = 1) -> list:
        """UUID generator. sh.uuid_gen(5)"""
        import uuid
        uuids = [str(uuid.uuid4()) for _ in range(count)]
        print()
        for u in uuids:
            print(f"  {self._style(u, color='cyan')}")
        print()
        return uuids

    def dict_diff(self, old: dict, new: dict, title: str | None = None) -> None:
        """Deep dictionary comparison. sh.dict_diff({'a':1}, {'a':2,'b':3})"""
        print()
        if title:
            print(self._style(f"  {title}", "bold"))
        all_keys = set(old.keys()) | set(new.keys())
        for key in sorted(all_keys):
            if key not in old:
                print(f"  + {self._style(str(key), color='green')}: {self._style(str(new[key]), color='green')}")
            elif key not in new:
                print(f"  - {self._style(str(key), color='red')}: {self._style(str(old[key]), color='red')}")
            elif old[key] != new[key]:
                print(f"  ~ {key}: {self._style(str(old[key]), color='red')} → {self._style(str(new[key]), color='green')}")
            else:
                print(f"    {key}: {old[key]}")
        print()
