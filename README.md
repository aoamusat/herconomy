# Project Setup

This guide will walk you through the process of setting up and running this project using `pipenv` for managing packages and dependencies.

## Prerequisites

- Python 3.10.x
- `pip` (Python package manager)
- `pipenv` (Python dependency management tool)

## Getting Started

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/aoamusat/herconomy.git
   cd herconomy
   pipenv shell
   ```

2. **Install all dependencies:**

   ```bash
   pipenv install 
   
   or
   
   pip install -r requirements.txt
   ```
3. **Run database migrations:**
   ```bash
   python manage.py migrate
   ```
4. **Run the server:**
   ```bash
   python manage.py runserver
   ```
Note: a ```.env``` file should be created under the directory where Django ```settings.py``` is located. There's a sample  ```env.example``` file for guidelines.
# API Documentation

## Create Transaction
Create a new transaction.

```
Endpoint: /api/v1/transaction/
HTTP Method: POST
Request Headers
Content-Type: application/json
Authorization: Basic Auth credentials (Base64 encoded username and password)
Request Body
The request body should contain a JSON object with the following parameters:
```


| Parameter | Description |
| ----------- | ------------ |
| amount (double, required)      | The amount of the transaction      |
| destination_account (string, required)      | The destination account number      |
| narration (string, required)      | A short description or note for the transaction      |


Example Request Body:

```json
{
    "amount": 10000,
    "destination_account": "45393353",
    "narration": "Test"
}
```

### Response
Upon successful creation of the transaction, the API will respond with a JSON object containing transaction details:

Example Response:

```json
{
    "source_account": "4512309871",
    "source_name": "Akeem Amusat",
    "destination_name": "John Doe",
    "destination_account": "45393353",
    "tx_reference": "39928765711654089835342790037423"
}
```
### Status Codes
```
201 Created: The transaction was successfully created.
400 Bad Request: If the request body is invalid or missing required parameters.
401 Unauthorized: If the provided authorization credentials are invalid.
500 Internal Server Error: If there was an error while processing the request.
```