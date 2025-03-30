# Generates a PDF report for use in the GitHub CI/CD pipeline

import fpdf
import datetime

# Set constants and variables
PDF_TITLE = "Qubit Data Retrieval: Testing report"
TEST_FRAMEWORK = "pytest"
current_time = datetime.datetime.now().ctime()

unit_tests_pass = True
linting_pass = True
type_checking_pass = True


# Function which converts a boolean value (true / false) into a string
# (PASSING or FAILING)
def pass_or_fail(boolean: bool):
    if boolean:
        return "PASSING"
    else:
        return "FAILING"


# Set up PDF
pdf = fpdf.FPDF()
pdf.set_title(f"{PDF_TITLE} - {current_time}")
pdf.add_page()

# PDF title and time of creation
pdf.set_font("helvetica", size=25, style="BU")
pdf.cell(text=f"{PDF_TITLE}", center=True, new_x="LMARGIN", new_y="NEXT")
pdf.set_font("helvetica", size=12, style="I")
pdf.cell(text=f"{current_time}", center=True, new_x="LMARGIN", new_y="NEXT")

# Create some empty space
pdf.set_font("helvetica", size=12)
pdf.cell(text=" ", new_x="LMARGIN", new_y="NEXT")
pdf.cell(text=" ", new_x="LMARGIN", new_y="NEXT")
pdf.cell(text=" ", new_x="LMARGIN", new_y="NEXT")

# Add section for unit tests and coverage
pdf.set_font("helvetica", size=15, style="B")
pdf.cell(text="Unit Tests", new_x="LMARGIN", new_y="NEXT")
pdf.set_font("helvetica", size=12)
pdf.cell(
    text=f"Our functions and routes have been tested with the {TEST_FRAMEWORK} test framework. Here are the results:", new_x="LMARGIN", new_y="NEXT")
pdf.cell(text=" ", new_x="LMARGIN", new_y="NEXT")

pdf.set_font("courier", size=12)
try:
    with open("test_results.txt", "r") as test_results:
        lines = test_results.readlines()

        for line in lines:
            pdf.multi_cell(w=0, text=f"{line}", new_x="LMARGIN", new_y="NEXT")

            if "fail" in line.lower():
                unit_tests_pass = False
except FileNotFoundError:
    pdf.cell(text="ERROR: Unit test results could not be found",
             new_x="LMARGIN", new_y="NEXT")

    unit_tests_pass = False

pdf.set_font("helvetica", size=12)
pdf.cell(text=" ", new_x="LMARGIN", new_y="NEXT")
pdf.cell(text="Our unit tests currently have the following coverage:",
         new_x="LMARGIN", new_y="NEXT")
pdf.cell(text=" ", new_x="LMARGIN", new_y="NEXT")

pdf.set_font("courier", size=12)
try:
    with open("coverage.txt", "r") as coverage_report:
        lines = coverage_report.readlines()

        for line in lines:
            pdf.multi_cell(w=0, text=f"{line}", new_x="LMARGIN", new_y="NEXT")
except FileNotFoundError:
    pdf.cell(text="ERROR: Coverage report could not be found",
             new_x="LMARGIN", new_y="NEXT")

# Add section for linting
pdf.set_font("helvetica", size=15, style="B")
pdf.cell(text=" ", new_x="LMARGIN", new_y="NEXT")
pdf.cell(text="Linting", new_x="LMARGIN", new_y="NEXT")
pdf.set_font("helvetica", size=12)
pdf.cell(text="Our code has been linted with flake8 to ensure conformity to PEP-8 guidelines.",
         new_x="LMARGIN", new_y="NEXT")

try:
    with open("linting.txt", "r") as linting:
        lines = linting.readlines()

        if len(lines) == 2 and lines[0].rstrip('\n') == "0" and lines[1].rstrip('\n') == "0":
            pdf.cell(text="The linting checks have passed, so our code is fully PEP-8 compliant.",
                     new_x="LMARGIN", new_y="NEXT")
        else:
            pdf.cell(text="The linting checks have failed, with the following errors:",
                     new_x="LMARGIN", new_y="NEXT")
            pdf.cell(text=" ", new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("courier", size=12)

            for line in lines:
                pdf.multi_cell(w=0, text=f"{line}",
                               new_x="LMARGIN", new_y="NEXT")

            linting_pass = False
except FileNotFoundError:
    pdf.cell(text="The linting checks have failed, with the following errors:",
             new_x="LMARGIN", new_y="NEXT")
    pdf.cell(text=" ", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("courier", size=12)
    pdf.cell(text="ERROR: Linting results could not be found",
             new_x="LMARGIN", new_y="NEXT")

    linting_pass = False

# Add section for type checking
pdf.set_font("helvetica", size=15, style="B")
pdf.cell(text=" ", new_x="LMARGIN", new_y="NEXT")
pdf.cell(text="Type Checking", new_x="LMARGIN", new_y="NEXT")
pdf.set_font("helvetica", size=12)
pdf.cell(text="Since Python is dynamically typed, we used mypy to ensure type safety.",
         new_x="LMARGIN", new_y="NEXT")
pdf.cell(text="Here are the results of our type checking:",
         new_x="LMARGIN", new_y="NEXT")
pdf.cell(text=" ", new_x="LMARGIN", new_y="NEXT")

pdf.set_font("courier", size=12)
try:
    with open("type_checking.txt", "r") as type_checking:
        lines = type_checking.readlines()

        if not lines[0].startswith("Success"):
            type_checking_pass = False

        for line in lines:
            pdf.multi_cell(w=0, text=f"{line}", new_x="LMARGIN", new_y="NEXT")
except FileNotFoundError:
    pdf.cell(text="ERROR: Type checking results could not be found",
             new_x="LMARGIN", new_y="NEXT")

    type_checking_pass = False

# Add section for overall results
# Add section for type checking
pdf.set_font("helvetica", size=15, style="B")
pdf.cell(text=" ", new_x="LMARGIN", new_y="NEXT")
pdf.cell(text="Overall Results", new_x="LMARGIN", new_y="NEXT")
pdf.set_font("helvetica", size=12)

overall_pass = unit_tests_pass and linting_pass and type_checking_pass

pdf.cell(
    text=f"Overall our tests are {pass_or_fail(overall_pass)}.", new_x="LMARGIN", new_y="NEXT")
pdf.cell(text="The final results for each type of testing are as follows:",
         new_x="LMARGIN", new_y="NEXT")
pdf.cell(text=" ", new_x="LMARGIN", new_y="NEXT")
pdf.cell(text=f"Unit Tests: {pass_or_fail(unit_tests_pass)}",
         new_x="LMARGIN", new_y="NEXT")
pdf.cell(text=f"Linting: {pass_or_fail(linting_pass)}",
         new_x="LMARGIN", new_y="NEXT")
pdf.cell(
    text=f"Type Checking: {pass_or_fail(type_checking_pass)}", new_x="LMARGIN", new_y="NEXT")

# Generate the PDF using the provided information
pdf.output("testing_report.pdf")
