# REST API for SWIFT codes

This REST API is developed in Python using [SQLModel](https://sqlmodel.tiangolo.com/) and [FastAPI](https://fastapi.tiangolo.com/), based on the [requirements](task_requirements/task_requirements.pdf).

To run the application, first change your directory to `swift-codes-app`:

```
cd swift-codes-app
```

Then, build and run the Docker container using the following commands:

```
docker build -t swift-codes-app-image .
docker run -d --name swift-codes-app-container -p 8000:8000 swift-codes-app-image
```

Once running, you can use Swagger UI at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) to interact with the database through the interface presented below.
![example of Swagger UI main page](images/swagger_ui_main_page.png)
![result of querying the API with ISO2 code PL](images/swagger_ui_query_results.png)

## Additional assumptions
I have made a few assumptions/clarifications that were not directly stated in the [requirements](task_requirements/task_requirements.pdf).

- A branch can exist without a headquarters (e.g., `ALBPPLP1BMW` in the Excel file), and a headquarters can exist without a branch (e.g., `AAISALTRXXX` in the Excel file). Consequently, deletions are not cascaded.
- The last three characters of the SWIFT code must align with the `isHeadquarter` field (for example, a bank with the SWIFT code `A1234567890` cannot be marked as a headquarters at the same time).
- New countries can be added to the database when a new bank is created.
- A country with a given ISO2 code must always have the same name in POST requests.