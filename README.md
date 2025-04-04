# Qubit_data_retrieval_2

- Has Frontend
- Tests on Paul's testing Mongo database
- Need to change app.py's Mongo uri to JACKs uri, as well as his database and collection for the News API
- Test coverage around 86% for testing routes from Paul's database, as well as testing for frontend (might not be necessary)
- Test Command =  pytest --cov=. test_retrieval.py test_frontend.py

![Pipeline](https://github.com/Confluencer101/Qubit_data_retrieval_2/actions/workflows/data-retrieval-ci.yml/badge.svg)

## Testing Report

To download the latest testing report PDF, go to the "Actions" tab of the
repository, click on the latest workflow run, and scroll down to Artifacts.

The testing report PDF should be contained inside the artifact file named
**data-retrieval-testing-report**. The other artifact files contain incomplete
data from various jobs in the pipeline.
