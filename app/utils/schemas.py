from marshmallow import Schema, fields, validate, pre_load, ValidationError
from app.models.ticker import Ticker
from app import db


class UserSchema(Schema):
    id = fields.Str(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    email = fields.Email(required=True)
    phone_number = fields.Str(validate=validate.Length(max=20))
    is_admin = fields.Bool(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    tickers = fields.List(fields.Nested('TickerSchema'), dump_only=True)
    topics = fields.List(fields.Nested('TopicSchema'), dump_only=True)


class UserRegistrationSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=6))


class UserLoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True)


class TickerSchema(Schema):
    id = fields.Str(dump_only=True)
    symbol = fields.Str(dump_only=True)
    name = fields.Str(dump_only=True)
    last_price = fields.Float(dump_only=True)
    last_updated = fields.DateTime(dump_only=True)


class TopicSchema(Schema):
    """Schema for Topic"""
    id = fields.Str(dump_only=True)
    name = fields.Str(dump_only=True)


class ArticleSchema(Schema):
    id = fields.Str(dump_only=True)
    url = fields.Str(required=True, validate=validate.Length(max=512))
    title = fields.Str(required=True, validate=validate.Length(max=512))
    timestamp = fields.Int(required=True)
    provider = fields.Str(validate=validate.Length(max=256), allow_none=True)
    provider_url = fields.Str(validate=validate.Length(max=512), allow_none=True)
    bullets = fields.List(fields.Str(), allow_none=True)  # NEW: Bullet points
    summary = fields.Str(allow_none=True)
    image_url = fields.Str(validate=validate.Length(max=512), allow_none=True)
    article_text = fields.Str(allow_none=True)
    extracted_at = fields.Str(validate=validate.Length(max=64), allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    tickers = fields.List(fields.Nested('TickerSchema'), dump_only=True)
    topics = fields.List(fields.Nested('TopicSchema'), dump_only=True)  # NEW: Topics


class ArticleCreateSchema(Schema):
    url = fields.Str(required=True, validate=validate.Length(max=512))
    title = fields.Str(required=True, validate=validate.Length(max=512))
    timestamp = fields.Int(required=True)
    provider = fields.Str(required=True, validate=validate.Length(max=256))
    provider_url = fields.Str(required=True, validate=validate.Length(max=512))
    bullets = fields.List(fields.Str(), missing=[])
    summary = fields.Str(allow_none=True)
    image_url = fields.Str(validate=validate.Length(max=512), allow_none=True)
    article_text = fields.Str(allow_none=True)
    extracted_at = fields.Str(validate=validate.Length(max=64), allow_none=True)
    tickers = fields.List(fields.Str(), missing=[])
    topics = fields.List(fields.Str(), missing=[])