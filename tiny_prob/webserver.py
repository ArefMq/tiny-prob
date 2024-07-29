from threading import Thread
from typing import Any
from bottle import Bottle, static_file, template
from os.path import dirname, abspath, join


index_template_string = """
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
                <option value="1000" selected>1sec</option>
                <option value="2000">2sec</option>
                <option value="5000">5sec</option>
                <option value="30000">30sec</option>
                <option value="60000">1min</option>
                <option value="300000">5min</option>
                <option value="1800000">30min</option>
                <option value="3600000">1h</option>
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
                        <th>Value</th>
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


class WebServer(Bottle):
    def __init__(
        self,
        template_args: dict[str, Any] | None = None,
        static_root: str | None = None,
    ) -> None:
        super().__init__()
        self.__app_thread: Thread | None = None
        self.__template_args = template_args or {}
        self.__static_root = static_root

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
        return template(index_template_string, **self.__template_args)

    def run_non_blocking(self, *args, **kwargs) -> None:
        """
        Same as run, but threaded.
        """
        self.stop()
        self.__app_thread = Thread(target=self.run, args=args, kwargs=kwargs)
        self.__app_thread.start()

    def stop_server(self, timeout: int | None = None) -> None:
        """
        Stop the webserver.
        """
        self.close()  # FIXME: this does not work
        if self.__app_thread is not None and self.__app_thread.is_alive():
            self.__app_thread.join(timeout=timeout)
            self.__app_thread = None


if __name__ == "__main__":
    WebServer().run()
