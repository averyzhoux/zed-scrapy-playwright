from importlib.resources import files

# from importlib.resources.abc import Traversable
from pathlib import Path

HOME_HTML = "zed.home.html"
CUSTOM_HTML = "zed.custom.html"

JQ4 = "jquery-4.0.0.slim.min.js"

CLI_PARAM_NAME = "zed="

PACKAGE_NAME = "zed_sp_schedule"


def assets(file: str = ""):
    """获取包内 assets 文件夹的路径对象"""
    path = str(files(PACKAGE_NAME) / "assets")
    return Path(path) / file
