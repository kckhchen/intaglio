# Contributing

This project is actively maintained and frequently updated. If you'd like to contribute, you can submit issues or fork this repository.

## Running From Source

Use this if you want to modify the tool or run the test suite:

```bash
git clone https://github.com/kckhchen/intaglio.git
cd intaglio
python3 -m venv .venv
source .venv/bin/activate
# or .venv\Scripts\activate.bat for Windows
pip install -e .
```

## Testing

This project uses `pytest` for testing. The tests are in the `tests` folder. To run the tests locally, follow these steps:

1. Install Dependencies

```bash
pip install -r requirements-dev.txt
```

1. Run the Test Suite
   To run all tests:

```bash
pytest
# or pytest --spec for spec reviews
```

To run a specific test file:

```bash
pytest tests/test_process_images.py
```
