# mm-customer/app/swagger.py

from flask_restx import Api

def configure_swagger(app):
    """Configure the Swagger UI settings for the app."""
    app.config['RESTX_MASK_SWAGGER'] = False  # Disable default masking of Swagger fields
    app.config['SWAGGER_UI_DOC_EXPANSION'] = 'list'  # Expand all endpoints by default
    app.config['SWAGGER_UI_JSONEDITOR'] = True  # Allow editing JSON in Swagger
    app.config['RESTX_VALIDATE'] = True  # Enable input validation

    # Initialize and configure the API for Swagger UI
    api = Api(app,
              title="MM Customer API",
              version="1.0",
              description="API for customer registration with JWT authentication",
              doc="/swagger")  # Swagger UI available at /swagger

    # Optionally add namespaces here (if you use any)
    # e.g. api.add_namespace(customer_namespace)
