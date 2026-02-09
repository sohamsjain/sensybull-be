# Investment Thesis Tracker — Product & Technical Plan

## Part 1: The Pain

### The One Problem

Every serious self-directed investor has a thesis for every stock they own. It lives in their head, maybe in a Google Doc, maybe in scattered notes. There is no tool that:

1. **Captures** the thesis in a structured way
2. **Monitors** whether the thesis is playing out or breaking down
3. **Alerts** them when something changes that's relevant to their thesis
4. **Holds them accountable** to their own logic

This matters because the #1 reason retail investors lose money isn't picking the wrong stocks — it's **holding too long after their reason for owning has evaporated**, or **selling too early because they forgot why they bought**.

### Who Is This For?

Not day traders. Not passive index fund buyers. This is for the **thoughtful, research-driven retail investor** who:

- Reads 10-Ks and listens to earnings calls
- Has strong, specific opinions about 10-30 individual stocks
- Spends real time on research before buying
- Is frustrated that none of their tools capture the "why"
- Wants to become a better investor over time by learning from their own decisions

These people exist in large numbers. They use Seeking Alpha, read r/investing, follow fintwit. They are underserved because every tool is built around the "what" (price, P&L) and ignores the "why" (thesis, catalysts, conviction).

### Why $20/Month?

Because this tool **prevents the $500-$5,000 mistake** that happens 1-2 times per year: holding a broken thesis, missing a catalyst, or panic-selling a thesis that's intact. One saved mistake per year pays for the entire annual subscription 2-10x over.

---

## Part 2: The Experience

### 2.1 Core Concept: The Thesis Card

Every position has a **Thesis Card** — the atomic unit of the product. It's the investor's structured argument for why they own (or are watching) a stock.

```
┌─────────────────────────────────────────────────────────────┐
│  NVDA — NVIDIA Corp                          Added Mar 2025 │
│  Status: ● ACTIVE          Conviction: ████████░░ HIGH      │
│                                                             │
│  THESIS                                                     │
│  "AI infrastructure spending is in a multi-year upcycle.    │
│   NVDA has 80%+ market share in training GPUs and is        │
│   expanding into inference and networking. Revenue will      │
│   compound 30%+ annually through 2027."                     │
│                                                             │
│  CATALYSTS (what needs to happen)               Status      │
│  ├─ Data center revenue > $15B/quarter          ✅ Hit Q4'25│
│  ├─ Blackwell GPU ramp to volume production     ⏳ On track │
│  ├─ Inference market share > 50%                ⏳ Watching │
│  └─ Gross margins stay above 70%                ✅ 74% last │
│                                                             │
│  KILL CONDITIONS (what would make me sell)                   │
│  ├─ AMD gains >30% datacenter GPU share         ✅ Safe     │
│  ├─ Revenue growth drops below 20% YoY          ✅ Safe     │
│  ├─ Major customer builds competing silicon      ⚠️ Watch   │
│  │   → Dec 12: MSFT announced Maia 2 chip                  │
│  └─ Gross margins fall below 65%                ✅ Safe     │
│                                                             │
│  RECENT SIGNALS (auto-detected)                  last 7 days│
│  ├─ 🟢 "NVDA announces $3B partnership with Oracle"        │
│  │     Supports: AI infrastructure spending thesis          │
│  ├─ 🟡 "Custom AI chip startups raise $2.1B in Q4"         │
│  │     Watch: competitive threat to GPU dominance           │
│  └─ 🟢 Insider: Jensen Huang exercised options (routine)   │
│                                                             │
│  JOURNAL                                                    │
│  Feb 8 — "Earnings blew out. Raising conviction to HIGH."   │
│  Jan 15 — "MSFT Maia 2 is a risk but years away from       │
│            competing at scale. Holding."                     │
│  Nov 3 — "Bought 25 shares at $608. Thesis: AI infra."     │
│                                                             │
│  TARGET: $250 (+38%)    STOP: $120 (-34%)    P&L: +67%     │
└─────────────────────────────────────────────────────────────┘
```

This is the entire product. Everything else exists to make this card **richer, more automated, and more honest**.

---

### 2.2 The Three Screens

#### Screen 1: Thesis Dashboard (Home)

The daily view. Not a portfolio tracker — a **thesis health check**.

