# mm-customer/app/schemas.py

from marshmallow import Schema, fields, validate

class CustomerSchema(Schema):
    fullname = fields.Str(required=True, validate=validate.Length(min=1))
    cpf = fields.Str(required=True, validate=validate.Length(equal=11))  # Accept unformatted CPF
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=8))
    addressid = fields.Int(required=True)  # Reference to the address service

    # Include the address fields directly if not using a separate Address model
    cep = fields.Str(required=True)
    street = fields.Str(required=True)
    number = fields.Str(required=True)
    neighborhood = fields.Str(required=True)
    state = fields.Str(required=True)
    city = fields.Str(required=True)
    complement = fields.Str(required=False)
