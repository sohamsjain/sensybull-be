# Portfolio Tracker for US Equities — Product & Technical Plan

## Part 1: The Pain (Why Would Someone Pay $20/month?)

### The Core Problem

Retail equity investors in the US today are **fragmented across 5-10 tools** to answer basic questions about their own money:

1. **"How am I actually doing?"** — Brokerage apps show P&L per account, but most investors hold 2-3 accounts (Fidelity 401k, Schwab brokerage, Robinhood play account). Nobody shows them the unified picture.

2. **"What should I be paying attention to right now?"** — An FDA decision on a biotech they hold, an earnings date, a lockup expiry, an activist taking a position. This information exists but it's scattered across SEC filings, press releases, and news. Nobody connects it to *their specific portfolio*.

3. **"Am I concentrated in ways I don't realize?"** — An investor owns AAPL, MSFT, QQQ, and a tech-focused mutual fund in their 401k. They think they're diversified. They're 60% tech. Nobody tells them this simply.

4. **"What happened while I wasn't looking?"** — Investors don't check daily. When they come back after a week, they want a briefing: what moved, why, and does it matter?

5. **"What's the tax damage?"** — At any point in the year, investors have no idea what their realized/unrealized gains look like, or which lots to sell for tax-loss harvesting.

### Why Existing Tools Fail

| Tool | What it does well | Where it falls short |
|------|-------------------|---------------------|
| Brokerage apps | Trade execution, single-account view | No cross-account view, no intelligence layer |
| Google Finance | Quick price checks | No real portfolio tracking, no alerts |
| Yahoo Finance | News, basic portfolio | Stale UX, no AI summaries, no tax tools |
| Stock Events | Dividend tracking | Narrow scope, no portfolio-level intelligence |
| Sharesight | Tax reporting | Expensive ($25+/mo), complex, built for accountants |
| Wealthfront/Betterment | Automated investing | No control — you can't pick your own stocks |

### The Gap We Fill

**A single place that combines: unified portfolio view + personalized news intelligence + tax awareness — specifically for self-directed US equity investors.**

The $20/mo value proposition: "We save you hours per week of manual tracking and prevent costly mistakes (tax, concentration, missed events) that cost you far more than $20."

---

## Part 2: The Experience (What the User Sees)

### 2.1 Onboarding (First 5 Minutes)

**Goal**: Get the user to value within 5 minutes. No brokerage linking on day one — that's friction.

1. **Sign up** (Google OAuth — already built)
2. **"Add your holdings"** — Simple form: ticker + shares + avg cost (optional). Support CSV upload for power users.
3. **Instant dashboard** — The moment they add holdings, show:
   - Total portfolio value
   - Today's P&L ($ and %)
   - A personalized news feed for their holdings (already built via our article pipeline)
   - One insight: "You're 45% concentrated in Technology"

**Phase 2**: Offer brokerage linking via Plaid/Snaptrade for automatic sync.

---

### 2.2 Daily Experience — The Dashboard

```
┌─────────────────────────────────────────────────────────────┐
│  Portfolio Value: $127,432.18        Today: +$1,243 (+0.98%)│
│  Total Gain: +$23,412 (+22.5%)      YTD: +$8,231 (+6.9%)  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  📋 TODAY'S BRIEFING                              Feb 9, 2026│
│  ─────────────────────────────────────────────────────────  │
│  • NVDA +3.2% — New AI chip partnership announced           │
│  • JNJ: FDA advisory committee meets Thursday (you hold 50) │
│  • Tax alert: TSLA has $2,100 in unrealized losses          │
│    (wash sale window closes in 4 days)                      │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│  HOLDINGS                          Sort: Value ▼            │
│  ─────────────────────────────────────────────────────────  │
│  AAPL    100 shares   $18,432   +$4,231  (+29.8%)   14.5%  │
│  NVDA     25 shares   $15,200   +$6,100  (+67.0%)   11.9%  │
│  MSFT     40 shares   $14,800   +$2,800  (+23.3%)   11.6%  │
│  ...                                                        │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│  UPCOMING EVENTS (next 14 days)                             │
│  ─────────────────────────────────────────────────────────  │
│  Feb 11  AAPL ex-dividend ($0.25/share — you'll get $25)    │
│  Feb 13  JNJ earnings (before market open)                  │
│  Feb 18  NVDA lockup expiry (insider selling possible)      │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│  PORTFOLIO HEALTH                                           │
│  ─────────────────────────────────────────────────────────  │
│  Sector Concentration   ██████████░░ Technology 52% ⚠️      │
│  Single Stock Risk      ████████░░░░ AAPL 14.5% (ok)       │
│  Dividend Yield         2.1% ($2,674/yr estimated)          │
│  Unrealized Gains       +$23,412 (short-term: $8,200)      │
└─────────────────────────────────────────────────────────────┘
```

