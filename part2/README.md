# HBnB Evolution: Part 2 — Business Logic & API Layer
## Table of Contents

1. [Introduction](#introduction)
2. [Architecture & Design Patterns](#arch-design)
3. [Technical Implementation Details](#tech-details)
    * [The Business Logic Layer (Models)](#logic-models)
    * [The Persistence Layer (Repository)](#persistence-repo)
    * [The Service Layer (Facade)](#service-facade)
    * [The Presentation Layer (API)](#presentation-api)
4. [API Endpoints Reference](#api-reference)
5. [Running Tests](#running-tests)
    * [Business Logic Validation](#logic-validation)
    * [API Manual Testing using cURL](#curl-testing)
6. [Installation and Setup](#setup)
7. [Automated Unit Testing](#unit-testing)
8. [Detailed Testing Report Summary](#test-report)
9. [Authors](#authors)
-----------------------------------

## Introduction <a name="introduction"></a>
HBnB Evolution is a modular vacation rental management system. In this second phase of development, we have implemented the core Business Logic and the RESTful API. This implementation emphasizes a clean separation of concerns, ensuring that each component—from user management to place reviews—is decoupled and independently testable.

-----------------------------------

## Architecture & Design Patterns <a name="arch-design"></a>
The project follows a 3-Tier Architecture (Presentation, Business Logic, and Persistence) connected via the Facade Pattern.

## Key Patterns Used:
- Facade Pattern: The HBnBFacade acts as a single point of entry for the API, coordinating operations between the models and the repositories.
- Repository Pattern: We use an InMemoryRepository to abstract data storage. This allows the system to remain storage-agnostic; we can swap the in-memory dictionary for a database in the future without changing the logic.
- Singleton Pattern: The facade is instantiated once and shared across the application to maintain a consistent state.
- Data Transfer Objects (DTOs): We use serialize_... methods in the API layer to format model data into JSON, ensuring internal logic doesn't leak to the client.
--------------------------------------------
## Technical Implementation Details <a name="tech-details"></a>

1. The Business Logic Layer (Models) <a name="logic-models"></a>
All entities (User, Place, Review, Amenity) inherit from a BaseModel that provides:
- A unique uuid4 identifier.
- created_at and updated_at timestamps.
- An update() method for bulk attribute modification.

## Robust Validation (validators.py)
Data integrity is enforced at the model level using custom validator functions. Every time a model is created or updated, the validate() method is called to ensure:
- Users: Valid email formats and required names.
- Places: Price must be positive; Latitude (-90 to 90) and Longitude (-180 to 180) must be within geo-spatial bounds.
- Reviews: Ratings must be between 1 and 5.

2. The Persistence Layer (Repository): <a name="persistence-repo"></a>

We implemented a generic Repository Abstract Base Class (ABC) to define the interface for data operations (add, get, get_all, update, delete). The InMemoryRepository currently manages these objects in a dictionary, providing fast access for development.

3. The Service Layer (Facade): <a name="service-facade"></a>
The HBnBFacade handles the "heavy lifting" of the application

- User Management: Ensures email uniqueness before adding a user.
- Place Management: Validates that an owner_id exists and that all provided amenity_ids are valid before creating a place.
- Review Management: Automatically updates the Place model's review collection when a new review is created.

4. The Presentation Layer (API): <a name="presentation-api"></a>
Built with Flask-RESTx, the API is organized into Namespaces

- Documentation: Automatic Swagger UI generation (accessible at /).
- Error Handling: Uses api.abort() to return clear, standard HTTP error codes (400 for bad data, 404 for missing resources).
---

## API Endpoints Reference <a name="api-reference"></a>

### **Users**

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| **POST** | `/users/` | Create a new user |
| **GET** | `/users/` | List all users |
| **GET** | `/users/<id>` | Get user details |
| **PUT** | `/users/<id>` | Update user info |
---

### **Places**

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| **POST** | `/places/` | Register a new place (validates owner & amenities) |
| **GET** | `/places/` | List all places |
| **GET** | `/places/<id>` | Detailed place view (includes owner details & amenities) |
| **PUT** | `/places/<id>` | Update place information |
---

### **Amenities**

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| **POST** | `/amenities/` | Create a new amenity (e.g., WiFi, Pool) |
| **GET** | `/amenities/` | List all available amenities |
| **GET** | `/amenities/<id>` | Get specific amenity details |
| **PUT** | `/amenities/<id>` | Update an amenity name |
---

### **Reviews**

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| **POST** | `/reviews/` | Create a review for a place |
| **GET** | `/reviews/` | List all reviews |
| **GET** | `/reviews/<id>` | Get specific review details |
| **DELETE** | `/reviews/<id>` | Delete a review (updates the Place's review list) |
| **GET** | `/reviews/places/<id>/reviews` | Get all reviews for a specific place |                                           ---
---

## Running Tests <a name="running-tests"></a>

### Objective:
The primary goal of this phase is to ensure the **reliability and integrity** of the HBnB API.

This involves:
* **Verifying business logic:** Ensuring data is handled according to specified rules.
* **API Communication:** Confirming the API layer communicates accurately with the **Facade**.
* **Error Handling:** Ensuring the system gracefully handles invalid inputs.

---

## 1. Business Logic Validation <a name="logic-validation"></a>
Before exposing endpoints, we implemented **strict validation checks** within the **Model Layer** to prevent "garbage data" from entering the system.

| Entity | Attribute | Validation Rule |
| :--- | :--- | :--- |
| **User** | `first_name`, `last_name`, `email` | Must be non-empty strings. |
| | `email` | Must match a valid email regex pattern. |
| **Place** | `title` | Cannot be empty; maximum 100 characters. |
| | `price` | Must be a positive float/integer ($> 0$). |
| | `latitude` | Range: $[-90.0, 90.0]$. |
| | `longitude` | Range: $[-180.0, 180.0]$. |
| **Review** | `rating` | Must be an integer between $1$ and $5$. |
| | `text` | Required; cannot be empty. |
| **Amenity** | `name` | Maximum 50 characters; required. |

---

To run the basic model tests, execute the following command in your terminal:

```bash
python3 tests/test_models_basic.py
```
---

## API Manual Testing using cURL <a name="curl-testing"></a>
This section documents the manual testing performed on all API endpoints, covering both positive (Success) and negative (Failure) scenarios to ensure robust validation and error handling.


### 1- User Operations (/users/)
#### *Success*: Create a New User
```
curl -X POST "http://127.0.0.1:5000/users/" \
     -H "Content-Type: application/json" \
     -d '{"first_name": "Alice", "last_name": "Smith", "email": "alice@example.com", "password": "secure123"}'
```
- Expected Response: 201 Created with the full user object (id, created_at, etc.).

#### *Failure*: Duplicate Email
```
curl -X POST "http://127.0.0.1:5000/users/" \
     -H "Content-Type: application/json" \
     -d '{"first_name": "Alice", "last_name": "Smith", "email": "alice@example.com", "password": "secure123"}'
```
- Expected Response: 400 Bad Request | {"message": "Email already exists"}.

#### *Failure*: Invalid Email Format
```
curl -X POST "http://127.0.0.1:5000/users/" \
     -H "Content-Type: application/json" \
     -d '{"first_name": "Alice", "last_name": "Smith", "email": "not-an-email"}'
```
-Expected Response: 400 Bad Request | {"message": "email must be a valid email address"}.
___

### 2- Amenity Operations (/amenities/)
#### *Success*: Create an Amenity
```
curl -X POST "http://127.0.0.1:5000/amenities/" \
     -H "Content-Type: application/json" \
     -d '{"name": "Swimming Pool"}'
```
- Expected Response: 201 Created.

#### *Failure*: Empty Amenity Name
```
curl -X POST "http://127.0.0.1:5000/amenities/" \
     -H "Content-Type: application/json" \
     -d '{"name": ""}'
```
- Expected Response: 400 Bad Request | {"message": "name is required"}.
___

### 3- Place Operations (/places/)
#### *Success*: Create a Place (Linked with Owner and Amenities)
```
curl -X POST "http://127.0.0.1:5000/places/" \
     -H "Content-Type: application/json" \
     -d '{
         "title": "Luxury Villa",
         "description": "Ocean view",
         "price": 250.0,
         "latitude": 34.05,
         "longitude": -118.24,
         "owner_id": "PASTE_USER_ID_HERE",
         "amenity_ids": ["PASTE_AMENITY_ID_HERE"]
     }'
```
- Expected Response: 201 Created.

#### *Failure*: Invalid Latitude
```
curl -X POST "http://127.0.0.1:5000/places/" \
     -H "Content-Type: application/json" \
     -d '{"title": "Mars Base", "price": 100, "latitude": 150.0, "longitude": 0, "owner_id": "USER_ID"}'
```
- Expected Response: 400 Bad Request | {"message": "latitude must be between -90.0 and 90.0"}.

#### *Failure*: Non-Existent Owner
```
curl -X POST "http://127.0.0.1:5000/places/" \
     -H "Content-Type: application/json" \
     -d '{"title": "Ghost House", "price": 10, "latitude": 0, "longitude": 0, "owner_id": "fake-id"}'
```
- Expected Response: 400 Bad Request | {"message": "Owner not found"}.
___

### 4- Review Operations (/reviews/)
#### *Success*: Create a Review
```
curl -X POST "http://127.0.0.1:5000/reviews/" \
     -H "Content-Type: application/json" \
     -d '{
         "text": "Amazing experience!",
         "rating": 5,
         "user_id": "USER_ID",
         "place_id": "PLACE_ID"
     }'
```
- Expected Response: 201 Created.

#### *Failure*: Rating Out of Range (e.g., 6)
```
curl -X POST "http://127.0.0.1:5000/reviews/" \
     -H "Content-Type: application/json" \
     -d '{"text": "Bad", "rating": 6, "user_id": "USER_ID", "place_id": "PLACE_ID"}'
```
- Expected Response: 400 Bad Request | {"message": "rating must be between 1 and 5"}.

#### *Success*: Delete a Review
```
curl -X DELETE "http://127.0.0.1:5000/reviews/REVIEW_ID"
```
- Expected Response: 200 OK | {"message": "Review deleted"}.
___

### 5- Fetching Data (GET Operations)
#### API Verification Examples

| Operation | Command | Expected Result & Status Codes |
| :--- | :--- | :--- |
| **List All Entities** | `curl http://127.0.0.1:5000/users/` | **200 OK**: Success. Returns a list (even if empty). |
| **Get Entity Details** | `curl http://127.0.0.1:5000/places/<ID>` | **200 OK**: Success.<br>**404 Not Found**: The specific ID does not exist. |
| **List Place Reviews** | `curl .../places/<ID>/reviews` | **200 OK**: Success.<br>**404 Not Found**: The Place ID was not found. |
| **Malformed ID** | `curl http://127.0.0.1:5000/users/abc` | **400 Bad Request**: ID format is invalid (non-UUID). |

---
## Installation and Setup <a name="setup"></a>
1. Clone the Repository:
```
git clone <repository_url>
cd part2
```
2. Setup Virtual Environment:
```
python3 -m venv venv
source venv/bin/activate
```
3. Install Dependencies:
```
pip install -r requirements.txt
```
4. Run the Application:
```
python run.py
```

- The API will be available at [http://127.0.0.1:5000](http://127.0.0.1:5000)

---
## 4. Automated Unit Testing <a name="unit-testing"></a>
To ensure long-term stability and prevent regressions, we implemented automated tests using unittest.
- Example: Testing User Persistence:
```
import unittest
from app import create_app

class TestHBnBAPI(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()

    def test_amenity_creation(self):
        """Test that a valid amenity can be created"""
        response = self.client.post('/amenities/', json={"name": "WiFi"})
        self.assertEqual(response.status_code, 201)
        self.assertIn("WiFi", response.get_data(as_text=True))

    def test_get_nonexistent_user(self):
        """Test error handling for invalid IDs"""
        response = self.client.get('/users/invalid-uuid-123')
        self.assertEqual(response.status_code, 404)
```
---
## 5. Detailed Testing Report summary <a name="test-report"></a>

### Test Execution Summary

| Test Category | Description | Status |
| :--- | :--- | :--- |
| **Functional** | Create, Read, Update, and Delete operations for all entities. | **PASS** (200, 201, 204) |
| **Validation** | Rejection of empty strings, invalid emails, and out-of-range numbers. | **PASS** (400) |
| **Integrity** | Ensuring a Place cannot be created without a valid Owner ID. | **PASS** (400, 422) |
| **Relational** | Deleting a Review correctly removes it from the Place's review list. | **PASS** (200, 204) |
| **Error Handling** | API returns appropriate `400`, `404`, and `409` (Conflict) codes. | **PASS** (400, 404, 409) |
| **Authentication** | Access control for protected routes (e.g., creating a Place). | **PASS** (401, 403) |

## Expected Outcome:
## By following this testing workflow, the project ensures:
- Model Reliability: Data is validated at the core before storage.
- API Consistency: Endpoints adhere strictly to the REST architectural style.
- Documentation Accuracy: The Swagger UI matches the actual code implementation.
- Resilience: The application handles edge cases and user errors gracefully.
---
## Authors
* **Afnan Alfaidi** - [GitHub Profile](https://github.com/Afnan2049)
* **Lara Alzannan** - [GitHub Profile](https://github.com/laradreamer79)
---
