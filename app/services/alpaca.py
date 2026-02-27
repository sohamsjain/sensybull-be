import logging
import requests
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional
from flask import current_app

logger = logging.getLogger(__name__)


class AlpacaClient:
    """Thin wrapper around the Alpaca Market Data REST API."""

    def _headers(self) -> dict:
        return {
            'APCA-API-KEY-ID': current_app.config['ALPACA_API_KEY_ID'],
            'APCA-API-SECRET-KEY': current_app.config['ALPACA_API_SECRET_KEY'],
        }

    def _base_url(self) -> str:
        return current_app.config['ALPACA_DATA_BASE_URL']

    def get_snapshot(self, symbol: str) -> Optional[dict]:
        """GET /stocks/{symbol}/snapshot — latest trade, quote, daily bar."""
        url = f"{self._base_url()}/stocks/{symbol}/snapshot"
        try:
            resp = requests.get(url, headers=self._headers(), timeout=10)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            logger.error(f"Alpaca snapshot error for {symbol}: {e}")
            return None

    def get_snapshots(self, symbols: List[str]) -> Dict[str, dict]:
        """GET /stocks/snapshots?symbols=... — batch latest prices."""
        if not symbols:
            return {}
        url = f"{self._base_url()}/stocks/snapshots"
        params = {'symbols': ','.join(symbols)}
        try:
            resp = requests.get(url, headers=self._headers(),
                                params=params, timeout=10)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            logger.error(f"Alpaca multi-snapshot error: {e}")
            return {}

    def get_bars(
        self,
        symbol: str,
        timeframe: str = '1Day',
        start: Optional[str] = None,
        end: Optional[str] = None,
        limit: int = 1000,
    ) -> List[dict]:
        """GET /stocks/{symbol}/bars — historical OHLCV with pagination."""
        if not start:
            start = (datetime.now(timezone.utc) - timedelta(days=30)).strftime('%Y-%m-%dT00:00:00Z')
        if not end:
            end = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

        all_bars = []
        page_token = None
        url = f"{self._base_url()}/stocks/{symbol}/bars"

        while True:
            params = {
                'timeframe': timeframe,
                'start': start,
                'end': end,
                'limit': limit,
                'feed': "iex",
            }
            if page_token:
                params['page_token'] = page_token

            try:
                resp = requests.get(url, headers=self._headers(),
                                    params=params, timeout=10)
                resp.raise_for_status()
                data = resp.json()
            except requests.RequestException as e:
                logger.error(f"Alpaca bars error for {symbol}: {e}")
                break

            all_bars.extend(data.get('bars') or [])
            page_token = data.get('next_page_token')
            if not page_token:
                break

        return all_bars


alpaca_client = AlpacaClient()