---

### 2.3 Key Feature Modules

#### Module 1: Portfolio Management (Core — Free tier bait)
- Manual holdings entry (ticker, shares, cost basis, date)
- Multiple portfolios / accounts (e.g., "Brokerage", "401k", "Roth IRA")
- CSV import
- Consolidated cross-account view
- Real-time valuation with live/delayed prices

#### Module 2: Personalized News & Intelligence (Core — Already partially built)
- News feed filtered to *only* stocks the user holds
- AI-generated summaries and bullet points (already built)
- Event classification: M&A, earnings, FDA, guidance, etc. (already built)
- **NEW**: Relevance scoring — rank news by portfolio impact (% of portfolio affected)
- **NEW**: "What happened" digest — weekly email/in-app summary

#### Module 3: Event Calendar (High value — key differentiator)
- Earnings dates for all held stocks
- Ex-dividend dates with projected income
- FDA decision dates (PDUFA)
- Lockup expiry dates (for recent IPOs)
- Index rebalance dates (S&P 500 additions/removals)
- SEC filing deadlines (13F, insider transactions)

#### Module 4: Portfolio Analytics (Paid tier differentiator)
- Sector/industry breakdown (pie chart)
- Geographic revenue exposure (e.g., "Your portfolio has 35% China revenue exposure")
- Correlation analysis (which of your holdings move together)
- Concentration risk scoring
- Historical performance vs benchmarks (S&P 500, QQQ)
- Dividend income projection (annual, monthly)

#### Module 5: Tax Intelligence (Paid tier — biggest $ saver)
- Realized vs unrealized gains/losses (YTD)
- Short-term vs long-term classification per lot
- Tax-loss harvesting opportunities with wash sale awareness
- "What if I sell?" tax impact calculator
- Year-end tax preview estimate
- Lot-level cost basis tracking (FIFO, LIFO, specific lot)

#### Module 6: Alerts & Notifications (Retention driver)
- Price alerts (above/below threshold)
- Earnings in X days for your holdings
- Dividend approaching (ex-date, payment date)
- Unusual volume / large price moves on holdings
- New insider buying/selling on holdings
- Weekly portfolio digest email

---

### 2.4 Pricing Tiers

| Feature | Free | Pro ($20/mo) |
|---------|------|-------------|
| Manual portfolio (1 account) | ✓ | ✓ |
| Multiple accounts | — | ✓ (unlimited) |
| Consolidated view | — | ✓ |
| Live prices | 15-min delayed | Real-time |
| News feed (your holdings) | Last 24h | Full history + search |
| AI summaries | 5/day | Unlimited |
| Event calendar | Next 7 days | Full calendar + alerts |
| Portfolio analytics | Basic (sector only) | Full suite |
| Tax tools | — | ✓ |
| Alerts | 3 price alerts | Unlimited + all types |
| Weekly digest email | — | ✓ |
| CSV export | — | ✓ |
| Brokerage sync | — | ✓ (Phase 2) |

---

## Part 3: Data Requirements (What Do We Need?)

### 3.1 Market Data

| Data | Source | Cost | Update Frequency |
|------|--------|------|------------------|
| Real-time/delayed stock prices | Polygon.io or Twelve Data | $30-80/mo (startup plans) | Real-time or 15-min |
| Historical daily prices | Polygon.io or Yahoo Finance API | Included or free | End of day |
| Company fundamentals (sector, industry, market cap) | Financial Modeling Prep (FMP) or Polygon | $15-30/mo | Daily |
| Stock splits & corporate actions | Polygon.io | Included | As they occur |

### 3.2 Event Data

