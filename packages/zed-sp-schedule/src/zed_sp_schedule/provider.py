import asyncio
import enum
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any

# import scrapy.http
from playwright.async_api import (
    Browser,
    BrowserContext,
    Page,
    Playwright,
    async_playwright,
)

import zed_scrapy_playwright.interface

# from playwright_stealth import Stealth
# from scrapy import Request, crawler, signals
# from scrapy.exceptions import IgnoreRequest
from zed_scrapy_playwright import ExecParam, ZedRequest
from zed_sp_schedule import constants as C
from zed_sp_schedule import functions


class PageStatus(str, enum.Enum):
    """页面状态"""

    @staticmethod
    def _generate_next_value_(name, start, count, last_values) -> str:
        return name  # 返回成员名字作为值

    Unmount = enum.auto()
    Leisure = enum.auto()
    BeUsing = enum.auto()
    Cooling = enum.auto()


class PageData(str, enum.Enum):
    @staticmethod
    def _generate_next_value_(name, start, count, last_values) -> str:
        return f"data-{name}"  # 返回 data-{name} 作为值

    address = enum.auto()
    status = enum.auto()


print(list(PageStatus))
print(list(PageData))


@dataclass
class ObjectProxy:
    page: Page | BrowserContext | Browser | Playwright
    queue: asyncio.Queue[ZedRequest] = field(default_factory=asyncio.Queue)

    async def x(self):
        for i in range(self.queue.qsize()):
            r = await self.queue.get()


class Scheduler(zed_scrapy_playwright.interface.Provider):
    """处理 Playwright 对象的调用"""

    async def start(self):
        if self.config is None:
            raise ValueError

        # 1. 创建基础容器
        self.playwright_context_manager = async_playwright()
        self.playwright = await self.playwright_context_manager.start()
        self.default_browser = await self.playwright.chromium.launch(
            **self.config["chrome_params"]
        )
        self.default_context = await self.default_browser.new_context(no_viewport=True)
        self.default_page = await self.default_context.new_page()
        # 2. 更新页面内容
        await self.init_home_page()
        # 3. 绑定基础变量
        await self.bind_defaults()
        # 4. 防止变量丢失
        self.objs: dict[str, ObjectProxy] = {}
        # for obj in [
        #     self.playwright,
        #     self.default_browser,
        #     self.default_context,
        #     self.default_page,
        # ]:
        #     self.objs[str(id(obj))] = obj
        return self

    async def init_home_page(self):
        home = self.default_page
        await home.goto("about:_blank")
        h, m = functions.content()
        await home.set_content(h)
        await home.evaluate(C.assets(C.JQ4).read_text(encoding="utf-8"))
        await home.evaluate(
            # "(m) => document.querySelector('main').outerHTML = m;",
            "(m) => { $('main').replaceWith(m); }",
            m,
        )
        # scripts = await home.locator("main script").all()
        # [await home.evaluate(await s.text_content() or "") for s in scripts]

    # async def bind(self, selector: str, address): ...

    async def bind_defaults(self):
        async def bind_default(selector: str, obj):
            home = self.default_page
            op = ObjectProxy(obj)
            self.objs[str(id(op))] = op
            await home.evaluate(
                """([s,v,status]) => { $(s).addClass('default').attr('data-address',v).attr('data-status', status) }""",
                [selector, id(op), PageStatus.Leisure],
            )

        await bind_default("playwright:first", self.playwright)
        await bind_default("browser:first", self.default_browser)
        await bind_default("context:first", self.default_context)
        await self.default_page.evaluate("""$('context').prepend($('<page></page>'))""")
        await bind_default("page:first", self.default_page)

    async def close(self):
        await self.default_browser.close()
        await self.playwright.stop()
        await self.playwright_context_manager.__aexit__()

    async def css(self, selector) -> list[ObjectProxy]:
        """此处只负责取 TODO"""

        elements = await self.default_page.locator(selector).all()
        addresses = [await e.get_attribute(PageData.address.value) for e in elements]

        def get(a: str | None):
            if a is None:  # 当注册了，但没绑定
                op = ObjectProxy() # 那就创建并绑定
                return op
            if op := self.objs.get(a):
                return op
            else:
                raise RuntimeError(f"")

        objects = [get(a) for a in addresses]
        return objects
        # rank = [
        #     PageStatus.Leisure,
        #     PageStatus.Cooling,
        #     PageStatus.BeUsing,
        #     PageStatus.Unmount,
        #     None,
        # ]

        # def sort_(e):
        #     status = asyncioe.get_attribute(PageData.status)
        #     return rank.index(status)

        # elements.sort(key=sort_)
        address: str | None = None

        for e in elements:  # TODO 这里的排队逻辑有待理清
            status = await e.get_attribute(PageData.status)

            match status:
                case None:
                    ...
                case PageStatus.Unmount:
                    ...
                case PageStatus.Leisure:
                    address = await e.get_attribute(PageData.address)

                case PageStatus.BeUsing:
                    ...
                case PageStatus.Cooling:
                    ...

        if address is None:
            raise ValueError()

        if obj := self.objs.get(int(address)):
            return obj
        else:
            raise KeyError()

    async def takeover(self, request):
        if request.selector is None:
            page = await self.default_context.new_page()

        ops = await self.css(request.selector)
        for op in ops:  # 每个都进入排队
            await op.queue.put(request)
