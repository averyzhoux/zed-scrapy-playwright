

class Translator:
    ...


    # def exec():
    #         print("兼容请求", request.url, request.meta)

    #         page = await self.provider.css()  # newpage

    #         if page is None:
    #             raise IgnoreRequest("此处不应该 page is None")

    #         # if request.meta.get("no-stealth") is None:
    #         #     print("已为 new page 自动施加 Stealth.apply_stealth_async")
    #         #     await Stealth().apply_stealth_async(page)
    #         if pms := request.meta.get("playwright_page_methods"):
    #             for pm in pms:
    #                 method_name = pm.method  # 方法名，如 "wait_for_selector"
    #                 args = pm.args  # 位置参数元组
    #                 kwargs = pm.kwargs  # 关键字参数字典

    #                 method = getattr(page, method_name)
    #                 await method(*args, **kwargs)

    #         response = scrapy.http.HtmlResponse(
    #             url=request.url,
    #             # status=200,
    #             # headers=None,
    #             # body=b"",
    #             # flags=None,
    #             request=request,
    #             # certificate=None,
    #             # ip_address=None,
    #             # protocol=None,
    #         )
    #         response._encoding = "utf-8"
    #         response._set_body(await page.content())
    #         return response
