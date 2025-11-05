from typing import Optional, List
import sqlalchemy as sa
import sqlalchemy.orm as so
from app.models.base import BaseModel
from app.models.ticker import article_ticker
from app.models.topic import article_topic


class Article(BaseModel):
    __tablename__ = 'article'

    url: so.Mapped[str] = so.mapped_column(sa.String(512), unique=True, nullable=False)
    title: so.Mapped[str] = so.mapped_column(sa.String(512), nullable=False)
    timestamp: so.Mapped[int] = so.mapped_column(sa.BigInteger, nullable=False)
    provider: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256), nullable=True)
    provider_url: so.Mapped[Optional[str]] = so.mapped_column(sa.String(512), nullable=True)
    bullets: so.Mapped[Optional[List[str]]] = so.mapped_column(sa.JSON, nullable=True)
    summary: so.Mapped[Optional[str]] = so.mapped_column(sa.Text, nullable=True)
    image_url: so.Mapped[Optional[str]] = so.mapped_column(sa.String(512), nullable=True)
    article_text: so.Mapped[Optional[str]] = so.mapped_column(sa.Text, nullable=True)
    extracted_at: so.Mapped[Optional[str]] = so.mapped_column(sa.String(64), nullable=True)

    # Relationship with Ticker - eagerly loaded
    tickers: so.Mapped[List['Ticker']] = so.relationship(back_populates='articles', secondary=article_ticker)
    topics: so.Mapped[List['Topic']] = so.relationship(back_populates='articles', secondary=article_topic)