from typing import Optional

import pytest
from dirty_equals import IsDict, IsStr
from fastapi import APIRouter, Depends, FastAPI
from fastapi.testclient import TestClient

app = FastAPI()

router = APIRouter()


async def common_parameters(q: str, skip: int = 0, limit: int = 100):
    return {"q": q, "skip": skip, "limit": limit}


@app.get("/main-depends/")
async def main_depends(commons: dict = Depends(common_parameters)):
    return {"in": "main-depends", "params": commons}


@app.get("/decorator-depends/", dependencies=[Depends(common_parameters)])
async def decorator_depends():
    return {"in": "decorator-depends"}


@router.get("/router-depends/")
async def router_depends(commons: dict = Depends(common_parameters)):
    return {"in": "router-depends", "params": commons}


@router.get("/router-decorator-depends/", dependencies=[Depends(common_parameters)])
async def router_decorator_depends():
    return {"in": "router-decorator-depends"}


app.include_router(router)

client = TestClient(app)


async def overrider_dependency_simple(q: Optional[str] = None):
    return {"q": q, "skip": 5, "limit": 10}


async def overrider_sub_dependency(k: str):
    return {"k": k}


async def overrider_dependency_with_sub(msg: dict = Depends(overrider_sub_dependency)):
    return msg


def test_main_depends(insert_assert):
    response = client.get("/main-depends/")
    assert response.status_code == 422
    # insert_assert(response.json())
    assert response.json() == IsDict(
        {
            "detail": [
                {
                    "type": "missing",
                    "loc": ["query", "q"],
                    "msg": "Field required",
                    "input": None,
                    "url": IsStr(regex=r"^https://errors\.pydantic\.dev/.*/v/missing"),
                }
            ]
        }
    ) | IsDict(
        # TODO: remove when deprecating Pydantic v1
        {
            "detail": [
                {
                    "loc": ["query", "q"],
                    "msg": "field required",
                    "type": "value_error.missing",
                }
            ]
        }
    )


def test_main_depends_q_foo():
    response = client.get("/main-depends/?q=foo")
    assert response.status_code == 200
    assert response.json() == {
        "in": "main-depends",
        "params": {"q": "foo", "skip": 0, "limit": 100},
    }


def test_main_depends_q_foo_skip_100_limit_200():
    response = client.get("/main-depends/?q=foo&skip=100&limit=200")
    assert response.status_code == 200
    assert response.json() == {
        "in": "main-depends",
        "params": {"q": "foo", "skip": 100, "limit": 200},
    }


def test_decorator_depends(insert_assert):
    response = client.get("/decorator-depends/")
    assert response.status_code == 422
    # insert_assert(response.json())
    assert response.json() == IsDict(
        {
            "detail": [
                {
                    "type": "missing",
                    "loc": ["query", "q"],
                    "msg": "Field required",
                    "input": None,
                    "url": IsStr(regex=r"^https://errors\.pydantic\.dev/.*/v/missing"),
                }
            ]
        }
    ) | IsDict(
        # TODO: remove when deprecating Pydantic v1
        {
            "detail": [
                {
                    "loc": ["query", "q"],
                    "msg": "field required",
                    "type": "value_error.missing",
                }
            ]
        }
    )


def test_decorator_depends_q_foo():
    response = client.get("/decorator-depends/?q=foo")
    assert response.status_code == 200
    assert response.json() == {"in": "decorator-depends"}


def test_decorator_depends_q_foo_skip_100_limit_200():
    response = client.get("/decorator-depends/?q=foo&skip=100&limit=200")
    assert response.status_code == 200
    assert response.json() == {"in": "decorator-depends"}


def test_router_depends():
    response = client.get("/router-depends/")
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "loc": ["query", "q"],
                "msg": "field required",
                "type": "value_error.missing",
            }
        ]
    }


def test_router_depends_q_foo():
    response = client.get("/router-depends/?q=foo")
    assert response.status_code == 200
    assert response.json() == {
        "in": "router-depends",
        "params": {"q": "foo", "skip": 0, "limit": 100},
    }


def test_router_depends_q_foo_skip_100_limit_200():
    response = client.get("/router-depends/?q=foo&skip=100&limit=200")
    assert response.status_code == 200
    assert response.json() == {
        "in": "router-depends",
        "params": {"q": "foo", "skip": 100, "limit": 200},
    }


def test_router_decorator_depends():
    response = client.get("/router-decorator-depends/")
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "loc": ["query", "q"],
                "msg": "field required",
                "type": "value_error.missing",
            }
        ]
    }


