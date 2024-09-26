```
# PUC-Rio  
**Especialização em Desenvolvimento Fullstack**  
**Disciplina: Desenvolvimento Back-end Avançado**  

Aluno: Rodrigo Alves Costa  
```

## Market Master: Customer Management Service

The `mm-customer` service is part of the Market Master project, a suite of microservices designed to manage various aspects of a supermarket e-commerce platform. This service handles customer registration, login, and management, along with JWT-based authentication.

### Related Market Master Microservices:
- [mm-inventory](https://github.com/MarketMasterPlus/mm-inventory) — Inventory (available items) Management
- [mm-product](https://github.com/MarketMasterPlus/mm-product) — Product (item registry) Management
- [mm-shopping-cart](https://github.com/MarketMasterPlus/mm-shopping-cart) — Shopping Cart Management
- [mm-address](https://github.com/MarketMasterPlus/mm-address) — Address Management with ViaCEP API integration
- [mm-store](https://github.com/MarketMasterPlus/mm-store) — Store Management
- [mm-pact-broker](https://github.com/MarketMasterPlus/mm-pact-broker) — Pact Broker for Contract tests
- [mm-ui](https://github.com/MarketMasterPlus/mm-ui) — User Interface for Market Master

---

## Quick Start

### Prerequisites
- **Docker** and **Docker Compose** are required to run this service.

### Steps to Run the Service
1. Clone the repository:  
   git clone https://github.com/MarketMasterPlus/mm-customer

2. Navigate to the project directory:  
   cd mm-customer

3. Start the services with Docker Compose:  
   docker-compose up -d

4. Access the Customer Management API at:  
   http://localhost:5701/

---

## Project Description

The `mm-customer` service is responsible for managing customer data, including creating new customer accounts, handling login via JWT tokens, and updating customer information. It also interacts with the `mm-address` service to handle address-related data.

### Key Features
- **Customer Registration**: Allows users to register by providing their personal information, including CPF (Brazilian identifier), email, and address details.
- **JWT Authentication**: Provides secure login and token-based authentication for customers.
- **Customer Information Management**: Enables updating and deleting customer records.
- **Integration with Address Service**: Communicates with the `mm-address` service to store address data based on a customer's postal code (CEP).

---

## Docker Setup

The `docker-compose.yml` file configures the `mm-customer` service and a PostgreSQL database for data storage.

### Docker Compose Configuration:

version: '3.8'

services:
  mm-customer-db:
    image: postgres:latest
    container_name: mm-customer-db
    environment:
      POSTGRES_DB: postgres
      POSTGRES_USER: marketmaster
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./db/mm-customer.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - 5433:5432
    networks:
      - marketmaster-network

  customer_service:
    build: .
    container_name: mm-customer
    ports:
      - 5701:5701
    depends_on:
      - mm-customer-db
    env_file:
      - .env
    volumes:
      - .:/app
    networks:
      - marketmaster-network

volumes:
  postgres_data:

networks:
  marketmaster-network:
    external: true

To start the service using Docker, run:

docker-compose up -d

---

## API Endpoints

### Customer Registration:
- **POST /register**  
  Allows customers to register by providing personal information such as full name, CPF, email, and address.  
  Example:  
  curl -X POST http://localhost:5701/register -d '{"fullname": "John Doe", "cpf": "12345678900", "email": "john@example.com", "password": "securepassword", "cep": "58700123", "street": "Rua A", "neighborhood": "Centro", "state": "PB", "city": "Patos"}'

### Customer Login:
- **POST /login**  
  Logs in a customer using CPF or email along with the password, returning a JWT token for authenticated sessions.  
  Example:  
  curl -X POST http://localhost:5701/login -d '{"identifier": "12345678900", "password": "securepassword"}'

### Customer Information:
- **GET /customers**  
  Retrieves a list of all customers, or searches for customers by CPF, full name, or email using a query parameter (`q`).  
  Example:  
  curl http://localhost:5701/customers?q=John

- **GET /customers/{cpf}**  
  Retrieves detailed information for a customer by their CPF.  
  Example:  
  curl http://localhost:5701/customers/12345678900

- **PUT /customers/{cpf}**  
  Updates customer information based on the CPF. Fields like full name, email, password, and address can be updated.  
  Example:  
  curl -X PUT http://localhost:5701/customers/12345678900 -d '{"fullname": "John Updated", "email": "john_updated@example.com"}'

- **DELETE /customers/{cpf}**  
  Deletes a customer record based on their CPF.  
  Example:  
  curl -X DELETE http://localhost:5701/customers/12345678900

---

## Running the Flask Application Locally

If you prefer to run the service without Docker, follow the steps below.

### Step 1: Install Dependencies

Make sure you have Python 3 and `pip` installed. Then, install the required dependencies:

pip install -r requirements.txt

### Step 2: Configure Environment Variables

Create a `.env` file in the root of the project with the following content:

FLASK_APP=app.py  
FLASK_ENV=development  
DATABASE_URL=postgresql://marketmaster:password@localhost:5433/postgres  
JWT_SECRET_KEY=your_jwt_secret

### Step 3: Run the Application

With the environment variables set, you can run the Flask application:

flask run

By default, the service will be accessible at `http://localhost:5701`.

---

## Additional Information

This microservice is part of the Market Master system, providing customer management features that are essential for user authentication and interaction. It is closely integrated with other services in the system, such as the `mm-address` service for managing customer addresses.

For more details about the Market Master project and to explore other microservices, visit the respective repositories:

- [mm-inventory](https://github.com/MarketMasterPlus/mm-inventory)
- [mm-product](https://github.com/MarketMasterPlus/mm-product)
- [mm-shopping-cart](https://github.com/MarketMasterPlus/mm-shopping-cart)
- [mm-address](https://github.com/MarketMasterPlus/mm-address)
- [mm-store](https://github.com/MarketMasterPlus/mm-store)
- [mm-pact-broker](https://github.com/MarketMasterPlus/mm-pact-broker)
- [mm-ui](https://github.com/MarketMasterPlus/mm-ui)

For any further questions, feel free to open an issue on GitHub or consult the provided documentation within each repository.
