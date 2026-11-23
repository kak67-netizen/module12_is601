# Module 12 User and Calculation Routes with Integration Testing

This FastAPI calculator adds user registration and login and lets users create, list, retrieve, update, and delete calculations stored in PostgreSQL. Pydantic validates requests and defines response fields. Passwords are stored as Argon2 hashes.

[Docker Hub repository](https://hub.docker.com/r/keanek98/module12_is601)  
[GitHub Actions workflow runs](https://github.com/kak67-netizen/module12_is601/actions)

## Run the Published Image

Run these commands from the repository root with Docker running. Stop any other local server using port 8000 first.

```bash
docker compose up -d db
docker compose pull web
docker compose up -d --no-build web
docker compose exec -T web python -c \
  "from app.database import engine; from app.models.calculation import Calculation; Calculation.metadata.create_all(bind=engine)"
```

The last command creates the `users` and `calculations` tables if they are missing. Open [Swagger UI](http://127.0.0.1:8000/docs) to try the API.

## Manual API Checks

In Swagger UI, expand a route, click **Try it out**, enter the parameters or JSON, and click **Execute**. Check the **Server response** section.

| Route | What to check |
|---|---|
| `POST /users/register` | Submit a new username, email, and demo password. Expect `201 Created`. Submit the same details again and expect `409 Conflict`. |
| `POST /users/login` | Use the registered username and password. Expect `200 OK`. Try an incorrect password and expect `401 Unauthorized`. |
| `POST /calculations` | Submit `{"a": 10, "b": 5, "type": "Add"}`. Expect `201 Created` and a result of `15`. Save the returned ID. |
| `GET /calculations` | Expect `200 OK` and a list containing the new calculation. |
| `GET /calculations/{calculation_id}` | Use the returned ID. Expect `200 OK` and the saved calculation. |
| `PUT /calculations/{calculation_id}` | Use the same ID and submit `{"a": 10, "b": 5, "type": "Multiply"}`. Expect `200 OK` and a result of `50`. |
| `DELETE /calculations/{calculation_id}` | Use the same ID. Expect `204 No Content`. A subsequent GET for that ID returns `404 Not Found`. |

To check validation, submit `{"a": 10, "b": 0, "type": "Divide"}` to `POST /calculations`. Expect `422` and a division-by-zero validation message.

## Run Tests Locally

From the repository root in Ubuntu WSL, create a virtual environment if you do not already have one and install the dependencies.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
docker compose up -d db
docker compose ps db
```

Once PostgreSQL is healthy, create the test database if it does not already exist.

```bash
docker compose exec db psql -U postgres -d postgres \
  -c "CREATE DATABASE fastapi_test_db;"
```

Run the unit and integration tests against the test database. The integration test setup creates and drops tables, so use `fastapi_test_db` for this command.

```bash
DATABASE_URL="postgresql://postgres:postgres@localhost:5432/fastapi_test_db" \
  python -m pytest tests/unit tests/integration -v
```

The Module 12 suite passed all 42 unit and integration tests locally.

## Continuous Integration and Deployment

The GitHub Actions workflow in `.github/workflows/ci.yml` starts PostgreSQL, runs the pytest suite and Playwright browser tests, then builds and scans the Docker image. A successful push to `main` publishes `keanek98/module12_is601:latest` to Docker Hub.