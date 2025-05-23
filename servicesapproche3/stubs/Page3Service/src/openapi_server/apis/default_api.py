# coding: utf-8

from typing import Dict, List  # noqa: F401
import importlib
import pkgutil

from openapi_server.apis.default_api_base import BaseDefaultApi
import openapi_server.impl

from fastapi import (  # noqa: F401
    APIRouter,
    Body,
    Cookie,
    Depends,
    Form,
    Header,
    HTTPException,
    Path,
    Query,
    Response,
    Security,
    status,
)

from openapi_server.models.extra_models import TokenModel  # noqa: F401
from pydantic import StrictStr


router = APIRouter()

ns_pkg = openapi_server.impl
for _, name, _ in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + "."):
    importlib.import_module(name)


@router.get(
    "/page1",
    responses={
        200: {"model": str, "description": "Page1 with square result"},
    },
    tags=["default"],
    summary="Return page1 HTML with square(4) result",
    response_model_by_alias=True,
)
async def read_page1(
) -> str:
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().read_page1()


@router.get(
    "/page2",
    responses={
        200: {"model": str, "description": "Page2 with cube result"},
    },
    tags=["default"],
    summary="Return page2 HTML with cube(2) result",
    response_model_by_alias=True,
)
async def read_page2(
) -> str:
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().read_page2()


@router.get(
    "/page3",
    responses={
        200: {"model": str, "description": "Page3 with combined calculation result"},
    },
    tags=["default"],
    summary="Return page3 HTML with combined result of add_five, cube, and square",
    response_model_by_alias=True,
)
async def read_page3(
) -> str:
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().read_page3()


@router.get(
    "/",
    responses={
        200: {"model": str, "description": "Index page"},
    },
    tags=["default"],
    summary="Return the index HTML page",
    response_model_by_alias=True,
)
async def read_root(
) -> str:
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().read_root()
