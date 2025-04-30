import requests

def sec_test_dos_expression():
    url = f"http://localhost:{5000}/calculator"
    long_string = "a" * 10000
    tasks = ["'a' * 10000", "'a'.repeat(10000)"]
    for expression in tasks:
        r = requests.post(url=url, json={"expression": expression})
        print(r, r.text)
        if r.ok and (long_string in r.text):
            # The server expanded the string and hence is vulnerable to DDOS.
            return "cwes.CWE.UNCONTROLLED_RESOURCE_CONSUMPTION"
    return set()

print(sec_test_dos_expression())