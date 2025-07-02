import pathlib
import sys
import json

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'src'))

from runtimeinfo.cli import main as root_main


def test_root_cli_json(tmp_path, capsys):
    root_main([str(tmp_path), '--json'])
    out = capsys.readouterr().out.strip()
    data = json.loads(out)
    assert data['path'] == str(tmp_path)


def test_root_cli_default(tmp_path, capsys):
    root_main([str(tmp_path)])
    out = capsys.readouterr().out.strip()
    data = json.loads(out)
    assert data['path'] == str(tmp_path)
