from typing import List
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db
from app.models.base import BaseModel
from datetime import datetime, timezone


# Many-to-many relationship between User and Ticker
user_topic = sa.Table('user_topic',
                      db.metadata,
                      sa.Column('user_id', sa.String(36), sa.ForeignKey('user.id'), primary_key=True),
                      sa.Column('topic_id', sa.String(36), sa.ForeignKey('topic.id'), primary_key=True))

# Many-to-many relationship between Article and Ticker
article_topic = sa.Table('article_topic',
                      db.metadata,
                      sa.Column('article_id', sa.String(36), sa.ForeignKey('article.id'), primary_key=True),
                      sa.Column('topic_id', sa.String(36), sa.ForeignKey('topic.id'), primary_key=True))

class Topic(BaseModel):
    __tablename__ = 'topic'

    name: so.Mapped[str] = so.mapped_column(sa.String(200), nullable=False, index=True)
    last_updated: so.Mapped[datetime] = so.mapped_column(sa.DateTime(timezone=True), nullable=False,
                                                         default=datetime.now(timezone.utc))
    # Relationships
    users: so.Mapped[List["User"]] = so.relationship(back_populates='topics', secondary=user_topic)
    articles: so.Mapped[List["Article"]] = so.relationship(back_populates='topics', secondary=article_topic)

    def __repr__(self):
        return f'<Topic {self.symbol}>'