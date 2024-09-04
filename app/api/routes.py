# mm-customer/app/api/routes.py
from flask import Blueprint, request, jsonify
from flask_restx import Api, Resource, fields, reqparse
import requests
import os
from jwt.exceptions import PyJWTError
from werkzeug.security import check_password_hash
from ..models import db, Customer
from ..schemas import CustomerSchema
from ..jwt_helper import generate_jwt

# Create the blueprint and API
blueprint = Blueprint('api', __name__)
api = Api(blueprint, title='MM Customer API', version='1.0',
          description='API for customer registration with JWT authentication')

# Swagger models
customer_model = api.model('Customer', {
    'full_name': fields.String(required=True, description='Full name of the customer'),
    'cpf': fields.String(required=True, description='CPF identifier'),
    'email': fields.String(required=True, description='Email address'),
    'password': fields.String(required=True, description='Password'),
    'cep': fields.String(required=True, description='Postal code (CEP)'),
    'street': fields.String(required=True, description='Street name'),
    'number': fields.String(description='House number'),
    'neighborhood': fields.String(required=True, description='Neighborhood'),
    'state': fields.String(required=True, description='State'),
    'city': fields.String(required=True, description='City'),
    'complement': fields.String(description='Complement')
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
        # Ensure password is provided
        if not data.get('password'):
            return {'message': 'Password is required'}, 400

        # Try generating the JWT first (if it fails, we stop the process early)
        try:
            # Generate the token early
            fake_customer = Customer(full_name=data['full_name'], cpf=data['cpf'], email=data['email'], address_id=0)
            fake_customer.password = data['password']  # Set password to test hash generation
            token = generate_jwt(1)  # Test JWT generation with a fake ID
        except PyJWTError as e:
            return jsonify({'message': 'Error generating JWT token', 'error': str(e)}), 500

        # Check if customer with CPF or email already exists
        existing_customer_by_cpf = Customer.query.filter_by(cpf=data['cpf']).first()
        existing_customer_by_email = Customer.query.filter_by(email=data['email']).first()

        if existing_customer_by_cpf:
            return {'message': 'CPF already exists'}, 409  # Return as dictionary
        if existing_customer_by_email:
            return {'message': 'Email already exists'}, 409  # Return as dictionary

        # Prepare address data to send to the address service
        address_data = {
            'cep': data.get('cep'),
            'street': data.get('street'),
            'number': data.get('number'),
            'neighborhood': data.get('neighborhood'),
            'state': data.get('state'),
            'city': data.get('city'),
            'complement': data.get('complement', '')
        }

        mm_address_url = os.getenv('MM_ADDRESS_API_URL')
        if not mm_address_url:
            return {'message': 'Address service URL not configured'}, 500

        try:
            address_response = requests.post(f'{mm_address_url}/mm-address/', json=address_data)

            # Check if the response contains JSON
            address_json = address_response.json()

            if address_response.status_code != 201:
                return {'message': 'Failed to create address',
                                'status': address_response.status_code}, address_response.status_code

            address_id = address_json.get('id')
            if not address_id:
                return {'message': 'Invalid address response from the service'}, 500

            # Create a new customer
            customer = Customer(
                full_name=data['full_name'],
                cpf=data['cpf'],
                email=data['email'],
                address_id=address_id
            )
            customer.password = data['password']
            db.session.add(customer)
            try:
                db.session.commit()
            except IntegrityError as e:
                db.session.rollback()
                # Handling duplicate CPF or email errors
                if 'customers_cpf_key' in str(e.orig):
                    return {'message': 'CPF already exists'}, 409
                elif 'customers_email_key' in str(e.orig):
                    return {'message': 'Email already exists'}, 409
                return {'message': 'Database error', 'error': str(e)}, 500

            # Generate JWT token
            try:
                token = generate_jwt(customer.id)
            except PyJWTError as e:
                return {'message': 'Error generating JWT token', 'error': str(e)}, 500

            return {'message': 'Customer registered successfully', 'token': token}, 201

        except requests.RequestException as e:
            return {'message': 'Error connecting to address service', 'error': str(e)}, 500



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

        # Check if identifier (CPF or email) and password are provided
        identifier = data.get('identifier')
        password = data.get('password')

        if not identifier or not password:
            return {'message': 'Identifier (CPF or Email) and password are required'}, 400

        # Check if the identifier is an email or CPF (basic check using "@" to differentiate)
        if '@' in identifier:
            # It's an email, look up by email
            customer = Customer.query.filter_by(email=identifier).first()
        else:
            # It's a CPF, look up by CPF
            customer = Customer.query.filter_by(cpf=identifier).first()

        if not customer:
            return {'message': 'Invalid identifier or password'}, 401

        # Verify the password
        if not check_password_hash(customer.password_hash, password):
            return {'message': 'Invalid identifier or password'}, 401

        # Generate JWT token
        try:
            token = generate_jwt(customer.id)
        except PyJWTError as e:
            return {'message': 'Error generating JWT token', 'error': str(e)}, 500

        return {'message': 'Login successful', 'token': token}, 200

# Create a parser for the 'q' query parameter
customer_query_parser = reqparse.RequestParser()
customer_query_parser.add_argument('q', type=str, location='args', help='Search by CPF, full name, or email')

@api.route('/customers')
class CustomersList(Resource):
    @api.expect(customer_query_parser)  # Add this to show query param 'q' in Swagger
    def get(self):
        # Parse the query parameters
        args = customer_query_parser.parse_args()
        search_query = args.get('q')

        query = Customer.query

        if search_query:
            # Perform case-insensitive partial matching on CPF, full name, or email
            query = query.filter(
                (Customer.cpf.ilike(f'%{search_query}%')) |
                (Customer.full_name.ilike(f'%{search_query}%')) |
                (Customer.email.ilike(f'%{search_query}%'))
            )

        # Execute the query and fetch the matching customers
        customers = query.all()

        # Serialize the results using the customer schema
        result = [customer_schema.dump(customer) for customer in customers]

        return result, 200


@api.route('/customers/<string:cpf>')  # Change to search by CPF
class CustomerDetailByCPF(Resource):
    def get(self, cpf):
        # Query the customer by CPF instead of ID
        customer = Customer.query.filter_by(cpf=cpf).first_or_404(description=f'Customer with CPF {cpf} not found')
        return jsonify({
            'full_name': customer.full_name,
            'cpf': customer.cpf,
            'email': customer.email
        })

    def delete(self, cpf):
        customer = Customer.query.filter_by(cpf=cpf).first_or_404(description=f'Customer with CPF {cpf} not found')
        db.session.delete(customer)
        db.session.commit()
        return jsonify({'message': f'Customer with CPF {cpf} deleted successfully'})

    def put(self, cpf):
        customer = Customer.query.filter_by(cpf=cpf).first_or_404(description=f'Customer with CPF {cpf} not found')
        data = request.get_json()

        customer.full_name = data.get('full_name', customer.full_name)
        customer.cpf = data.get('cpf', customer.cpf)
        customer.email = data.get('email', customer.email)

        try:
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            return jsonify({'message': 'Error updating customer', 'error': str(e)}), 500

        return jsonify({'message': f'Customer with CPF {cpf} updated successfully'})