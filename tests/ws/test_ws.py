import json

def test_websocket_echo_text(client):
    with client.websocket_connect("/ws/echo") as websocket:
        websocket.send_text("Hello WebSocket")
        data = websocket.receive_text()
        assert data == "Hello WebSocket"

def test_websocket_echo_binary(client):
    with client.websocket_connect("/ws/echo") as websocket:
        payload = bytes([0, 1, 2, 253, 254, 255])
        websocket.send_bytes(payload)
        data = websocket.receive_bytes()
        assert data == payload

def test_websocket_echo_large_message(client):
    with client.websocket_connect("/ws/echo") as websocket:
        payload = "x" * 100_000
        websocket.send_text(payload)
        data = websocket.receive_text()
        assert data == payload

def test_websocket_echo_json(client):
    with client.websocket_connect("/ws/echo") as websocket:
        json_msg = json.dumps({"message": "Hello WebSocket"})
        websocket.send_text(json_msg)
        data = websocket.receive_text()
        assert json.loads(data) == {"message": "Hello WebSocket"}

def test_websocket_heartbeat_ping(client):
    with client.websocket_connect("/ws/heartbeat") as websocket:
        websocket.send_json({"message": "ping"})
        data = websocket.receive_json()
        assert data == {"type": "heartbeat", "message": "pong"}

def test_websocket_heartbeat_message(client):
    with client.websocket_connect("/ws/heartbeat") as websocket:
        websocket.send_json({"message": "hello world"})
        data = websocket.receive_json()
        assert data == {"type": "message", "data": {"message": "hello world"}}

from starlette.websockets import WebSocketDisconnect
import pytest

def test_websocket_strict_heartbeat_timeout(client):
    with pytest.raises(WebSocketDisconnect) as exc:
        with client.websocket_connect("/ws/timeout/1") as websocket:
            websocket.receive_json()
    assert exc.value.code == 1008

def test_websocket_strict_heartbeat_success(client):
    with client.websocket_connect("/ws/timeout/1") as websocket:
        websocket.send_json({"message": "ping"})
        data = websocket.receive_json()
        assert data == {"type": "heartbeat", "message": "pong"}

def test_websocket_ticker(client):
    with client.websocket_connect("/ws/ticker/1") as websocket:
        data = websocket.receive_json()
        assert data == {"type": "ticker", "tick": 1, "interval": 1}

def test_websocket_ticker_invalid_interval(client):
    with pytest.raises(WebSocketDisconnect) as exc:
        with client.websocket_connect("/ws/ticker/0") as websocket:
            websocket.receive_json()
    assert exc.value.code == 1008

def test_websocket_close_with_code(client):
    with pytest.raises(WebSocketDisconnect) as exc:
        with client.websocket_connect("/ws/close/4001") as websocket:
            data = websocket.receive_json()
            assert data["type"] == "close"
            websocket.receive_text()  # next receive surfaces the close frame
    assert exc.value.code == 4001

def test_websocket_close_invalid_code(client):
    with pytest.raises(WebSocketDisconnect) as exc:
        with client.websocket_connect("/ws/close/1005") as websocket:
            websocket.receive_json()
            websocket.receive_text()
    assert exc.value.code == 1008

def test_websocket_auth_header(client):
    with client.websocket_connect(
            "/ws/auth",
            headers={"Authorization": "Bearer apidash-test-ws-token"}) as websocket:
        data = websocket.receive_json()
        assert data == {"type": "auth", "status": "authenticated"}
        websocket.send_text("hello")
        assert websocket.receive_text() == "hello"

def test_websocket_auth_query_token(client):
    with client.websocket_connect("/ws/auth?token=apidash-test-ws-token") as websocket:
        data = websocket.receive_json()
        assert data["status"] == "authenticated"

def test_websocket_auth_rejected(client):
    with pytest.raises(WebSocketDisconnect) as exc:
        with client.websocket_connect("/ws/auth") as websocket:
            websocket.receive_json()
    assert exc.value.code == 1008

def test_websocket_broadcast(client):
    with client.websocket_connect("/ws/broadcast") as ws1:
        with client.websocket_connect("/ws/broadcast") as ws2:
            ws1.send_text("hello")
            assert ws1.receive_text() == "hello"
            assert ws2.receive_text() == "hello"
