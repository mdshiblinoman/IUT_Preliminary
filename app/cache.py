"""In-memory response caches for read-heavy reporting endpoints.

Usage reports and per-room availability are relatively expensive to compute and
are read far more often than the underlying data changes, so results are cached
and invalidated when the data they depend on is modified.
"""

_report_cache: dict[tuple, dict] = {}
_availability_cache: dict[tuple, dict] = {}


def get_report(org_id: int, frm: str, to: str):
    return _report_cache.get((org_id, frm, to))


def set_report(org_id: int, frm: str, to: str, value: dict) -> None:
    _report_cache[(org_id, frm, to)] = value


def invalidate_report(org_id: int) -> None:
    for key in [k for k in _report_cache if k[0] == org_id]:
        _report_cache.pop(key, None)


def get_availability(room_id: int, date: str):
    return _availability_cache.get((room_id, date))


def set_availability(room_id: int, date: str, value: dict) -> None:
    _availability_cache[(room_id, date)] = value


def invalidate_availability(room_id: int, date: str) -> None:
    _availability_cache.pop((room_id, date), None)
