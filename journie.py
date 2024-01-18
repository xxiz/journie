from selenium import webdriver
from selenium.webdriver.common.by import By
import random
from os import path
from string import ascii_letters #, digits, punctuation
from json import load
from names import get_first_name, get_last_name

PASSWORD = "password123"
VALID_EMAILS = ["john@gmail.com", "smith@gmail.com"]
GENERATED_EMAILS_FILE = "generated_emails"
PROVINCE = "BC"
REGISTERED_EMAILS_FILE = "registered_emails"
POSTAL_CODES_FILE = "postal_codes.json"

if not path.exists(GENERATED_EMAILS_FILE):
    with open(GENERATED_EMAILS_FILE, "w") as f:
        f.write("")
        f.close()

if not path.exists(REGISTERED_EMAILS_FILE):
    with open(REGISTERED_EMAILS_FILE, "w") as f:
        f.write("")
        f.close()

# def generate_password():
#     import random, string

#     length = random.randint(8, 16)
#     password = "".join(
#         random.choice(string.ascii_letters + string.digits + string.punctuation)
#         for _ in range(length)
#     )
#     return password


def generate_postal_suffix():
    return f"{random.randint(0, 9)}{random.choice(ascii_letters)}{random.randint(0, 9)}"


def generate_email_variations(email):
    local, domain = email.split("@")
    local_variations = set([local])  # Include the original local part

    # Generate variations by adding periods at random positions
    for _ in range(500):  # Number of variations to attempt
        chars = list(local)
        for i in range(1, len(chars)):  # Start from 1 to avoid leading period
            if chars[i - 1] != "." and random.choice([True, False]):
                chars.insert(i, ".")
                i += 1  # Skip the next character to avoid consecutive periods
        new_local = "".join(chars).rstrip(".")  # Ensure no trailing period
        local_variations.add(new_local)

    return [f"{lv}@{domain}" for lv in local_variations]


def generate_email():
    try:
        with open(GENERATED_EMAILS_FILE, "r") as f:
            generated_emails = set(line.strip() for line in f)

        for email in VALID_EMAILS:
            email_variations = generate_email_variations(email)

            for new_email in email_variations:
                if new_email not in generated_emails:
                    with open(GENERATED_EMAILS_FILE, "a") as f:
                        f.write(new_email + "\n")
                    return new_email

        raise Exception("No more emails to generate")

    except IOError as e:
        print(f"An error occurred: {e}")
        return None


def generate_postal_code():
    with open(POSTAL_CODES_FILE, "r") as file:
        postal_codes = load(file)["data"]
    filtered_codes = [
        item["name"] for item in postal_codes if PROVINCE in item["detail"]
    ]
    return random.choice(filtered_codes) + generate_postal_suffix()


def get_name():
    return get_first_name(), get_last_name()

def register(email, firstName, lastName, postalCode, password):
    print(
        f"\n---\nNow registering\n"
        f"Password: {password}\n"
        f"Email: {email}\n"
        f"First Name: {firstName}\n"
        f"Last Name: {lastName}\n"
        f"Postal Code: {postalCode}\n---\n"
    )

    browser = webdriver.Firefox()

    # load registration page
    browser.get("https://www.journie.ca/en-CA/Registration/NewCep")

    # fill in registration form
    firstName_field = browser.find_element(By.ID, "FirstName")
    firstName_field.send_keys(firstName)

    lastName_field = browser.find_element(By.ID, "LastName")
    lastName_field.send_keys(lastName)

    email_field = browser.find_element(By.ID, "EmailAddress")
    email_field.send_keys(email)

    postalCode_field = browser.find_element(By.ID, "PostalCode")
    postalCode_field.send_keys(postalCode)

    password_field = browser.find_element(By.ID, "Password")
    password_field.send_keys(password)

    confirmPassword_field = browser.find_element(By.ID, "ConfirmPassword")
    confirmPassword_field.send_keys(password)

    termsAndCondition_checkbox = browser.find_element(
        By.XPATH,
        "/html/body/div[1]/div[1]/div[1]/div[2]/form/div[4]/div[1]/div[2]/div[2]/div/label/div",
    )
    termsAndCondition_checkbox.click()

    submit = browser.find_element(By.ID, "btnSubmit")
    submit.click()

    user = input(f"Options:\n- Enter to Continue\n- b to exit\n- 0 to skip account\n> ")

    if user == "b":
        browser.quit()
        exit(0)

    elif user == "0":
        browser.quit()
        return

    with open("registered_emails", "a") as f:
        f.write(email + ":" + password + "\n")
        f.close()

    browser.quit()


if __name__ == "__main__":
    while True:
        email = generate_email()
        if not email:
            break
        firstName, lastName = get_name()
        postalCode = generate_postal_code()
        # password = generate_password()
        register(email, firstName, lastName, postalCode, PASSWORD)
