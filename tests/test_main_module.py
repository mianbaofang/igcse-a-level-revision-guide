import runpy


def test_main_module_delegates_to_cli_main(monkeypatch):
    import intl_exam_guide.cli as cli

    monkeypatch.setattr(cli, "main", lambda: 7)

    try:
        runpy.run_module("intl_exam_guide.__main__", run_name="__main__")
    except SystemExit as exc:
        assert exc.code == 7
    else:
        raise AssertionError("Expected SystemExit")
