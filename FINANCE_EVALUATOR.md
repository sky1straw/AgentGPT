# Finance Evaluator

This repository includes a standalone Python script `finance_evaluator.py` that provides a simple graphical interface for evaluating financial projects.

## Usage

1. Ensure Python 3 is installed on your system.
2. Install the MySQL connector package:

```bash
pip install mysql-connector-python
```

3. Make sure a MySQL server is running locally. You can set the `MYSQL_USER`,
   `MYSQL_PASSWORD`, and `MYSQL_DB` environment variables to control the
   connection. The database will be created automatically if it does not exist.

4. Run the script:

```bash
python3 finance_evaluator.py
```

5. Use the GUI to create projects, record inflows and outflows (with
   source/destination, date, and amount), and generate a report showing each
   project's total inflow, total outflow, net return, and ROI.