| Data | Source | Cost | Update Frequency |
|------|--------|------|------------------|
| Earnings dates | FMP or Earnings Whispers scrape | $15-30/mo or free | Weekly refresh |
| Dividend data (ex-date, amount, pay date) | Polygon.io or FMP | Included | Daily |
| FDA calendar (PDUFA dates) | FDA.gov scrape + BioPharmCatalyst | Free (scrape) | Daily |
| IPO lockup expiry dates | Derived (IPO date + 180 days) | Free (calculated) | Once per IPO |
| SEC insider transactions | SEC EDGAR (Forms 3, 4, 5) | Free (public data) | Daily |
| Index rebalance dates | S&P Global press releases | Free (scrape) | Quarterly |

### 3.3 News & Intelligence Data

| Data | Source | Status |
|------|--------|--------|
| Press releases (GlobeNewswire, PR Newswire, Business Wire) | Yahoo Finance sitemap + RSS | **Already built** |
| AI classification & summarization | Groq LLM | **Already built** |
| SEC filings (8-K, 10-Q, 10-K) | SEC EDGAR RSS | Needs building |
| Insider transaction alerts | SEC EDGAR Form 4 | Needs building |

### 3.4 Tax & Cost Basis Data

| Data | Source | Notes |
|------|--------|-------|
| User's cost basis & purchase dates | User input / brokerage sync | Core to tax features |
| Federal tax brackets | IRS published rates | Update annually |
| Wash sale rules | Business logic | 30-day window rule |
| Long-term vs short-term cutoff | Business logic | 1-year holding period |

### 3.5 Reference Data

| Data | Source | Notes |
|------|--------|-------|
| US stock ticker master list | Already have (us_common_stocks.csv) | **Already built** |
| GICS sector/industry classifications | Polygon or FMP | Map each ticker |
| Company geographic revenue breakdown | FMP or manual | For exposure analysis |
| ETF holdings (for look-through analysis) | ETF provider APIs or FMP | Phase 2 |

---

## Part 4: Technical Architecture

### 4.1 New Database Models

```
Portfolio
├── id (UUID)
├── user_id (FK → User)
├── name (e.g., "Schwab Brokerage", "Fidelity 401k")
├── account_type (enum: brokerage, ira, roth_ira, 401k, other)
├── created_at

Holding
├── id (UUID)
├── portfolio_id (FK → Portfolio)
├── ticker_id (FK → Ticker)
├── status (enum: open, closed)
├── created_at

Lot (tax lot — one per purchase)
├── id (UUID)
├── holding_id (FK → Holding)
├── shares (decimal)
├── cost_per_share (decimal)
├── purchase_date (date)
├── sold_shares (decimal, default 0)
├── sold_date (date, nullable)
├── sold_price (decimal, nullable)
├── is_closed (boolean)

StockEvent
├── id (UUID)
├── ticker_id (FK → Ticker)
├── event_type (enum: earnings, dividend, fda, lockup, split, insider_tx)
├── event_date (date)
├── details (JSON — flexible payload)
├── source_url
├── created_at

Dividend
├── id (UUID)
├── ticker_id (FK → Ticker)
├── ex_date (date)
├── pay_date (date)
├── amount_per_share (decimal)
├── frequency (enum: quarterly, monthly, annual, special)

PriceSnapshot
├── id (UUID)
├── ticker_id (FK → Ticker)
├── price (decimal)
├── change_pct (decimal)
├── volume (bigint)
├── market_cap (bigint)
├── timestamp (datetime)

Alert
├── id (UUID)
├── user_id (FK → User)
├── ticker_id (FK → Ticker)
├── alert_type (enum: price_above, price_below, earnings, dividend, volume, insider)
├── threshold (decimal, nullable)
├── is_active (boolean)
├── last_triggered (datetime)

TickerFundamentals
├── ticker_id (FK → Ticker, unique)
├── sector
├── industry
├── market_cap (bigint)
├── pe_ratio (decimal)
├── dividend_yield (decimal)
├── beta (decimal)
├── revenue_geo_breakdown (JSON)
├── updated_at
```

### 4.2 New API Endpoints

