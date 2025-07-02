import pathlib
import sys
import socket
import base64
import json
import jcs
import uuid
import hashlib
import getpass
import os

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'src'))

from runtimeinfo import RuntimeInfo

def test_root_basic(tmp_path):
    r = RuntimeInfo(str(tmp_path))
    assert r.path == str(tmp_path)
    assert r.hostname is None or isinstance(r.hostname, str)
    assert r.ip_address is None or isinstance(r.ip_address, str)
    assert r.mac_address is None or isinstance(r.mac_address, str)
    assert r.username is None or isinstance(r.username, str)


def test_hostname_failure(monkeypatch):
    def bad_hostname():
        raise OSError('fail')

    monkeypatch.setattr(socket, 'gethostname', bad_hostname)
    monkeypatch.setattr(socket, 'getaddrinfo', lambda *a, **k: (_ for _ in ()).throw(RuntimeError('should not be called')))
    monkeypatch.setattr(uuid, 'getnode', lambda: 0x010203040506)

    r = RuntimeInfo('/tmp')
    assert r.hostname is None
    assert r.ip_address is None
    assert r.mac_address == '01:02:03:04:05:06'

def test_root_initialization():
    root = RuntimeInfo()
    assert root.hostname == socket.gethostname()
    assert root.username == getpass.getuser()


def test_root_default_path():
    expected = os.path.abspath(os.getcwd())
    root = RuntimeInfo()
    assert root.path == expected


def test_canonical_hash():
    data = {"b": 2, "a": 1}
    h = RuntimeInfo.canonical_hash(data)

    json_bytes = jcs.canonicalize(data)
    digest = hashlib.sha1(json_bytes).digest()
    expected = base64.urlsafe_b64encode(digest).decode('ascii').rstrip('=')[:10]
    assert h == expected


def test_to_json(tmp_path):
    r = RuntimeInfo(str(tmp_path))
    js = r.to_json()
    data = json.loads(js)
    assert data['path'] == str(tmp_path)
    assert data['username'] == r.username
    assert js == jcs.canonicalize(data).decode('utf-8')


def test_str(tmp_path):
    r = RuntimeInfo(str(tmp_path))
    s = str(r)
    data = json.loads(s)
    assert data['path'] == str(tmp_path)
    assert data['username'] == r.username


def test_exclude_loopback(monkeypatch):
    monkeypatch.setattr(socket, 'gethostname', lambda: 'testhost')

    def fake_addrinfo(*args, **kwargs):
        return [
            (socket.AF_INET, socket.SOCK_STREAM, 6, '', ('127.0.0.1', 0)),
            (socket.AF_INET, socket.SOCK_STREAM, 6, '', ('192.0.2.1', 0)),
        ]

    monkeypatch.setattr(socket, 'getaddrinfo', fake_addrinfo)

    r = RuntimeInfo('/tmp')
    assert r.ip_address == '192.0.2.1'


def test_loopback_only(monkeypatch):
    monkeypatch.setattr(socket, 'gethostname', lambda: 'testhost')
    monkeypatch.setattr(
        socket,
        'getaddrinfo',
        lambda *a, **k: [
            (socket.AF_INET, socket.SOCK_STREAM, 6, '', ('127.0.0.1', 0)),
            (socket.AF_INET6, socket.SOCK_STREAM, 6, '', ('::1', 0, 0, 0)),
        ],
    )

    r = RuntimeInfo('/tmp')
    assert r.ip_address is None
