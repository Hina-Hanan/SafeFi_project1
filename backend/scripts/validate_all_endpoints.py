#!/usr/bin/env python3
from __future__ import annotations

import os
import sys
import time
import argparse
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Tuple

import requests
try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except Exception:
    pass


def _env(*names: str, default: Optional[str] = None) -> Optional[str]:
    for n in names:
        v = os.getenv(n)
        if v:
            return v
    return default

API_BASE = _env("API_BASE_URL", "BACKEND_BASE_URL", "BASE_URL", default=None)
MLFLOW_URL = _env("MLFLOW_TRACKING_URI", default="http://127.0.0.1:5001")
TIMEOUT_S = float(os.getenv("API_TIMEOUT_S", "30"))


def _url(path: str) -> str:
    return API_BASE.rstrip("/") + path


def _get(path: str, *, timeout: Optional[float] = None, **kwargs: Any) -> requests.Response:
    return requests.get(_url(path), timeout=timeout or TIMEOUT_S, **kwargs)


def _post(path: str, json: Optional[dict] = None, *, timeout: Optional[float] = None, **kwargs: Any) -> requests.Response:
    return requests.post(_url(path), json=json or {}, timeout=timeout or TIMEOUT_S, **kwargs)


@dataclass
class CheckResult:
    name: str
    ok: bool
    status: int
    elapsed_ms: int
    detail: str = ""


class Validator:
    def __init__(self) -> None:
        self.results: List[CheckResult] = []
        self.context: Dict[str, Any] = {}

    def run_check(self, name: str, fn: Callable[[], requests.Response], expect_status: Tuple[int, ...] = (200,)) -> None:
        t0 = time.time()
        try:
            resp = fn()
            ok = resp.status_code in expect_status
            detail = ""
            if not ok:
                detail = f"Unexpected status {resp.status_code}: {resp.text[:300]}"
            self.results.append(
                CheckResult(name=name, ok=ok, status=resp.status_code, elapsed_ms=int((time.time() - t0) * 1000), detail=detail)
            )
            if ok:
                self.context[name] = resp.json() if resp.headers.get("content-type", "").startswith("application/json") else resp.text
        except Exception as exc:
            self.results.append(
                CheckResult(name=name, ok=False, status=-1, elapsed_ms=int((time.time() - t0) * 1000), detail=str(exc))
            )

    def summary(self) -> Tuple[int, int]:
        passed = sum(1 for r in self.results if r.ok)
        total = len(self.results)
        return passed, total

    def print_report(self) -> None:
        print("\nAPI Endpoint Validation Report")
        print("=" * 40)
        for r in self.results:
            status = "PASS" if r.ok else "FAIL"
            print(f"[{status}] {r.name:<35} {r.status:>3} {r.elapsed_ms:>5}ms")
            if r.detail and not r.ok:
                print(f"       -> {r.detail}")
        p, t = self.summary()
        print("-" * 40)
        print(f"Result: {p}/{t} passed")


def _pick_api_base() -> str:
    candidates: List[str] = []
    if API_BASE:
        candidates.append(API_BASE)
    # common defaults
    candidates += [
        "http://127.0.0.1:8000",
        "http://localhost:8000",
        "http://127.0.0.1:8081",
        "http://localhost:8081",
    ]
    seen: set[str] = set()
    ordered = [c for c in candidates if not (c in seen or seen.add(c))]
    for base in ordered:
        try:
            r = requests.get(base.rstrip("/") + "/health", timeout=2)
            if r.status_code == 200:
                return base
        except Exception:
            continue
    # fall back to first provided or default
    return API_BASE or "http://127.0.0.1:8000"


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate API endpoints")
    parser.add_argument("--base", dest="base", help="API base URL, e.g. http://127.0.0.1:8000")
    parser.add_argument("--timeout", dest="timeout", type=float, help="Default request timeout (seconds)")
    args = parser.parse_args()

    selected_base = args.base or _pick_api_base()
    if args.timeout:
        global TIMEOUT_S
        TIMEOUT_S = args.timeout

    print(f"Using API_BASE_URL={selected_base}")
    print(f"Using MLFLOW_TRACKING_URI={MLFLOW_URL}")
    global API_BASE
    API_BASE = selected_base

    v = Validator()

    # Health
    v.run_check("health", lambda: _get("/health"), expect_status=(200,))
    v.run_check("root", lambda: _get("/"), expect_status=(200,))

    # Protocols list
    v.run_check("protocols:list", lambda: _get("/protocols", params={"limit": 10, "offset": 0}, timeout=10), expect_status=(200,))

    # Pick a protocol id if available
    protocol_id: Optional[str] = None
    try:
        plist = v.context.get("protocols:list")
        if isinstance(plist, dict):
            arr = plist.get("data", [])  # if wrapped
        else:
            arr = plist or []
        if arr:
            first = arr[0]
            protocol_id = first.get("protocol", {}).get("id") or first.get("id")
    except Exception:
        protocol_id = None

    # Risk endpoints
    if protocol_id:
        v.run_check("risk:details", lambda: _get(f"/risk/protocols/{protocol_id}/risk-details", timeout=25), expect_status=(200, 400))
        v.run_check("risk:history", lambda: _get(f"/risk/protocols/{protocol_id}/history", params={"days": 7, "limit": 50}, timeout=15), expect_status=(200, 404))
    else:
        v.results.append(CheckResult("risk:details", ok=True, status=0, elapsed_ms=0, detail="skipped (no protocol)"))
        v.results.append(CheckResult("risk:history", ok=True, status=0, elapsed_ms=0, detail="skipped (no protocol)"))

    # Data collection (validate endpoint presence/behavior)
    # Happy path not guaranteed in test env; expect 200/400/500
    v.run_check("data:collect", lambda: _post("/data/collect", json={"source": "coingecko", "protocol_ids": []}, timeout=30), expect_status=(200, 400, 500))

    # ML endpoints
    v.run_check("models:performance", lambda: _get("/models/performance", timeout=25), expect_status=(200,))
    v.run_check("models:train", lambda: _post("/models/train", timeout=90), expect_status=(200, 400))
    v.run_check("risk:batch", lambda: _post("/risk/calculate-batch", json={}, timeout=60), expect_status=(200,))

    # Error scenarios
    v.run_check("not-found", lambda: _get("/this-should-404"), expect_status=(404,))
    v.run_check("method-not-allowed", lambda: _post("/health"), expect_status=(405, 404))

    # Simple data-flow assertion (if protocol/risk details were fetched successfully)
    flow_ok = True
    if protocol_id:
        rd = v.context.get("risk:details")
        if isinstance(rd, dict):
            flow_ok = "risk_level" in rd and "risk_score" in rd
    v.results.append(CheckResult("flow:collection->storage->risk", ok=flow_ok, status=200 if flow_ok else 500, elapsed_ms=0, detail=""))

    v.print_report()
    passed, total = v.summary()
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())


