import requests  # type: ignore
import re
from datetime import date


def main():
    find_neo(check_input())


def check_input():  # receives the user input and checks that it is valid as well as accepted by the API

    user_start_date = input("Enter Start Date (YYYY-MM-DD): ")  # start day check
    start_year, start_month, start_day = map(
        int, user_start_date.split("-")
    )  # splits the date into year, month and day
    while True:
        if re.fullmatch(
            r"^\d{4}-\d{2}-\d{2}$", user_start_date): # Ensures that the input date is in the correct format for the API
            if validate_date(user_start_date) == True:
                if 1900 <= start_year <= 2200:
                    break
                else:
                    user_start_date = input(
                        "Start Date must be between 1900 and 2200. Please Re-enter Start Date (YYYY-MM-DD): "
                    )  # Checks that the year is between 1900 and 2200, which is the range of years accepted by the API
                    start_year, start_month, start_day = map(
                        int, user_start_date.split("-")
                    )
            else:
                user_start_date = input(
                    "Date does not exist. Please Re-enter Start Date (YYYY-MM-DD): "
                )  # Uses the date function to check that date actually exists.
                start_year, start_month, start_day = map(
                    int, user_start_date.split("-")
                )
        else:
            user_start_date = input(
                "Invalid Start Date format. Please Re-enter Start Date (YYYY-MM-DD): "
            )
            start_year, start_month, start_day = map(int, user_start_date.split("-"))

    user_end_date = input("Enter End Date (YYYY-MM-DD): ")  # end date input
    end_year, end_month, end_day = map(int, user_end_date.split("-"))
    while True:
        if (
            start_day <= end_day
            and (end_day - start_day) <= 7
            and start_month == end_month
            and start_year == end_year
        ):  # Checks that the end date is after the start date as well as that they are within 7 days of each other
            if re.fullmatch(r"^\d{4}-\d{2}-\d{2}$", user_end_date):
                if validate_date(user_end_date) == True: # Uses the date function to check that date actually exists.
                    if 1900 <= end_year <= 2200:
                        break
                    else:
                        user_end_date = input(
                            "End Date must be between 1900 and 2200. Please Re-enter End Date (YYYY-MM-DD): " # Checks that the year is between 1900 and 2200, which is the range of years accepted by the API
                        )
                        end_year, end_month, end_day = map(
                            int, user_end_date.split("-")
                        )
                else:
                    user_end_date = input(
                        "Date does not exist. Please Re-enter End Date (YYYY-MM-DD): "
                    )
                    end_year, end_month, end_day = map(int, user_end_date.split("-"))
            else:
                user_end_date = input(
                    "Invalid End Date format. Please Re-enter End Date (YYYY-MM-DD): "
                )
                end_year, end_month, end_day = map(int, user_end_date.split("-"))
        else:
            user_end_date = input(
                "Dates must be within 7 days of each other and the end date must be on or after start date. Please Re-enter End Date (YYYY-MM-DD): "
            )
            end_year, end_month, end_day = map(int, user_end_date.split("-"))

    user_API_key = input("Enter API Key: ")  # API key input, the API key is used to access the NASA API and retrieve data about near earth objects. The user can obtain an API key by registering on the NASA API website. The API key is a unique identifier that allows the user to access the API and retrieve data about near earth objects. The user can use the API key to make requests to the API and retrieve data about near earth objects, such as their size, distance from Earth, and potential impact risk. The user can also use the API key to access other NASA APIs and retrieve data about other space-related topics.
    NEO_Web_link = (
        "https://api.nasa.gov/neo/rest/v1/feed?start_date="
        + user_start_date
        + "&end_date="
        + user_end_date
        + "&api_key="
        + user_API_key
    )
    while True:
        if test_API_key(NEO_Web_link) == 200: # Code 200 is when the API key is valid and the request was completed
            break
        elif test_API_key(NEO_Web_link) == 403: # Code 403 is when the API key is invalid and needs to be re-entered
            user_API_key = input("Invalid API Key. Please Re-enter API Key: ")
        elif test_API_key(NEO_Web_link) == 429: # Code 429 is when the API key has exceeded the number of requests allowed and needs to be re-entered after some time has passed
            print(
                "API Key has exceeded the number of requests allowed. Please try again later."
            )
        else:
            user_API_key = input("Invalid API Key format. Please Re-enter API Key: ") # Accounts for any other error codes - may need to be updated to account for any other error codes that may arise

    return NEO_Web_link


def validate_date(
    date_string,):  # Checks that the date is valid and exists in the calendar, for example, 02/29/2026 is not valid because 2026 is not a leap year.
    try:
        year, month, day = map(int, date_string.split("-"))
        date(year, month, day)
        return True
    except ValueError:
        return False


def test_API_key(NEO_Web_link): # Returns the status code of the API request to the Check Input funcion, which can be used to determine if the API key is valid or if there are any issues with the request. The status code can be used to provide feedback to the user and prompt them to re-enter their API key if it is invalid or if there are any issues with the request.
    NEO_Web = requests.get(NEO_Web_link)
    Status_Code = NEO_Web.status_code
    return Status_Code


def find_neo(NEO_Web_link): # this function will retrieve the data about NEOs from the NASA API which will then be used for the rest of the programs calculations. The plan is to organize certain data about each NEO in a time frame and store them in a list which will allow for organized access to the data for the rest of the program.
    NEO_Web = requests.get(NEO_Web_link)
    NEO = NEO_Web.json()
    print(NEO)


main()
# code: 403 is when the API key is invalid, code: 200 is when the API key is valid and the request was completed
