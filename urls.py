import socket
import ssl
import pathlib


class Url:
    def __init__(self, url: str) -> None:
        self.scheme, self.fullpath = url.split("://")
        self.view_source = False
        if "view-source" in self.scheme:
            self.scheme = self.scheme.split(":")[1]
            self.view_source = True
        if "/" not in self.fullpath:
            self.fullpath = self.fullpath + "/"

        self.domain, self.path = self.fullpath.split("/", 1)
        self.path = "/" + self.path
        if self.scheme == "http":
            self.port = 80
        elif self.scheme == "https":
            self.port = 443

        if ":" in self.domain:
            self.domain, self.port = self.domain.split(":", 1)
            self.port = int(self.port)

    def make_request(self) -> str:
        """Makes connection to a server and does and http request receive the response extracts contents and returns the content"""
        if self.scheme == "file":  # handle for file://
            return self.handle_file_scheme()

        client = socket.socket(
            family=socket.AF_INET, type=socket.SOCK_STREAM, proto=socket.IPPROTO_TCP
        )
        if self.scheme == "https":  # ssl layer
            ctx = ssl.create_default_context()
            client = ctx.wrap_socket(client, server_hostname=self.domain)

        client.connect((self.domain, self.port))  # made connection to a server

        request = f"GET {self.path} HTTP/1.0\r\nHost: {self.domain}\r\nUser-Agent: chanzen\r\nConnection: close\r\n\r\n"  # make http request

        client.send(request.encode("utf-8"))

        response_stream = b""
        chunks = client.recv(1024)

        while chunks:
            response_stream += chunks
            chunks = client.recv(1024)
        response_stream = response_stream.decode()

        response_stream_list = response_stream.splitlines(True)
        self.status_line = response_stream_list[0]
        self.status_code = self.status_line.split(" ")[1]

        self.header = {}
        i = 0
        while i < len(response_stream_list):
            line = response_stream_list[i]

            if line == "\r\n":
                break
            if ":" in line:
                hkey, hvalue = line.split(":", 1)
                self.header[hkey.lower()] = hvalue

            i += 1
        if int(self.status_code) == 301 or int(self.status_code) == 302: #handle redirects make use of location header
            new_loc_url = self.header["location"].strip()
            re_url = Url(new_loc_url)
            content = re_url.make_request()
            return re_url.get_text_content(content, self.view_source)

        content = "".join(response_stream_list[i:])

        client.close()
        return self.get_text_content(content, view_source=self.view_source)

    def get_text_content(self, content: str, view_source: bool) -> str:
        """Extract only the text removing html syntax"""
        if view_source:
            return content
        skip = False
        text = ""
        symbol_to_skip = 0
        for index, char in enumerate(content):

            if symbol_to_skip > 0:  #< and > are properly treated
                symbol_to_skip -= 1
                continue

            if content[index : index + 4] == "&lt;":
                text += "<"
                symbol_to_skip = 3
                continue

            elif content[index : index + 4] == "&gt;":
                text += ">"
                symbol_to_skip = 3
                continue

            if char == "<":
                skip = True
            elif char == ">":
                skip = False
            elif not skip:
                text += char
        return text

    def handle_file_scheme(self) -> None:
        filepath = pathlib.Path(self.fullpath)

        if filepath.exists():
            return filepath.read_text()
        else:
            print("The file doesnt exist")

