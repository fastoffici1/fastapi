from base64 import b64encode

from requests.auth import HTTPBasicAuth
from starlette.testclient import TestClient

from fastapi import FastAPI, Security
from fastapi.security import HTTPBasic, HTTPBasicCredentials

app = FastAPI()

security = HTTPBasic()


@app.get("/users/me")
def read_current_user(credentials: HTTPBasicCredentials = Security(security)):
    return {"username": credentials.username, "password": credentials.password}


client = TestClient(app)

openapi_schema = {
    "openapi": "3.0.2",
    "info": {"title": "Fast API", "version": "0.1.0"},
    "paths": {
        "/users/me": {
            "get": {
                "responses": {
                    "200": {
                        "description": "Successful Response",
                        "content": {"application/json": {"schema": {}}},
                    }
                },
                "summary": "Read Current User Get",
                "operationId": "read_current_user_users_me_get",
                "security": [{"HTTPBasic": []}],
            }
        }
    },
    "components": {
        "securitySchemes": {"HTTPBasic": {"type": "http", "scheme": "basic"}}
    },
}


def test_openapi_schema():
    response = client.get("/openapi.json")
    assert response.status_code == 200
    assert response.json() == openapi_schema


def test_security_http_basic():
    auth = HTTPBasicAuth(username="john", password="secret")
    response = client.get("/users/me", auth=auth)
    assert response.status_code == 200
    assert response.json() == {"username": "john", "password": "secret"}


def test_security_http_basic_no_credentials():
    response = client.get("/users/me")
    assert response.status_code == 403
    assert response.json() == {"detail": "Not authenticated"}


def test_security_http_basic_invalid_credentials():
    response = client.get(
        "/users/me", headers={"Authorization": "Basic notabase64token"}
    )
    assert response.status_code == 403
    assert response.json() == {"detail": "Invalid authentication credentials"}


def test_security_http_basic_non_basic_credentials():
    payload = b64encode(b"johnsecret").decode("ascii")
    auth_header = f"Basic {payload}"
    response = client.get("/users/me", headers={"Authorization": auth_header})
    assert response.status_code == 403
    assert response.json() == {"detail": "Invalid authentication credentials"}
