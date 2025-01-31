import random
import json
import sys

def generate_name():
    first_names = ["Anna", "Erik", "Sara", "Johan", "Lena"]
    last_names = ["Andersson", "Johansson", "Karlsson", "Nilsson", "Olsson"]
    return f"{random.choice(first_names)} {random.choice(last_names)}"

def generate_email(name):
    domains = ["example.com", "test.com", "demo.org"]
    username = name.lower().replace(" ", ".")
    return f"{username}@{random.choice(domains)}"

def generate_age():
    return random.randint(18, 70)

def generate_phone():
    return f"+46{random.randint(700000000, 799999999)}"

def main():
    # Read input from stdin
    try:
        input_data = sys.stdin.read().strip().split("\n")
        choice = int(input_data[0])  # First line: choice
        num_records = int(input_data[1])  # Second line: number of records
    except (IndexError, ValueError):
        print("Invalid input. Expecting choice and number of records.")
        sys.exit(1)

    data = []

    for _ in range(num_records):
        name = generate_name()
        email = generate_email(name)
        record = {"name": name, "email": email}

        if choice >= 2:
            record["age"] = generate_age()
        if choice >= 3:
            record["phone"] = generate_phone()

        data.append(record)

    # Print data as JSON to stdout
    print(json.dumps(data, indent=4))

if __name__ == "__main__":
    main()
