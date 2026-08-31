MarketSignal AI

MarketSignal AI is a full stack market research dashboard that combines live stock data, financial news processing, NLP based sentiment analysis, semantic event clustering, and historical analysis tracking into one interactive application.

The project is designed as an educational market intelligence tool. It does not provide financial advice or execute trades.

Features

Market data dashboard

Search stocks by ticker symbol

View current price, daily change, previous close, market capitalization, 52 week high, and 52 week low

Explore historical price charts across 1 day, 1 month, 6 month, and 1 year ranges

Automatically refresh saved stock quotes every 60 seconds

Watchlist

Add and remove stocks from a persistent PostgreSQL watchlist

Expand one saved stock at a time

View price history directly from the watchlist

Run a full MarketSignal analysis without searching for the stock again

News collection and article processing

Collects recent company related financial news from multiple public sources

Filters discovered articles for ticker relevance

Stores articles and ticker relationships in PostgreSQL

Prevents duplicate storage using URL and content based deduplication

Extracts article text with HTTP parsing

Uses Playwright as a fallback for pages that require browser rendering

Reuses previously scraped and analyzed data when possible

Financial sentiment analysis

MarketSignal uses FinBERT to analyze financial text.

The pipeline:

Cleans scraped article text

Splits long articles at sentence boundaries

Avoids overlapping chunks so sentences are not counted multiple times

Runs FinBERT on each chunk

Aggregates positive, neutral, and negative probabilities into one article level result

Stores article sentiment in PostgreSQL so future analyses can reuse it

Semantic event clustering

Multiple articles can describe the same real world event. Counting every article independently would overweight heavily covered stories.

MarketSignal uses sentence-transformers/all-MiniLM-L6-v2 to compare article titles and lead content and group articles that describe the same event.

The clustering logic also uses:

title semantic similarity

lead semantic similarity

a maximum event time span

conservative similarity thresholds

member level checks to reduce cluster drift

Each unique event contributes once to the company level analysis.

Example:

Article A: NVIDIA reports quarterly earnings
Article B: NVIDIA posts strong quarterly results

                ↓

        One earnings event

The individual article sentiment results are still retained and aggregated within that event.

Multi source event aggregation

If multiple independent publishers cover the same event, MarketSignal keeps the individual perspectives but does not count the event several times directionally.

Instead:

article sentiment is aggregated into one event sentiment

unique source count is retained as supporting evidence

the event contributes once to the company analysis

This prevents popular companies from receiving stronger signals simply because they receive more media coverage.

Event classification

MarketSignal uses facebook/bart-large-mnli for zero shot classification of news events.

Current categories include:

earnings

guidance

product technology

partnership deal

financing capital

competition demand

regulation legal

analyst valuation

insider activity

market movement

Low confidence classifications fall back to other rather than forcing an unreliable category.

Event category does not determine bullish or bearish direction. It is explanatory metadata used to organize the final outlook.

MarketSignal outlook

The final company analysis combines unique event sentiment with recency weighting.

The dashboard presents:

direction such as Bullish, Slightly Bullish, Neutral, Slightly Bearish, or Bearish

conviction level

news agreement

directional score

positive, neutral, and negative sentiment distribution

positive catalysts

negative risks

supporting positive signals

supporting negative signals

Fundamental events such as earnings, guidance, competition, financing, and regulation are kept separate from supporting signals such as analyst opinions, insider activity, and general market movement.

Historical analysis tracking

Each completed company analysis is stored as a historical snapshot containing:

stock price at analysis time

sentiment scores

signal

confidence

articles used

article weights

timestamp

The latest analysis can then be compared with the previous snapshot to show:

previous direction

score change

stock price change

improving, stable, or weakening sentiment trend

Historical analyses are used for comparison only. Previous predictions are not fed back into the current news score as fresh evidence.

Architecture

                         Next.js Frontend
                                │
                                │ REST API
                                ▼
                         FastAPI Backend
                                │
              ┌─────────────────┼─────────────────┐
              │                 │                 │
              ▼                 ▼                 ▼
         Market Data       News Pipeline      Watchlist
              │                 │                 │
              │                 ▼                 │
              │           Article Storage         │
              │                 │                 │
              │                 ▼                 │
              │            Text Extraction        │
              │                 │                 │
              │                 ▼                 │
              │              FinBERT              │
              │                 │                 │
              │                 ▼                 │
              │        Semantic Event Clustering  │
              │                 │                 │
              │                 ▼                 │
              │       Zero Shot Classification    │
              │                 │                 │
              │                 ▼                 │
              │        Event Level Aggregation    │
              │                 │                 │
              └─────────────────┼─────────────────┘
                                ▼
                      MarketSignal Analysis
                                │
                                ▼
                           PostgreSQL

Single pass analysis pipeline

A complete analysis is orchestrated by MarketAnalysisService.

Collect recent news
        ↓
Filter and store relevant articles
        ↓
Scrape new article content
        ↓
Run FinBERT only where sentiment is missing
        ↓
Cluster articles into unique events once
        ↓
Classify each event once
        ↓
Build company sentiment from the shared event results
        ↓
Build catalysts, risks, and supporting signals
        ↓
Build direction, conviction, and news agreement
        ↓
Store historical analysis snapshot
        ↓
Compare with previous analysis
        ↓
Return one API response to the frontend

