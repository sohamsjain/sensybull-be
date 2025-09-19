from marshmallow import Schema, fields, validate


class UserSchema(Schema):
    id = fields.Str(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    email = fields.Email(required=True)
    phone_number = fields.Str(validate=validate.Length(max=20))
    is_admin = fields.Bool(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    tickers = fields.List(fields.Nested('TickerSchema'), dump_only=True)


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
