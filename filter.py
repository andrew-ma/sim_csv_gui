import sys
import csv
from io import StringIO
from sim_csv_script import check_that_field_is_valid

INDEX_COLUMN_NAME = "FieldName"


def get_csv_dict(csv_string):
    lines = csv_string.splitlines()

    reader = csv.DictReader(lines)

    csv_dict = {row[INDEX_COLUMN_NAME]: row for row in reader}

    return csv_dict


def check_csv_dict(csv_dict):
    for field_name, row_dict in csv_dict.items():
        field_value = row_dict["FieldValue"]

        check_that_field_is_valid(field_name, field_value)


def get_str_from_csv_dict(csv_dict):
    output_str = StringIO()
    fieldnames = list(next(iter(csv_dict.values())).keys())
    writer = csv.DictWriter(output_str, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(row for row in csv_dict.values())
    output_str.seek(0)
    return output_str.read()


def main():
    #############################################################
    ###########  Check Filter Script Prerequisites ##############
    assert len(sys.argv) > 1, "arg1 is required"

    arg1 = sys.argv[1]
    assert len(arg1) == 2, "arg1 must be exactly 2 digits"

    if not arg1.isdigit():
        raise ValueError("arg1 must be a valid integer")

    #############################################################

    # Read CSV from STDIN
    input_csv_string = sys.stdin.read()

    # Convert CSV string to dictionary
    csv_dict = get_csv_dict(input_csv_string)

    # Find invalid fields
    check_csv_dict(csv_dict)

    #############################################################
    #####################  Modify CSV here ######################

    # Modify SPN Value first 2 characters to be arg1
    old_value = csv_dict["SPN"]["FieldValue"]
    new_value = arg1 + old_value[2:]
    csv_dict["SPN"]["FieldValue"] = new_value

    #############################################################

    # Find invalid fields
    check_csv_dict(csv_dict)

    # Convert CSV dictionary to string
    output_csv_string = get_str_from_csv_dict(csv_dict)

    # Write modified CSV to STDOUT
    sys.stdout.write(output_csv_string)
    sys.stdout.flush()

    # Return 0 on Success
    return 0


if __name__ == "__main__":
    try:
        # exit with the return code of main() function
        sys.exit(main())
    except Exception as e:
        print(e, file=sys.stderr)
        sys.exit(1)
