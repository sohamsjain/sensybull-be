from typing import List
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db
from app.models.base import BaseModel
from datetime import datetime, timezone


# Many-to-many relationship between User and Ticker
user_ticker = sa.Table('user_ticker',
                      db.metadata,
                      sa.Column('user_id', sa.String(36), sa.ForeignKey('user.id'), primary_key=True),
                      sa.Column('ticker_id', sa.String(36), sa.ForeignKey('ticker.id'), primary_key=True))

# Many-to-many relationship between Article and Ticker
article_ticker = sa.Table('article_ticker',
                      db.metadata,
                      sa.Column('article_id', sa.String(36), sa.ForeignKey('article.id'), primary_key=True),
                      sa.Column('ticker_id', sa.String(36), sa.ForeignKey('ticker.id'), primary_key=True))

class Ticker(BaseModel):
    __tablename__ = 'ticker'

    symbol: so.Mapped[str] = so.mapped_column(sa.String(20), nullable=False, index=True, unique=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(200), nullable=False, index=True)
    last_price: so.Mapped[float] = so.mapped_column(sa.Float, default=0.0, nullable=False)
    last_updated: so.Mapped[datetime] = so.mapped_column(sa.DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc))

    # Relationships
    users: so.Mapped[List["User"]] = so.relationship(back_populates='tickers', secondary=user_ticker)
    articles: so.Mapped[List["Article"]] = so.relationship(back_populates='tickers', secondary=article_ticker)

    def __repr__(self):
        return f'<Ticker {self.symbol}>'

