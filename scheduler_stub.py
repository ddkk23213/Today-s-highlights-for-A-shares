"""示例调度脚本。

该脚本演示如何在固定时间调用 `runner.py`。
实际部署时可改用 crontab、systemd 或 CI 平台。
"""
from __future__ import annotations

import datetime as dt
import sched
import subprocess
import time


def schedule_run(s: sched.scheduler, hour: int, minute: int, slot: str) -> None:
    def task() -> None:
        subprocess.run(["python", "runner.py", "--slot", slot], check=False)
        # 下一天同一时间再次执行
        s.enter(24 * 3600, 1, task)

    now = dt.datetime.now()
    first = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if first < now:
        first += dt.timedelta(days=1)
    delay = (first - now).total_seconds()
    s.enter(delay, 1, task)


def main() -> None:
    s = sched.scheduler(time.time, time.sleep)
    schedule_run(s, 7, 30, "morning")
    schedule_run(s, 12, 5, "noon")
    schedule_run(s, 15, 10, "close")
    s.run()


if __name__ == "__main__":
    main()