def test_router_decorator_depends_q_foo():
    response = client.get("/router-decorator-depends/?q=foo")
    assert response.status_code == 200
    assert response.json() == {"in": "router-decorator-depends"}


def test_router_decorator_depends_q_foo_skip_100_limit_200():
    response = client.get("/router-decorator-depends/?q=foo&skip=100&limit=200")
    assert response.status_code == 200
    assert response.json() == {"in": "router-decorator-depends"}


@pytest.mark.parametrize(
    "url,status_code,expected",
    [
        (
            "/main-depends/",
            200,
            {"in": "main-depends", "params": {"q": None, "skip": 5, "limit": 10}},
        ),
        (
            "/main-depends/?q=foo",
            200,
            {"in": "main-depends", "params": {"q": "foo", "skip": 5, "limit": 10}},
        ),
        (
            "/main-depends/?q=foo&skip=100&limit=200",
            200,
            {"in": "main-depends", "params": {"q": "foo", "skip": 5, "limit": 10}},
        ),
        ("/decorator-depends/", 200, {"in": "decorator-depends"}),
        (
            "/router-depends/",
            200,
            {"in": "router-depends", "params": {"q": None, "skip": 5, "limit": 10}},
        ),
        (
            "/router-depends/?q=foo",
            200,
            {"in": "router-depends", "params": {"q": "foo", "skip": 5, "limit": 10}},
        ),
        (
            "/router-depends/?q=foo&skip=100&limit=200",
            200,
            {"in": "router-depends", "params": {"q": "foo", "skip": 5, "limit": 10}},
        ),
        ("/router-decorator-depends/", 200, {"in": "router-decorator-depends"}),
    ],
)
def test_override_simple(url, status_code, expected):
    app.dependency_overrides[common_parameters] = overrider_dependency_simple
    response = client.get(url)
    assert response.status_code == status_code
    assert response.json() == expected
    app.dependency_overrides = {}


@pytest.mark.parametrize(
    "url,status_code,expected",
    [
        (
            "/main-depends/",
            422,
            {
                "detail": [
                    {
                        "loc": ["query", "k"],
                        "msg": "field required",
                        "type": "value_error.missing",
                    }
                ]
            },
        ),
        (
            "/main-depends/?q=foo",
            422,
            {
                "detail": [
                    {
                        "loc": ["query", "k"],
                        "msg": "field required",
                        "type": "value_error.missing",
                    }
                ]
            },
        ),
        ("/main-depends/?k=bar", 200, {"in": "main-depends", "params": {"k": "bar"}}),
        (
            "/decorator-depends/",
            422,
            {
                "detail": [
                    {
                        "loc": ["query", "k"],
                        "msg": "field required",
                        "type": "value_error.missing",
                    }
                ]
            },
        ),
        (
            "/decorator-depends/?q=foo",
            422,
            {
                "detail": [
                    {
                        "loc": ["query", "k"],
                        "msg": "field required",
                        "type": "value_error.missing",
                    }
                ]
            },
        ),
        ("/decorator-depends/?k=bar", 200, {"in": "decorator-depends"}),
        (
            "/router-depends/",
            422,
            {
                "detail": [
                    {
                        "loc": ["query", "k"],
                        "msg": "field required",
                        "type": "value_error.missing",
                    }
                ]
            },
        ),
        (
            "/router-depends/?q=foo",
            422,
            {
                "detail": [
                    {
                        "loc": ["query", "k"],
                        "msg": "field required",
                        "type": "value_error.missing",
                    }
                ]
            },
        ),
        (
            "/router-depends/?k=bar",
            200,
            {"in": "router-depends", "params": {"k": "bar"}},
        ),
        (
            "/router-decorator-depends/",
            422,
            {
                "detail": [
                    {
                        "loc": ["query", "k"],
                        "msg": "field required",
                        "type": "value_error.missing",
                    }
                ]
            },
        ),
        (
            "/router-decorator-depends/?q=foo",
            422,
            {
                "detail": [
                    {
                        "loc": ["query", "k"],
                        "msg": "field required",
                        "type": "value_error.missing",
                    }
                ]
            },
        ),
        ("/router-decorator-depends/?k=bar", 200, {"in": "router-decorator-depends"}),
    ],
)
def test_override_with_sub(url, status_code, expected):
    app.dependency_overrides[common_parameters] = overrider_dependency_with_sub
    response = client.get(url)
    assert response.status_code == status_code
    assert response.json() == expected
    app.dependency_overrides = {}
