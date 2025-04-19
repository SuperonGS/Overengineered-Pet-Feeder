import requests
import sys

if len(sys.argv) != 2:
    print("Usage: python3 log_test.py <weight_in_grams>")
    sys.exit(1)

try:
    weight_grams = int(sys.argv[1])
except ValueError:
    print("Please enter a valid number for weight.")
    sys.exit(1)

r = requests.post("http://localhost:5000/log_weight", json={"weight": weight_grams})
print(f"Sent weight: {weight_grams}g -> Response: {r.json()}")

