#!/usr/bin/env python3
"""
Bybit 대시보드 시계열 데이터 수집기
매시간 data.json을 가져와 timeseries.csv에 저장합니다.
"""

import csv
import json
import os
import sys
from datetime import datetime, timezone, timedelta
from urllib.request import urlopen, Request
from urllib.error import URLError

DATA_URL = "https://skstmdals1-ctrl.github.io/bybit-dashboard-client1/data.json"
CSV_PATH = os.path.join(os.path.dirname(__file__), "data", "timeseries.csv")

CSV_HEADERS = [
    "timestamp_kst",         # 기록 시각 (KST)
    "equity",                # TOTAL EQUITY (USDT)
    "daily_pnl",             # 오늘 실현 PNL (USDT)
    "total_pnl",             # 누적 실현 PNL (USDT)
    "unrealized",            # 미실현 PNL (USDT)
    "cum_pnl_with_unrealized",  # 누적 PNL (미실현 포함)
    "position_count",        # 총 포지션 수
    "long_count",            # 롱 포지션 수
    "short_count",           # 숏 포지션 수
    "seed_used_pct",         # 시드 사용률 (%)
    "seed_used",             # 시드 사용 금액 (USDT)
    "mdd",                   # MDD (%)
    "current_dd",            # CURRENT DD (%)
    "source_ts",             # 원본 data.json 타임스탬프
]


def fetch_data(url: str) -> dict:
    """data.json 가져오기 (캐시 방지 헤더 포함)"""
    req = Request(
        url,
        headers={
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
            "User-Agent": "Mozilla/5.0 (timeseries-collector/1.0)",
        },
    )
    with urlopen(req, timeout=30) as resp:
        raw = resp.read().decode("utf-8")
    return json.loads(raw)


def extract_row(data: dict, timestamp_kst: str) -> dict:
    """필요한 필드만 추출해 row dict 반환"""
    total_pnl = data.get("total_pnl", 0.0)
    unrealized = data.get("unrealized", 0.0)
    long_count = data.get("long_count", 0)
    short_count = data.get("short_count", 0)

    return {
        "timestamp_kst": timestamp_kst,
        "equity": data.get("equity", ""),
        "daily_pnl": data.get("daily_pnl", ""),
        "total_pnl": total_pnl,
        "unrealized": unrealized,
        "cum_pnl_with_unrealized": total_pnl,  # total_pnl이 이미 미실현 포함 최종 누적 PNL
        "position_count": long_count + short_count,
        "long_count": long_count,
        "short_count": short_count,
        "seed_used_pct": data.get("seed_used_pct", ""),
        "seed_used": data.get("seed_used", ""),
        "mdd": data.get("mdd", ""),
        "current_dd": data.get("current_dd", ""),
        "source_ts": data.get("ts", ""),
    }


def append_to_csv(row: dict) -> bool:
    """CSV 파일에 한 행 추가. 파일 없으면 헤더 포함해서 새로 생성."""
    os.makedirs(os.path.dirname(CSV_PATH), exist_ok=True)

    file_exists = os.path.isfile(CSV_PATH)
    is_empty = file_exists and os.path.getsize(CSV_PATH) == 0

    with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
        if not file_exists or is_empty:
            writer.writeheader()
            print(f"[+] CSV 생성: {CSV_PATH}")
        writer.writerow(row)

    return True


def main():
    # KST 현재 시각
    kst = timezone(timedelta(hours=9))
    now_kst = datetime.now(kst).strftime("%Y-%m-%d %H:%M:%S")

    print(f"[{now_kst} KST] 데이터 수집 시작")
    print(f"  URL: {DATA_URL}")

    try:
        data = fetch_data(DATA_URL)
        print(f"  원본 ts: {data.get('ts', 'N/A')}")
    except URLError as e:
        print(f"[ERROR] 네트워크 오류: {e}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"[ERROR] JSON 파싱 오류: {e}", file=sys.stderr)
        sys.exit(1)

    row = extract_row(data, now_kst)
    append_to_csv(row)

    print(f"  ✅ 기록 완료:")
    print(f"     EQUITY       : {row['equity']:>12} USDT")
    print(f"     오늘 실현 PNL : {row['daily_pnl']:>12} USDT")
    print(f"     누적 PNL      : {row['total_pnl']:>12} USDT")
    print(f"     미실현 PNL    : {row['unrealized']:>12} USDT")
    print(f"     누적 PNL(최종) : {row['cum_pnl_with_unrealized']:>12} USDT")
    print(f"     포지션        : {row['position_count']}개 (롱 {row['long_count']} / 숏 {row['short_count']})")
    print(f"     시드 사용률   : {row['seed_used_pct']:>11}%")
    print(f"     MDD           : {row['mdd']:>12}%")
    print(f"     CURRENT DD    : {row['current_dd']:>12}%")


if __name__ == "__main__":
    main()
