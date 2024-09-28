# mm-customer/app/api/routes.py
from flask import Blueprint, abort, request, jsonify
from flask_restx import Api, Resource, fields, reqparse
import requests
import os
from jwt.exceptions import PyJWTError
from werkzeug.security import check_password_hash, generate_password_hash
from ..models import db, Customer
from ..schemas import CustomerSchema
from ..jwt_helper import generate_jwt

# Create the blueprint and API
blueprint = Blueprint('api', __name__)
api = Api(blueprint, title='MM Customer API', version='1.0',
          description='API for customer registration with JWT authentication')

# Swagger models
customer_model = api.model('Customer', {
    'id': fields.Integer(readOnly=True, description='The customer unique identifier'),
    'fullname': fields.String(required=True, description='Full name of the customer'),
    'cpf': fields.String(required=True, description='CPF identifier'),
    'email': fields.String(required=True, description='Email address'),
    'password': fields.String(required=True, description='Password'),
    'addressid': fields.String(required=True, description='Address ID from the mm-address service'),
})

# Schema instance
customer_schema = CustomerSchema()

@api.route('/register')
class CustomerRegister(Resource):
    @api.expect(customer_model)
    def post(self):
        data = request.get_json()
        errors = customer_schema.validate(data)
        if errors:
            return {'message': 'Validation error', 'errors': errors}, 400
        
        if not data.get('password'):
            return {'message': 'Password is required'}, 400

        if not data.get('addressid'):
            return {'message': 'Address ID is required'}, 400

        existing_customer_by_cpf = Customer.query.filter_by(cpf=data['cpf']).first()
        existing_customer_by_email = Customer.query.filter_by(email=data['email']).first()

        if existing_customer_by_cpf:
            return {'message': 'CPF already exists'}, 409
        if existing_customer_by_email:
            return {'message': 'Email already exists'}, 409

        # Create a new customer using the provided addressid
        customer = Customer(
            fullname=data['fullname'],
            cpf=data['cpf'],
            email=data['email'],
            addressid=data['addressid']
        )
        customer.password = data['password']  # Set password using the setter
        
        db.session.add(customer)
        try:
            db.session.commit()
            token = generate_jwt(customer.id)
            return {'message': 'Customer registered successfully', 'token': token}, 201
        except IntegrityError as e:
            db.session.rollback()
            return {'message': 'Database error', 'error': str(e)}, 500

# Define the login model for Swagger
login_model = api.model('Login', {
    'identifier': fields.String(required=True, description='CPF or Email'),
    'password': fields.String(required=True, description='Password')
})

@api.route('/login')
class CustomerLogin(Resource):
    @api.expect(login_model)
    def post(self):
        data = request.get_json()
        identifier = data.get('identifier')
        password = data.get('password')

        if not identifier or not password:
            return {'message': 'Identifier (CPF or Email) and password are required'}, 400

        # Check if the identifier is an email or CPF and find the customer
        customer = Customer.query.filter(
            (Customer.email == identifier) | (Customer.cpf == identifier)
        ).first()

        if not customer:
            return {'message': 'Invalid user id or password'}, 401
        
        if not customer.check_password(password):
            return {'message': 'Invalid user id or password'}, 401

        try:
            token = generate_jwt(customer.id)
            fullname = customer.fullname
            addressid = customer.addressid
            cpf = customer.cpf
            email = customer.email
            return {'message': 'Login successful', 'token': token, 'fullname': fullname, 'cpf': cpf, 'email': email, 'addressid': addressid}, 200
        except PyJWTError as e:
            return {'message': 'Error generating JWT token', 'error': str(e)}, 500

# Create a parser for the 'q' query parameter
customer_query_parser = reqparse.RequestParser()
customer_query_parser.add_argument('q', type=str, location='args', help='Search by CPF, full name, or email')

@api.route('/customers')
class CustomersList(Resource):
    @api.expect(customer_query_parser)
    def get(self):
        args = customer_query_parser.parse_args()
        search_query = args.get('q')
        query = Customer.query

        if search_query:
            query = query.filter(
                (Customer.cpf.ilike(f'%{search_query}%')) |
                (Customer.fullname.ilike(f'%{search_query}%')) |
                (Customer.email.ilike(f'%{search_query}%'))
            )

        customers = query.all()
        result = [customer_schema.dump(customer) for customer in customers]
        return result, 200

@api.route('/customers/<string:cpf>')
class CustomerDetailByCPF(Resource):
    def get(self, cpf):
        customer = Customer.query.filter_by(cpf=cpf).first_or_404(description=f'Customer with CPF {cpf} not found')
        return jsonify({
            'fullname': customer.fullname,
            'cpf': customer.cpf,
            'email': customer.email,
            'addressid': customer.addressid
        })

    def delete(self, cpf):
        customer = Customer.query.filter_by(cpf=cpf).first_or_404(description=f'Customer with CPF {cpf} not found')
        db.session.delete(customer)
        db.session.commit()
        return jsonify({'message': f'Customer with CPF {cpf} deleted successfully'})

    @api.expect(api.model('CustomerUpdate', {
        'fullname': fields.String(description='Full name of the customer'),
        'email': fields.String(description='Email address'),
        'password': fields.String(description='Password', required=False),
        'addressid': fields.String(description='Updated address ID from the mm-address service'),
    }))
    def put(self, cpf):
        customer = Customer.query.filter_by(cpf=cpf).first_or_404(description=f'Customer with CPF {cpf} not found')
        data = request.get_json()

        customer.fullname = data.get('fullname', customer.fullname)
        customer.email = data.get('email', customer.email)
        if 'password' in data:
            customer.password = data['password']  # Use setter to hash password

        try:
            db.session.commit()
            return {'message': f'Customer with CPF {cpf} updated successfully'}, 200
        except IntegrityError as e:
            db.session.rollback()
            return {'message': 'Error updating customer', 'error': str(e)}, 500
