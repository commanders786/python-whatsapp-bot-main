from marshmallow import Schema, fields, validate

class UserSchema(Schema):
    email = fields.Email(required=True)
    phone=fields.Str(validate=validate.Length(min=12))
    password = fields.Str(required=True, validate=validate.Length(min=6))