```
# Portfolio Management
POST   /portfolios/                          Create a portfolio
GET    /portfolios/                          List user's portfolios
GET    /portfolios/<id>                      Get portfolio with holdings
PUT    /portfolios/<id>                      Update portfolio name/type
DELETE /portfolios/<id>                      Delete portfolio

# Holdings & Lots
POST   /portfolios/<id>/holdings/            Add a holding (with lots)
GET    /portfolios/<id>/holdings/            List holdings in portfolio
PUT    /holdings/<id>                        Update a holding
DELETE /holdings/<id>                        Remove a holding
POST   /holdings/<id>/lots/                  Add a tax lot
PUT    /lots/<id>                            Update a lot
DELETE /lots/<id>                            Remove a lot
POST   /holdings/<id>/sell                   Record a sale (specify lots)

# Portfolio Analytics
GET    /portfolios/summary                   Consolidated cross-account view
GET    /portfolios/<id>/analytics/sectors     Sector breakdown
GET    /portfolios/<id>/analytics/performance Performance vs benchmark
GET    /portfolios/<id>/analytics/dividends   Dividend income projection
GET    /portfolios/<id>/analytics/concentration  Concentration risk analysis
GET    /portfolios/analytics/tax              Tax summary (gains/losses/harvesting)

# Events
GET    /events/                              Events for user's holdings (filtered)
GET    /events/calendar                      Calendar view (date-grouped)
GET    /events/upcoming                      Next 14 days for user's holdings

# Alerts
POST   /alerts/                              Create an alert
GET    /alerts/                              List user's alerts
PUT    /alerts/<id>                           Update alert
DELETE /alerts/<id>                           Delete alert

# Import
POST   /import/csv                           Import holdings from CSV
POST   /import/sync                          Trigger brokerage sync (Phase 2)

# Prices
GET    /prices/<symbol>                      Current price + change
GET    /prices/batch?symbols=AAPL,MSFT       Batch price lookup
```

### 4.3 New Data Pipelines (Extending `stream/`)

```
stream/
├── prices/
│   ├── price_fetcher.py          Poll Polygon/Twelve Data for live quotes
│   └── main.py                   Price update loop
├── events/
│   ├── earnings_scraper.py       Fetch upcoming earnings dates
│   ├── dividend_scraper.py       Fetch dividend calendars
│   ├── fda_scraper.py            Scrape FDA PDUFA calendar
│   ├── insider_scraper.py        Parse SEC EDGAR Form 4 filings
│   └── main.py                   Event pipeline orchestrator
├── fundamentals/
│   ├── fundamentals_fetcher.py   Fetch sector, industry, ratios
│   └── main.py                   Daily fundamentals refresh
```

### 4.4 Infrastructure Needs

| Component | Current | Needed |
|-----------|---------|--------|
| Database | SQLite | PostgreSQL (for concurrent writes from pipelines + API) |
| Task queue | None | Celery + Redis (for async pipeline jobs, alert checking) |
| Cache | None | Redis (for price caching, rate limiting) |
| Email | None | SendGrid or AWS SES (for digests, alerts) |
| Hosting | Local | AWS/GCP/Railway (API + workers + DB) |
| Price websocket | None | Consider for real-time price updates to frontend |

---

## Part 5: Build Phases

### Phase 1 — MVP (Weeks 1-4): "Manual Portfolio + News"
**Goal**: Launchable product. Users can track holdings and get personalized news.

- [ ] Portfolio & Holding models + CRUD endpoints
- [ ] Lot-level cost basis tracking
- [ ] Basic P&L calculation (current price vs cost basis)
- [ ] Price fetching pipeline (delayed quotes — free tier)
- [ ] Connect existing news feed to portfolio (show only articles for held tickers)
- [ ] Sector breakdown (using fundamentals data)
- [ ] CSV import for holdings
- [ ] Migrate from SQLite to PostgreSQL

**User value**: "I can see all my holdings in one place with P&L, and I get news that matters to me."

### Phase 2 — Intelligence (Weeks 5-8): "Events + Analytics"
**Goal**: The features that justify paying.

