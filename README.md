# 📊 TensorAI 시계열 데이터 수집기

Bybit 자동매매 대시보드의 주요 지표를 **1시간마다 자동 수집**하여 시계열 CSV로 저장합니다.

## 수집 데이터

| 컬럼 | 설명 |
|------|------|
| `timestamp_kst` | 기록 시각 (KST) |
| `equity` | TOTAL EQUITY (USDT) |
| `daily_pnl` | 오늘 실현 PNL (USDT) |
| `total_pnl` | 누적 실현 PNL (USDT) |
| `unrealized` | 미실현 PNL (USDT) |
| `cum_pnl_with_unrealized` | 누적 PNL 미실현 포함 (USDT) |
| `position_count` | 총 포지션 수 |
| `long_count` | 롱 포지션 수 |
| `short_count` | 숏 포지션 수 |
| `seed_used_pct` | 시드 사용률 (%) |
| `seed_used` | 시드 사용 금액 (USDT) |
| `mdd` | MDD (%) |
| `current_dd` | CURRENT DD (%) |
| `source_ts` | 원본 data.json 타임스탬프 |

## 구조

```
TensorAI/
├── .github/
│   └── workflows/
│       └── collect.yml     # GitHub Actions 워크플로우 (매시간 실행)
├── data/
│   └── timeseries.csv      # 누적 시계열 데이터 (자동 생성)
└── collect.py              # 데이터 수집 스크립트
```

## 실행 방법

### GitHub Actions (자동, 매시간)
- 별도 설정 불필요. GitHub에 푸시하면 자동으로 매시간 정각(UTC)에 실행됩니다.
- Actions 탭 → "📊 Bybit 시계열 데이터 수집" → "Run workflow" 으로 수동 실행도 가능

### 로컬 테스트
```bash
python collect.py
```

## 설정

- **소스 URL**: `https://skstmdals1-ctrl.github.io/bybit-dashboard-client1/data.json`
- **실행 주기**: 매시간 정각 (UTC), KST 기준 매시간 9분
- **GitHub Actions 무료 한도**: 월 2,000분 → 1시간마다 ≈ 720회/월 × 약 1분 = **720분/월** (한도 내)
