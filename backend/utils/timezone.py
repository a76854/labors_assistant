"""统一的北京时间工具。"""

from datetime import datetime, timedelta, timezone


BEIJING_TIMEZONE = timezone(timedelta(hours=8), name="Asia/Shanghai")


def now_beijing() -> datetime:
    """返回当前北京时间。"""
    return datetime.now(BEIJING_TIMEZONE)