- [ ] Earnings date scraper + calendar
- [ ] Dividend data pipeline + income projections
- [ ] Upcoming events feed (filtered to user's holdings)
- [ ] Portfolio analytics (sector, concentration, benchmark comparison)
- [ ] Historical performance charting data
- [ ] Multiple portfolio/account support
- [ ] Consolidated cross-account view

**User value**: "I never miss an earnings date or dividend, and I understand my portfolio's real composition."

### Phase 3 — Tax & Alerts (Weeks 9-12): "The $20/mo Justification"
**Goal**: Tax tools and alerts are the retention hooks.

- [ ] Realized/unrealized gains tracking
- [ ] Short-term vs long-term classification
- [ ] Tax-loss harvesting suggestions with wash sale detection
- [ ] "What if I sell?" tax calculator
- [ ] Price alerts (push/email)
- [ ] Earnings/dividend alerts
- [ ] Weekly portfolio digest email
- [ ] Insider transaction tracking (SEC EDGAR)

**User value**: "This tool just saved me $500 in taxes. The $240/year subscription pays for itself."

### Phase 4 — Automation (Weeks 13-16): "Stickiness"
**Goal**: Make it hard to leave.

- [ ] Brokerage sync via Plaid or SnapTrade (auto-import holdings)
- [ ] FDA calendar for biotech holdings
- [ ] ETF look-through (show underlying holdings of ETFs)
- [ ] Geographic revenue exposure analysis
- [ ] Correlation analysis between holdings
- [ ] Mobile-friendly API design for future app

---

## Part 6: Revenue & Unit Economics

### Cost Structure (Per Month at 1,000 Users)

| Item | Monthly Cost |
|------|-------------|
| Market data API (Polygon.io startup) | $80 |
| Groq LLM (article processing) | ~$20 |
| PostgreSQL (managed — e.g., Supabase/RDS) | $25-50 |
| Redis (managed) | $15-30 |
| Hosting (API + workers) | $50-100 |
| Email service (SendGrid) | $15 |
| **Total** | **~$200-300/mo** |

### Revenue Model

| Scenario | Users | Paid (10% conv.) | MRR |
|----------|-------|-------------------|-----|
| Launch | 1,000 | 100 | $2,000 |
| Growth | 10,000 | 1,500 | $30,000 |
| Scale | 50,000 | 10,000 | $200,000 |

At even 100 paid users, the service is cash-flow positive. Market data costs scale sub-linearly (one API call serves all users who hold the same stock).

---

## Part 7: What We Already Have (Leverage Points)

Our existing codebase gives us a head start:

| Existing Asset | Reuse For |
|----------------|-----------|
| User auth (JWT + Google OAuth) | Account system — ready |
| Ticker model + 8,700 US stocks loaded | Stock universe — ready |
| Ticker follow/unfollow | Basis for holdings (extend, don't replace) |
| Article scraping (Yahoo + RSS) | News feed — ready |
| AI classification (8 categories) | Personalized news — ready |
| AI summarization + bullet points | News intelligence — ready |
| Topic follow system | Alert preference foundation |
| Article ↔ Ticker relationships | Portfolio-filtered news — ready |
| Flask + SQLAlchemy + Alembic | Backend infrastructure — ready |
| Marshmallow schemas | API validation patterns — ready |

**Estimated reuse**: ~40% of the MVP is already built. The news intelligence layer (Module 2) is essentially done — we just need to filter it by the user's holdings instead of their followed tickers.

---

## Part 8: Key Technical Decisions to Make

1. **Price data provider**: Polygon.io (best data, $30-80/mo startup) vs Twelve Data (cheaper, $8-30/mo) vs Yahoo Finance unofficial (free, unreliable, legally gray)

2. **Real-time vs delayed prices**: Delayed (15-min) is dramatically cheaper and sufficient for a portfolio tracker (not a trading platform). Offer real-time as a pro feature later.

3. **Brokerage sync provider**: Plaid (most popular, expensive at scale) vs SnapTrade (built for this use case, simpler) vs MX (enterprise-grade). Defer to Phase 4.

4. **Database migration**: SQLite → PostgreSQL is necessary before launch. Do it in Phase 1.

5. **Frontend**: This plan is backend-only. Frontend options: React SPA, Next.js, or mobile-first with React Native. Decision needed separately.

6. **Notification delivery**: Email first (simple), push notifications later (requires mobile app or browser push).

---

## Part 9: Competitive Moat

What makes this defensible at $20/mo:

1. **AI-powered news intelligence** — Not just headlines, but classified, summarized, and ranked by portfolio relevance. Nobody else does this well for retail.

2. **Tax-lot awareness baked in from day one** — Most trackers bolt on tax features. We build with lot-level granularity from the start.

3. **Event anticipation, not just reaction** — The calendar tells you what's coming. Most tools only tell you what happened.

4. **Cross-account consolidation** — The simple act of seeing a unified view across 3 brokerages is worth the subscription for many users.

5. **Growing data advantage** — Every article we process, every event we track builds a better intelligence layer. The product gets smarter over time.
