import os
from pathlib import Path

import pytest

# import playwright.sync_api as psi


def test_config_check():
    import zed_sp_schedule.functions as zsps

    Z = "zed.custom.html"
    F = f"tests/{Z}"

    # 检查指定文件
    x = zsps.check(
        _testing_params={"sys_argv": ["python", "main.py", "-a", f"zed={F}"]}
    )
    assert x.resolve() == Path(F).resolve(), f"{x.resolve()}, {Path(F).resolve()}"

    # 检查默认文件
    x = zsps.check()
    assert x.resolve() == Path(Z).resolve()

    # 检查内置文件
    os.chdir("./tmp")
    x = zsps.check()
    os.chdir("..")
    assert x

    # 检查无实文件
    with pytest.raises(FileNotFoundError):
        zsps.check(_testing_params={"sys_argv": ["python", "main.py", "-a", "zed="]})
        zsps.check(
            _testing_params={"sys_argv": ["python", "main.py", "-a", "zed=none"]}
        )


def test_scheduler():
    from zed_sp_schedule import Scheduler

    # x = Scheduler()