```
┌─────────────────────────────────────────────────────────────┐
│  MY THESES                                    7 active, 2 watch│
│                                                             │
│  NEEDS ATTENTION                                            │
│  ┌─────────────────────────────────────────────────────────┐│
│  │ ⚠️  GOOGL — Kill condition triggered                    ││
│  │ "EU antitrust ruling could force Search unbundling"     ││
│  │ You said: "Sell if regulatory action threatens >10%     ││
│  │ of Search revenue." — Review your thesis.               ││
│  └─────────────────────────────────────────────────────────┘│
│  ┌─────────────────────────────────────────────────────────┐│
│  │ 🎯 CELH — Catalyst hit                                  ││
│  │ "Q4 revenue $430M — exceeds your target of $400M"      ││
│  │ This was a key milestone in your thesis. Update?        ││
│  └─────────────────────────────────────────────────────────┘│
│                                                             │
│  ALL THESES                         Sort: Conviction ▼      │
│  Symbol   Thesis (short)                Conv.  Signals P&L  │
│  NVDA     AI infra multi-year cycle     HIGH   🟢🟢🟡  +67% │
│  AMZN     AWS + advertising flywheel    HIGH   🟢🟢    +23% │
│  CELH     Energy drink share gains      MED    🟢🎯    +15% │
│  GOOGL    Search moat + AI pivot        MED    🟢⚠️    +8%  │
│  HIMS     Telehealth disruption         MED    🟢      +42% │
│  SOFI     Neobank with lending moat     LOW    🟡🟡    -12% │
│  PLTR     Gov + commercial AI platform  LOW    🟢      +5%  │
│                                                             │
│  WATCHLIST (no position yet)                                │
│  CRWD     Cyber recovery post-outage    —      🟢🟢    —    │
│  SHOP     SMB commerce reacceleration   —      🟡      —    │
└─────────────────────────────────────────────────────────────┘
```

#### Screen 2: Thesis Detail (The Card)

Deep view of a single thesis. As shown in Section 2.1 above.

#### Screen 3: Signal Feed

A timeline of everything our system detected that relates to ANY of the user's theses. Not a generic news feed — every item is tagged to a specific thesis element.

```
┌─────────────────────────────────────────────────────────────┐
│  SIGNAL FEED                             Showing: All theses│
│                                                             │
│  TODAY                                                      │
│  🟢 NVDA — "Oracle expands NVDA GPU orders by 3x"          │
│     → Supports: "AI infrastructure spending upcycle"        │
│                                                             │
│  ⚠️  GOOGL — "EU issues preliminary ruling on Search"       │
│     → Threatens: Kill condition "regulatory action on       │
│        Search revenue"                                      │
│     → ACTION NEEDED: Review your thesis                     │
│                                                             │
│  🟡 SOFI — "Fed signals rate cuts may slow in 2026"         │
│     → Mixed: Rate environment affects lending margins       │
│                                                             │
│  🎯 CELH — "Q4 Revenue: $430M (beat est. $405M)"           │
│     → Catalyst hit: "Revenue > $400M/quarter"               │
│                                                             │
│  YESTERDAY                                                  │
│  🟢 AMZN — "AWS revenue growth accelerates to 22%"         │
│     → Supports: "AWS growth reacceleration" catalyst        │
│  ...                                                        │
└─────────────────────────────────────────────────────────────┘
```

---

### 2.3 Feature Breakdown

#### Feature 1: Thesis Authoring (Core)
- Free-text thesis statement
- Structured catalysts with target metrics (quantifiable when possible)
- Kill conditions (the conditions that would make them sell)
- Conviction level (HIGH / MEDIUM / LOW)
- Target price and stop-loss price (optional)
- Position details (shares, cost basis — lightweight, not a full portfolio tracker)
- Status: ACTIVE / WATCHING / CLOSED

#### Feature 2: Signal Detection (The AI layer — what makes it worth $20)
- Our existing news pipeline scrapes press releases and articles
- AI classifies each article against **the user's specific thesis elements**
  - Does this support a catalyst?
  - Does this threaten a kill condition?
  - Is this neutral noise?
- Earnings data matched against quantitative catalyst targets
- Insider transactions surfaced when relevant
- SEC filings (8-K) flagged when they match thesis topics
- Signals tagged: 🟢 Supports | 🟡 Mixed/Neutral | ⚠️ Threatens | 🎯 Catalyst Hit

