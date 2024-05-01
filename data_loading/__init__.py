from contextlib import contextmanager
import importlib.resources as pkg_resources

__all__ = (
    "make_package_file_loader",
    "make_package_string_loader",
    "make_package_binary_loader"
)


def make_package_file_loader(package, data_type: str):
    @contextmanager
    def _file_loader(name: str):
        file_name = f"{name}.{data_type}"
        file = None
        try:
            with pkg_resources.path(package, file_name) as path:
                file = open(path)
            yield file
        finally:
            if file is not None:
                file.close()

    return _file_loader


def make_package_string_loader(package, data_type: str, encoding: str = "utf-8"):
    def _str_loader(name: str):
        file_name = f"{name}.{data_type}"
        return pkg_resources.read_text(package, file_name, encoding=encoding)
    return _str_loader


def make_package_binary_loader(package, data_type: str):
    def _binary_loader(name: str):
        file_name = f"{name}.{data_type}"
        return pkg_resources.read_binary(package, file_name)
    return _binary_loader
