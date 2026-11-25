import importlib.util
from pathlib import Path


def _load_typer():
    path = Path(__file__).parent / "bin" / "typer.py"
    spec = importlib.util.spec_from_file_location("local_typer", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


typer = _load_typer()


def test_dotool_controller_actions(tmp_path):
    log = tmp_path / "actions"
    controller = typer.DotoolController(command=["tee", str(log)])
    for char in "a b\n\t":
        controller.type(char)
    controller.tap("backspace")
    controller.close()

    assert log.read_text().splitlines() == [
        "type a",
        "key space",
        "type b",
        "key enter",
        "key tab",
        "key backspace",
    ]


def test_dotool_controller_ignores_carriage_return(tmp_path):
    log = tmp_path / "actions"
    controller = typer.DotoolController(command=["tee", str(log)])
    for char in "a\rb":
        controller.type(char)
    controller.close()

    assert log.read_text().splitlines() == ["type a", "type b"]
