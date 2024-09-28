# mm-customer/app/schemas.py

from marshmallow import Schema, fields, validate, EXCLUDE

class CustomerSchema(Schema):
    id = fields.Int(dump_only=True)
    fullname = fields.Str(required=True, validate=validate.Length(min=1))
    cpf = fields.Str(required=True, validate=validate.Length(equal=11))  # Accept unformatted CPF
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=8))
    addressid = fields.Str(required=True)  # Reference to the address service

    class Meta:
        unknown = EXCLUDE
