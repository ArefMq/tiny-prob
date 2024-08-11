from threading import Thread
from typing import Any
from bottle import Bottle, static_file, template, ServerAdapter, request
from os.path import dirname, abspath, join


DEFAULT_INDEX_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TinyProb</title>
    <link rel="stylesheet" href="static/styles.css">
</head>

<body>
    <header>
        <div class="header-left">
            <img src="static/logo.png" alt="Logo" class="logo">
            <h1>TinyProb</h1>
        </div>
        <div class="header-right">
            <button id="refreshButton">♻️</button>
            <select id="refreshRate">
                <option value="100">100ms</option>
                <option value="500">500ms</option>
                <option value="1000">1sec</option>
                <option value="2000">2sec</option>
                <option value="5000">5sec</option>
                <option value="30000">30sec</option>
                <option value="60000">1min</option>
                <option value="300000">5min</option>
                <option value="1800000" selected>30min</option>
                <option value="3600000">1h</option>
                <option value="-1">Manual</option>
            </select>
        </div>
    </header>

    <main>
        <div class="panel" id="variables">
            <h2>Variables</h2>
            <table id="variablesTable">
                <thead>
                    <tr>
                        <th>Topic</th>
                        <th>Data</th>
                    </tr>
                </thead>
                <tbody>
                    <!-- Variable rows will be added here dynamically -->
                </tbody>
            </table>
            <div id="logs">
                <h2>Logs</h2>
                <ul id="logList">
                    <!-- Logs will be appended here dynamically -->
                </ul>
            </div>
        </div>
        <div class="panel" id="canvases">
            <h2>Canvases</h2>
            <button id="addCanvas">+ Add Canvas</button>
            <div id="canvasContainer">
                <!-- Canvases will be added here dynamically -->
            </div>
        </div>
    </main>

    <footer>
        <p>&copy; 2024 TinyProb. <a href="https://github.com/ArefMq/tiny-prob">TinyProb</a></p>
    </footer>
    <script src="/static/scanner.js"></script>
</body>
</html>
"""

DEFAULT_PORT = 8080
DEFAULT_BOTTLE_LOCAL_URL = f"http://127.0.0.1:{DEFAULT_PORT}/"


class TinyServer(ServerAdapter):
    server = None

    def run(self, handler):
        from wsgiref.simple_server import make_server, WSGIRequestHandler

        if self.quiet:
            class QuietHandler(WSGIRequestHandler):
                def log_request(*args, **kw):
                    pass

            self.options["handler_class"] = QuietHandler
        self.server = make_server(self.host, self.port, handler, **self.options)
        self.server.serve_forever()

    def stop(self):
        if self.server is None:
            return
        # self.server.server_close() <--- alternative but causes bad fd exception
        self.server.shutdown()


class WebServer(Bottle):
    def __init__(
        self,
        template_args: dict[str, Any] | None = None,
        static_root: str | None = None,
        open_browser: bool = False,
        ask_before_exit: bool = False,
    ) -> None:
        super().__init__()
        self.__app_thread: Thread | None = None
        self.__template_args = template_args or {}
        self.__static_root = static_root
        self.__open_browser_on_start = open_browser
        self.__ask_before_exit = ask_before_exit
        self.__server: TinyServer | None = None

        # Fix Routes
        self.route("/", callback=self.index)
        self.route("/static/<filename>", callback=self.static)

    def static(self, filename):
        root_path = (
            join(dirname(abspath(__file__)), "static")
            if self.__static_root is None
            else self.__static_root
        )
        return static_file(filename, root=root_path)

    def index(self):
        return template(DEFAULT_INDEX_TEMPLATE, **self.__template_args)

    def run_non_blocking(self, *args, **kwargs) -> None:
        """
        Same as run, but threaded.
        """
        self.stop_server()
        self.__app_thread = Thread(target=self.run, args=args, kwargs=kwargs)
        self.__app_thread.start()

    def stop_server(self, timeout: int | None = None) -> None:
        """
        Stop the webserver.
        """
        self.close()
        self.__server.stop()
        if self.__app_thread is not None and self.__app_thread.is_alive():
            self.__app_thread.join(timeout=timeout)
            self.__app_thread = None

    @staticmethod
    def OpenBrowser(url: str = DEFAULT_BOTTLE_LOCAL_URL) -> None:
        import webbrowser

        webbrowser.open(url, new=0, autoraise=True)

    def start(self, blocking: bool = False, open_browser: bool = False) -> None:
        self.__server = TinyServer(port=DEFAULT_PORT)
        args = {
            "debug": True,
            "reloader": False,
            "server": self.__server,
            "quiet": False,
        }
        if blocking:
            self.run(**args)
        else:
            self.run_non_blocking(**args)

        if open_browser:
            WebServer.OpenBrowser()
    
    def __enter__(self):
        self.start(open_browser=self.__open_browser_on_start)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.__ask_before_exit and exc_type is None:
            input("[Press Enter to continue]")
        self.stop_server(timeout=1)

    @staticmethod
    def _get_param(param: str, default: Any) -> Any:
        return request.query.get(param, default)
    
    @staticmethod
    def _post_param(param: str, default: Any) -> Any:
        return request.json.get(param, default)

if __name__ == "__main__":
    WebServer().run()
