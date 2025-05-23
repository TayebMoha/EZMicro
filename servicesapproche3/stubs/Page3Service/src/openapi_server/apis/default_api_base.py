# coding: utf-8

from typing import ClassVar, Dict, List, Tuple  # noqa: F401

from pydantic import StrictStr


class BaseDefaultApi:
    subclasses: ClassVar[Tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BaseDefaultApi.subclasses = BaseDefaultApi.subclasses + (cls,)
    async def read_page1(
        self,
    ) -> str:
        ...


    async def read_page2(
        self,
    ) -> str:
        ...


    async def read_page3(
        self,
    ) -> str:
        ...


    async def read_root(
        self,
    ) -> str:
        ...