#### Feature 3: Thesis Journal (The accountability layer)
- Timestamped notes attached to each thesis
- Automatic entries when:
  - A catalyst is marked as hit/missed
  - A kill condition is triggered
  - Conviction level is changed
  - Position is added to / trimmed / closed
- The journal becomes a personal investing diary — the thing that makes you a better investor over time
- Searchable across all theses ("show me every time I changed conviction")

#### Feature 4: Alerts & Nudges (Retention)
- Push/email when a kill condition is threatened
- Notification when a catalyst milestone is hit
- "Thesis stale" nudge — if you haven't reviewed a thesis in 30/60/90 days
- Weekly digest: "Here's what happened this week across your theses"
- Earnings reminder: "NVDA reports Thursday. Your catalyst: revenue > $15B"

#### Feature 5: Thesis History & Performance (The learning loop)
- When a position is closed, the thesis is archived (never deleted)
- Track: Was the thesis right? Did you follow your own rules?
- Over time, build a personal track record:
  - "You've closed 14 theses. 9 profitable, 5 at a loss."
  - "You held 3 positions past a triggered kill condition. All 3 lost money."
  - "Your HIGH conviction picks return +32% avg vs +8% for LOW conviction."
- This data is priceless for self-improvement and it locks users in

---

### 2.4 What This Product Is NOT

- **Not a portfolio tracker** — We don't care about total portfolio value, sector allocation, or tax lots. We track theses, not portfolios.
- **Not a stock screener** — We don't help you find stocks. You come with your own ideas.
- **Not a social platform** — Your theses are private. No sharing, no following, no influencers. (Maybe later, opt-in.)
- **Not a trading tool** — No order execution, no real-time quotes needed.

This focus is the product's strength. We do ONE thing and we do it better than anyone.

---

### 2.5 Pricing

| Feature | Free | Pro ($20/mo) |
|---------|------|--------------|
| Active theses | 3 | Unlimited |
| Thesis authoring (catalysts, kill conditions) | Full | Full |
| Manual journal entries | Full | Full |
| Signal detection (AI matching to your thesis) | — | Full |
| Kill condition alerts | — | Full |
| Catalyst hit notifications | — | Full |
| Weekly thesis digest email | — | Full |
| Thesis history & performance analytics | Last 3 closed | Full archive |
| "Thesis stale" nudges | — | Full |
| Earnings pre-match ("NVDA reports Thu...") | — | Full |
| Export thesis history | — | Full |

The free tier is generous enough to hook them. 3 theses lets them track their top 3 positions. But the moment they want signals and alerts — the thing that actually monitors their thesis for them — they pay.

---

## Part 3: The AI Signal Matching Engine (The Core Innovation)

This is what makes the product worth paying for. This is the hard part and our moat.

### How It Works

```
┌──────────────┐     ┌──────────────────┐     ┌────────────────┐
│  Data Sources │────▶│  Article/Event   │────▶│  Signal Matcher│
│              │     │  Pipeline        │     │  (LLM)         │
│ - Press rel. │     │  (already built) │     │                │
│ - Yahoo News │     │                  │     │ For each user: │
│ - SEC filings│     │  Classified &    │     │ "Does this     │
│ - Earnings   │     │  summarized      │     │  article relate│
│ - Insider tx │     │                  │     │  to any of this│
│              │     │                  │     │  user's thesis │
│              │     │                  │     │  elements?"    │
└──────────────┘     └──────────────────┘     └───────┬────────┘
                                                      │
                                              ┌───────▼────────┐
                                              │  Signal Store   │
                                              │                │
                                              │ - thesis_id    │
                                              │ - article_id   │
                                              │ - element_type │
                                              │   (catalyst/   │
                                              │    kill cond.)  │
                                              │ - element_id   │
                                              │ - sentiment    │
                                              │   (supports/   │
                                              │    threatens/   │
                                              │    mixed)       │
                                              │ - reasoning    │
                                              │ - confidence   │
                                              └───────┬────────┘
                                                      │
                                              ┌───────▼────────┐
                                              │  Alert Engine   │
                                              │                │
                                              │ High confidence│
                                              │ + threatens    │
                                              │ kill condition │
                                              │ = PUSH ALERT   │
                                              └────────────────┘
```