The heavy NLP models are cached in a shared model registry so MiniLM and BART are loaded once per backend process and reused across analyses.

Tech stack

Frontend

TypeScript

React

Next.js

Tailwind CSS

Recharts

Backend

Python

FastAPI

SQLAlchemy

Pydantic

HTTPX

BeautifulSoup4

Playwright

AI and NLP

PyTorch

Hugging Face Transformers

FinBERT

Sentence Transformers

sentence-transformers/all-MiniLM-L6-v2

facebook/bart-large-mnli

Data and infrastructure

PostgreSQL

Docker

Docker Compose

Git

GitHub

Database

Main tables include:

watchlist

Stores saved ticker symbols.

news_articles

Stores article metadata and extracted content.

article_tickers

Many to many relationship between articles and ticker symbols.

article_sentiments

Stores cached FinBERT results for each successfully analyzed article.

company_analyses

Stores historical company level analysis snapshots.

analysis_articles

Stores the articles and normalized weights used by each historical analysis.

API endpoints

Health

GET /health

Stocks

GET /stocks/{symbol}
GET /stocks/{symbol}/history?period=1mo

Supported chart periods include 1d, 1mo, 6mo, and 1y.

Watchlist

GET /watchlist
POST /watchlist/{symbol}
DELETE /watchlist/{symbol}

Market analysis

POST /analysis/{symbol}
GET /analysis/{symbol}/latest

POST /analysis/{symbol} runs the complete MarketSignal pipeline and stores a new historical snapshot.

GET /analysis/{symbol}/latest retrieves the most recently stored snapshot without rerunning the AI pipeline.

Local setup

Prerequisites

Install:

Python 3

Node.js and npm

Docker Desktop

Git

1. Clone the repository

git clone https://github.com/aaditsingla/MarketSignalAI.git
cd MarketSignalAI

2. Configure PostgreSQL

Create a root .env file using your own local credentials:

POSTGRES_DB=marketsignal
POSTGRES_USER=marketsignal_user
POSTGRES_PASSWORD=your_local_password

Do not commit the .env file.

3. Start PostgreSQL

docker compose up -d

Check the container:

docker compose ps

4. Configure the backend

cd backend
python -m venv .venv

On Windows PowerShell:

.\.venv\Scripts\Activate.ps1

Install dependencies:

python -m pip install -r requirements.txt

Install the Playwright browser:

python -m playwright install chromium

Create database tables:

python -c "from app.database.init_db import create_tables; create_tables(); print('Database tables created successfully')"

Start FastAPI:

python -m uvicorn app.main:app

Backend:

http://127.0.0.1:8000

Interactive API documentation:

http://127.0.0.1:8000/docs

5. Start the frontend

Open another terminal:

cd frontend
npm install
npm run dev

Frontend:

http://localhost:3000

Typical workflow

Start Docker

Start PostgreSQL with Docker Compose

Start FastAPI

Start Next.js

Search for a ticker or expand a saved watchlist stock

View live quote information and price history

Click Run Market Analysis

Review the generated MarketSignal outlook

Run another analysis later to compare changes over time

Key engineering decisions

Why PostgreSQL?

The project stores relational data with clear relationships between stocks, articles, ticker mappings, sentiment results, analyses, and analysis inputs. PostgreSQL provides strong relational integrity and supports historical growth better than storing everything in local files.

Why cache article sentiment?

FinBERT inference is more expensive than reading a row from PostgreSQL. Once an article has been analyzed, MarketSignal reuses the stored result instead of repeatedly processing identical text.

Why use event level aggregation?

Article level aggregation can double count the same event when many publishers cover it. Event clustering reduces this bias and makes the company signal depend on unique developments instead of raw article volume.

Why separate event category from direction?

BART determines what type of event occurred. FinBERT determines the financial sentiment of the text. Keeping these responsibilities separate prevents a category such as earnings from automatically being treated as positive or negative.

Why recency weighting?

Recent events generally provide more relevant context for a current news outlook. MarketSignal therefore applies exponential recency weighting when aggregating unique events.

Why keep previous analyses separate from current evidence?

Historical results are useful for tracking whether sentiment is improving or weakening, but feeding old predictions back into the current score would mix historical evaluation with current evidence. MarketSignal stores and compares snapshots after the current analysis has already been calculated.

Current limitations

MarketSignal is a portfolio research project and not production trading infrastructure.

Current limitations include:

Semantic event clustering uses tuned similarity thresholds and can occasionally miss or incorrectly group ambiguous stories.

Zero shot event classification is not a finance specific supervised classifier.

Bullish, bearish, conviction, agreement, and trend labels use interpretable presentation thresholds rather than learned trading thresholds.

News availability and scraping quality depend on the public sources being accessed.

Some dynamically rendered or protected articles may not provide usable full text.

Analysis quality depends on the amount and quality of recent news available for a company.

The application analyzes news sentiment and events. It does not predict future stock prices.

The frontend currently uses a local backend URL and would need environment based API configuration for deployment.

Future improvements

Possible future extensions include:

configurable analysis lookback windows

broader news source coverage

finance specific supervised event classification

stronger source independence detection for syndicated articles

background analysis jobs

portfolio level analysis

model serving optimizations for cloud deployment

deeper evaluation of historical MarketSignal results against future price movement

These are intentionally left as future improvements so the current project remains focused, explainable, and practical.