### Signal Matching — The LLM Prompt (Conceptual)

When an article is published about a ticker that a user has a thesis on, we run:

```
Given this article about {TICKER}:
Title: {title}
Summary: {summary}

And this investor's thesis:
Thesis: {thesis_statement}

Catalysts they're watching:
{numbered list of catalysts}

Kill conditions (reasons they'd sell):
{numbered list of kill conditions}

Determine:
1. Is this article relevant to any of the above thesis elements? (yes/no)
2. If yes, which element(s)? (by number)
3. For each matched element: does this SUPPORT, THREATEN, or is it MIXED?
4. Confidence (high/medium/low)
5. One-sentence explanation of why
```

### Scaling Strategy

The naive approach (run every article against every user's thesis) doesn't scale. Instead:

1. **First filter by ticker** — only match articles to users who have a thesis on that ticker (already have ticker ↔ article relationships)
2. **Batch by ticker** — if 500 users have an NVDA thesis, we don't run 500 LLM calls. We run the article against a **merged set of unique thesis elements** across all users, then fan out the results.
3. **Cache common patterns** — "NVDA earnings beat" is relevant to 80% of NVDA theses. Cache the match.
4. **Tiered matching** — Fast keyword pre-filter before LLM. If article mentions "revenue" and a catalyst mentions "revenue > $15B", it's a candidate. If there's no keyword overlap, skip.

Expected LLM cost at scale: ~$0.50-1.00/user/month (well within margins at $20/mo).

---

## Part 4: Data Requirements

### What We Already Have

| Data | Source | Status |
|------|--------|--------|
| Press releases (GlobeNewswire, PR Newswire, Business Wire) | Yahoo sitemap + RSS scrapers | **Built** |
| AI article classification & summarization | Groq LLM pipeline | **Built** |
| Article ↔ Ticker relationships | Ticker extraction in pipeline | **Built** |
| US stock ticker universe (8,700 stocks) | us_common_stocks.csv | **Built** |
| User auth (JWT + Google OAuth) | Flask routes | **Built** |
| Ticker follow/unfollow | Models + API | **Built** |

### What We Need to Add

| Data | Source | Cost | Priority |
|------|--------|------|----------|
| **Earnings dates + results** | Financial Modeling Prep (FMP) API | $15/mo (starter) | Phase 1 — needed for catalyst matching |
| **Basic price data** (current price, % change) | FMP or Polygon free tier | Free-$30/mo | Phase 1 — needed for P&L on thesis card |
| **SEC 8-K filings** | SEC EDGAR RSS feed | Free | Phase 2 — material events |
| **Insider transactions** | SEC EDGAR Form 4 | Free | Phase 2 — insider signal |
| **Earnings call transcripts** (stretch) | FMP or Seeking Alpha | $30-50/mo | Phase 3 — deep catalyst matching |

### What We Explicitly Do NOT Need

- Real-time price feeds (not a trading tool)
- Full historical price data (not charting)
- Sector/industry classifications (not a portfolio analyzer)
- Dividend data (not an income tracker)
- Tax lot tracking (not a tax tool)
- Brokerage integration (not a portfolio sync tool)

This simplicity is a massive advantage. Our data costs are minimal.

---

## Part 5: Technical Architecture

### 5.1 New Database Models

```
Thesis
├── id (UUID, PK)
├── user_id (FK → User)
├── ticker_id (FK → Ticker)
├── status (enum: active, watching, closed)
├── thesis_statement (text — the core argument)
├── conviction (enum: high, medium, low)
├── target_price (decimal, nullable)
├── stop_price (decimal, nullable)
├── shares (decimal, nullable — lightweight, not lot-level)
├── cost_basis (decimal, nullable — avg cost per share)
├── entered_at (date, nullable — when position was opened)
├── closed_at (datetime, nullable)
├── closed_reason (text, nullable — why they exited)
├── closed_pnl_pct (decimal, nullable — final P&L when closed)
├── created_at
├── updated_at

ThesisCatalyst
├── id (UUID, PK)
├── thesis_id (FK → Thesis)
├── description (text — "Data center revenue > $15B/quarter")
├── status (enum: pending, on_track, hit, missed, irrelevant)
├── target_metric (text, nullable — structured: "revenue > 15000000000")
├── hit_at (datetime, nullable)
├── notes (text, nullable — context when status changed)
├── sort_order (int)
├── created_at
├── updated_at

ThesisKillCondition
├── id (UUID, PK)
├── thesis_id (FK → Thesis)
├── description (text — "AMD gains >30% datacenter GPU share")
├── status (enum: safe, watching, triggered)
├── triggered_at (datetime, nullable)
├── notes (text, nullable)
├── sort_order (int)
├── created_at
├── updated_at

ThesisJournalEntry
├── id (UUID, PK)
├── thesis_id (FK → Thesis)
├── entry_type (enum: manual, catalyst_update, kill_condition_update,
│                      conviction_change, position_change, system)
├── content (text — the note)
├── metadata (JSON, nullable — e.g., {from: "medium", to: "high"} for conviction changes)
├── created_at

Signal
├── id (UUID, PK)
├── thesis_id (FK → Thesis)
├── article_id (FK → Article, nullable)
├── source_type (enum: article, earnings, insider, sec_filing, system)
├── source_id (text, nullable — external ID for non-article sources)
├── matched_element_type (enum: catalyst, kill_condition, thesis_general)
├── matched_element_id (UUID, nullable — FK to catalyst or kill condition)
├── sentiment (enum: supports, threatens, mixed)
├── reasoning (text — one-sentence LLM explanation)
├── confidence (enum: high, medium, low)
├── is_read (boolean, default false)
├── created_at

ThesisSnapshot (for tracking changes over time)
├── id (UUID, PK)
├── thesis_id (FK → Thesis)
├── field_changed (text — "conviction", "status", "target_price", etc.)
├── old_value (text)
├── new_value (text)
├── created_at
```

### 5.2 API Endpoints

```
# Thesis CRUD
POST   /theses/                         Create a thesis (with catalysts & kill conditions)
GET    /theses/                         List user's theses (filterable by status, conviction)
GET    /theses/<id>                     Get full thesis detail (with catalysts, kills, recent signals)
PUT    /theses/<id>                     Update thesis (statement, conviction, prices, position)
DELETE /theses/<id>                     Soft-delete (archive) a thesis
POST   /theses/<id>/close              Close a thesis (with reason and final P&L)
POST   /theses/<id>/reopen             Reopen a closed thesis

# Catalysts
POST   /theses/<id>/catalysts/         Add a catalyst
PUT    /catalysts/<id>                  Update catalyst (description, status)
DELETE /catalysts/<id>                  Remove a catalyst
PUT    /catalysts/<id>/status           Update catalyst status (hit/missed/on_track)

# Kill Conditions
POST   /theses/<id>/kill-conditions/   Add a kill condition
PUT    /kill-conditions/<id>           Update kill condition
DELETE /kill-conditions/<id>           Remove a kill condition
PUT    /kill-conditions/<id>/status    Update kill condition status (safe/watching/triggered)

# Journal
POST   /theses/<id>/journal/           Add a journal entry
GET    /theses/<id>/journal/           Get journal entries for a thesis
GET    /journal/                       Get all journal entries across theses (global timeline)

# Signals
GET    /signals/                       Get signal feed (all theses, paginated, filterable)
GET    /theses/<id>/signals/           Get signals for a specific thesis
PUT    /signals/<id>/read              Mark signal as read
PUT    /signals/read-all               Mark all signals as read

# Thesis Analytics (Pro)
GET    /theses/stats                   Overall thesis track record
GET    /theses/closed/performance      Performance of closed theses
GET    /theses/patterns                Patterns in your investing (conviction accuracy, etc.)

# Digest
GET    /digest/weekly                  Generate weekly thesis digest (also sent via email)
```

### 5.3 New Pipeline: Signal Matching Engine

```
stream/
├── signals/
│   ├── matcher.py              Core signal matching logic
│   │   ├── match_article_to_theses(article) → list[Signal]
│   │   ├── match_earnings_to_theses(earnings_data) → list[Signal]
│   │   └── match_insider_tx_to_theses(tx_data) → list[Signal]
│   ├── prompt_builder.py       Build LLM prompts for thesis matching
│   ├── batch_optimizer.py      Merge thesis elements per ticker for efficiency
│   ├── keyword_prefilter.py    Fast keyword match before LLM call
│   ├── alert_dispatcher.py     Send alerts for high-priority signals
│   └── main.py                 Signal matching pipeline entry point
├── earnings/
│   ├── earnings_fetcher.py     Fetch earnings dates + results from FMP
│   └── main.py
├── insider/
│   ├── insider_fetcher.py      Fetch Form 4 filings from SEC EDGAR
│   └── main.py
```

### 5.4 Modified Existing Pipeline

The existing article pipeline (`stream/article_transformer.py`) doesn't change. After an article is processed and stored, the **signal matcher** picks it up:

```
Article stored → Signal matcher queries:
  "Which users have a thesis on the tickers in this article?"
  → For each: run thesis-matching LLM call
  → Store signals
  → Dispatch alerts if kill condition threatened
```

### 5.5 Infrastructure

| Component | Current | Needed | Notes |
|-----------|---------|--------|-------|
| Database | SQLite | **PostgreSQL** | Concurrent writes from signal matcher + API |
| Task queue | None | **Celery + Redis** | Async signal matching, alert dispatch |
| Cache | None | **Redis** | Cache LLM results per ticker-article pair |
| Email | None | **SendGrid** | Weekly digest, kill condition alerts |
| LLM | Groq (article classification) | **Groq (add signal matching)** | New prompt, same infra |
| Hosting | Local | **Railway or Fly.io** | Simple deploy, low cost |

---

## Part 6: Build Phases

### Phase 1 — "Write Your Thesis" (Weeks 1-3)
The scaffolding. Users can create and manage theses manually. No AI yet.

- [ ] PostgreSQL migration
- [ ] Thesis, Catalyst, KillCondition, JournalEntry models + migrations
- [ ] Full CRUD API for theses, catalysts, kill conditions
- [ ] Journal API (manual entries + auto-entries on changes)
- [ ] ThesisSnapshot (audit trail for changes)
- [ ] Basic price fetch for thesis card (current price, P&L vs cost basis)
- [ ] Thesis list/dashboard endpoint (with status, conviction, P&L)
- [ ] Close thesis flow (archive with reason + final P&L)

**User value**: "Finally, a structured place to capture WHY I own each stock."

### Phase 2 — "We Watch For You" (Weeks 4-7)
The magic. AI signal matching turns passive notes into a living thesis.

- [ ] Signal model + API endpoints
- [ ] Signal matching engine (LLM prompt for thesis ↔ article matching)
- [ ] Keyword pre-filter (reduce LLM calls)
- [ ] Batch optimization (merge thesis elements per ticker)
- [ ] Hook signal matcher into existing article pipeline
- [ ] Signal feed endpoint (filterable by thesis, sentiment, confidence)
- [ ] Earnings data fetcher (FMP) + earnings-to-catalyst matching
- [ ] Basic signal confidence calibration

**User value**: "I woke up and my thesis tracker told me an article threatens my GOOGL kill condition. I didn't have to go looking for it."

### Phase 3 — "Never Miss, Never Forget" (Weeks 8-10)
Alerts and accountability. The retention layer.

- [ ] Alert dispatcher (email for kill condition threats, catalyst hits)
- [ ] Weekly digest email (summary of signals across all theses)
- [ ] "Thesis stale" detection + nudge (no activity in 30+ days)
- [ ] Earnings pre-match ("NVDA reports Thursday — here's what to watch")
- [ ] Insider transaction fetcher (SEC EDGAR Form 4) + signal matching
- [ ] Mark signals as read
- [ ] Notification preferences (what to alert on, frequency)

**User value**: "I got an email that my CELH catalyst was hit. I reviewed and took profits. Without this, I would have missed it."

### Phase 4 — "Learn From Yourself" (Weeks 11-13)
The flywheel. Closed thesis analytics make you a better investor.

- [ ] Thesis performance analytics (win rate, avg return by conviction)
- [ ] Pattern detection ("You hold past triggered kill conditions — they lose money")
- [ ] Thesis history browser (search closed theses)
- [ ] Conviction accuracy tracking (do HIGH conviction picks outperform?)
- [ ] Journal search across all theses
- [ ] Export thesis history (PDF/CSV)

**User value**: "My data shows my HIGH conviction picks return 3x my LOW conviction ones. I'm going to concentrate more."

---

## Part 7: What We Leverage From Existing Codebase

| Existing | Reuse For |
|----------|-----------|
| User auth (JWT + Google OAuth) | Account system — no changes needed |
| Ticker model (8,700 stocks) | Thesis ↔ Ticker linkage — no changes needed |
| Article pipeline (Yahoo + RSS) | Source data for signal matching — no changes needed |
| AI classification (Groq) | Same LLM infra, new prompt for thesis matching |
| Article ↔ Ticker relationships | "Which articles match which theses?" — first filter |
| Flask + SQLAlchemy + Alembic | Add new models, same patterns |
| Marshmallow schemas | Validation for new endpoints |
| Topic system | Could map thesis categories, but may not need it |

**The existing article pipeline is our signal source.** We don't need to change it at all. We just add a consumer that reads stored articles and matches them against user theses.

---

## Part 8: Unit Economics

### Costs (at 1,000 users, 150 paid)

| Item | Monthly Cost |
|------|-------------|
| Groq LLM — signal matching (~$0.75/paid user) | ~$115 |
| Groq LLM — article processing (already running) | ~$20 |
| FMP API (earnings data) | $15-30 |
| PostgreSQL (Supabase free tier → $25) | $0-25 |
| Redis (Upstash free tier → $10) | $0-10 |
| Hosting (Railway/Fly.io) | $20-50 |
| SendGrid (email alerts + digests) | $0-15 |
| **Total** | **~$170-265/mo** |

### Revenue

| | Users | Paid (15% conv.) | MRR | Margin |
|---|---|---|---|---|
| Launch | 1,000 | 150 | $3,000 | ~90% |
| Growth | 5,000 | 750 | $15,000 | ~94% |
| Scale | 20,000 | 3,000 | $60,000 | ~96% |

Thesis tracking has **higher conversion than generic portfolio tools** because:
1. Users who write theses are more engaged by definition
2. The free tier (3 theses, no signals) is useful but has a clear ceiling
3. The paid feature (signal matching) is obviously valuable — you can see what you're missing

---

## Part 9: Competitive Landscape

| Competitor | What they do | Why we win |
|------------|-------------|-----------|
| **Brokerage apps** | Track P&L, execute trades | Zero thesis support. They track "what", never "why." |
| **Seeking Alpha** | Other people's theses | We track YOUR thesis. Their content is noise unless matched to your logic. |
| **Stock Rover / Simply Wall St** | Fundamental screening | They help you find stocks. We help you manage your conviction AFTER you buy. |
| **Notion / Google Docs** | Free-form notes | No signal matching, no structure, no automation, no accountability. |
| **FinChat** | AI-powered fundamental data | Great for research. Not for ongoing thesis monitoring. |
| **Journalytic / TradesViz** | Trade journaling | Track entries/exits, not theses. Backward-looking, not forward-looking. |

**Nobody connects the "why I bought" to "what's happening now" using AI.** That's the gap.

---

## Part 10: Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| LLM signal matching is noisy/inaccurate | Users lose trust | Start conservative (high confidence only). Show reasoning. Let users rate signals. Improve over time. |
| Users won't bother writing theses | No engagement | Make authoring dead simple. Offer templates. AI-assisted thesis drafting ("Tell me your NVDA bull case in 2 sentences"). |
| Market is too niche | Not enough paying users | The "thoughtful retail investor" is a large, growing segment (Seeking Alpha has 300K+ premium subs). |
| LLM costs spike | Margins shrink | Batch optimization, keyword pre-filter, caching. Switch models if needed. |
| Users want full portfolio tracking | Feature requests | Resist. Stay focused. Link out to brokerage for P&L. We're the thesis layer, not the portfolio layer. |

---

## Summary: Why This Wins

1. **Radically focused** — One concept (the thesis card), not 20 features fighting for attention.
2. **AI is the product, not a gimmick** — Signal matching is genuinely hard to do manually and obviously valuable.
3. **Gets better with use** — The longer you use it, the richer your journal and the more powerful your personal analytics.
4. **Low data costs** — We don't need real-time prices, full fundamentals, or brokerage integrations.
5. **Built on what we have** — Our article pipeline is the signal source. We're not starting from zero.
6. **Clear $20/mo value** — "This tool caught a kill condition I would have missed. That save was worth $2,000."
