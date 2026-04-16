import requests  # type: ignore
import re
from datetime import date, timedelta
import math


def main():
    NEO_Grouping(find_neo(check_input()))


def check_input():  # receives the user input and checks that it is valid as well as accepted by the API

    user_start_date = input("Enter Start Date (YYYY-MM-DD): ")  # start day check
    start_year, start_month, start_day = map(
        int, user_start_date.split("-")
    )  # splits the date into year, month and day
    while True:
        if re.fullmatch(
            r"^\d{4}-\d{2}-\d{2}$", user_start_date
        ):  # Ensures that the input date is in the correct format for the API
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
            date(end_year, end_month, end_day)
            >= date(start_year, start_month, start_day)
            and (
                date(end_year, end_month, end_day)
                - date(start_year, start_month, start_day)
            ).days
            <= 7
        ):  # Checks that the end date is after the start date as well as that they are within 7 days of each other
            if re.fullmatch(r"^\d{4}-\d{2}-\d{2}$", user_end_date):
                if (
                    validate_date(user_end_date) == True
                ):  # Uses the date function to check that date actually exists.
                    if 1900 <= end_year <= 2200:
                        break
                    else:
                        user_end_date = input(
                            "End Date must be between 1900 and 2200. Please Re-enter End Date (YYYY-MM-DD): "  # Checks that the year is between 1900 and 2200, which is the range of years accepted by the API
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

    user_API_key = input(
        "Enter API Key: "
    )  # API key input, the API key is used to access the NASA API and retrieve data about near earth objects. The user can obtain an API key by registering on the NASA API website. The API key is a unique identifier that allows the user to access the API and retrieve data about near earth objects. The user can use the API key to make requests to the API and retrieve data about near earth objects, such as their size, distance from Earth, and potential impact risk. The user can also use the API key to access other NASA APIs and retrieve data about other space-related topics.
    NEO_Web_link = (
        "https://api.nasa.gov/neo/rest/v1/feed?start_date="
        + user_start_date
        + "&end_date="
        + user_end_date
        + "&api_key="
        + user_API_key
    )
    while True:
        if (
            test_API_key(NEO_Web_link) == 200
        ):  # Code 200 is when the API key is valid and the request was completed
            break
        elif (
            test_API_key(NEO_Web_link) == 403
        ):  # Code 403 is when the API key is invalid and needs to be re-entered
            user_API_key = input("Invalid API Key. Please Re-enter API Key: ")
        elif (
            test_API_key(NEO_Web_link) == 429
        ):  # Code 429 is when the API key has exceeded the number of requests allowed and needs to be re-entered after some time has passed
            print(
                "API Key has exceeded the number of requests allowed. Please try again later."
            )
        else:
            user_API_key = input(
                "Invalid API Key format. Please Re-enter API Key: "
            )  # Accounts for any other error codes - may need to be updated to account for any other error codes that may arise

    return [
        NEO_Web_link,
        user_start_date,
        user_end_date,
        start_year,
        start_month,
        start_day,
        end_year,
        end_month,
        end_day,
        user_API_key,
    ]  # returns the API link and the user inputs for use in the rest of the program. # 0 = API link, 1 = start date, 2 = end date, 3 = start year, 4 = start month, 5 = start day, 6 = end year, 7 = end month, 8 = end day, 9 = API key


def validate_date(
    date_string,
):  # Checks that the date is valid and exists in the calendar, for example, 02/29/2026 is not valid because 2026 is not a leap year.
    try:
        year, month, day = map(int, date_string.split("-"))
        date(year, month, day)
        return True
    except ValueError:
        return False


def test_API_key(
    NEO_Web_link,
):  # Returns the status code of the API request to the Check Input funcion, which can be used to determine if the API key is valid or if there are any issues with the request. The status code can be used to provide feedback to the user and prompt them to re-enter their API key if it is invalid or if there are any issues with the request.
    NEO_Web = requests.get(NEO_Web_link)
    Status_Code = NEO_Web.status_code
    return Status_Code


def find_neo(
    Check_Input_Data,
):  # this function will retrieve the data about NEOs from the NASA API which will then be used for the rest of the programs calculations. The plan is to organize certain data about each NEO in a time frame and store them in a list which will allow for organized access to the data for the rest of the program.
    Start_Date = date(Check_Input_Data[3], Check_Input_Data[4], Check_Input_Data[5])
    End_Date = date(Check_Input_Data[6], Check_Input_Data[7], Check_Input_Data[8])
    NEO_Web_API = requests.get(Check_Input_Data[0])
    NEO_json = NEO_Web_API.json()
    # These are the lists which will store the data about the NEOs, the same positional argument in each list will correspond to the same NEO, for example, the NEO with ID_List[0] will have a diameter of Diameter_List[0], a relative velocity of Relative_Velocity_List[0], and a miss distance of Miss_Distance_List[0]:
    ID_List = [] # ID of each NEO
    NEO_Name_List = [] # Name of each NEO
    Semi_Major_Axis_List = [] # Semi Majoral Axis of each NEO (a)
    Eccentricity_List = [] # Eccentricity of each NEO (e)
    Inclination_List = [] # Inclination of each NEO (i)
    Perihelion_Distance_List = [] # Perihelion Distance of each NEO (q)
    Aphelion_Distance_List = [] # Aphelion Distance of each NEO (Q)
    Diameter_List = [] # Diameter of each NEO (m)
    Relative_Velocity_List = [] # Relative Velocity of each NEO (km/h)
    Miss_Distance_List = [] # Miss Distance of each NEO (km)
    Orbital_Period_List = [] # Orbital Period of each NEO (days)
    while (
        Start_Date <= End_Date
    ):  # Loops through the NEO - Feed API for all the dates within a specific time frame. Retrieves the IDs, calculates the average diameter by using the max and min diameter (meters) and dividing by 2, lists the relative velocity (km/h), and the miss distance (km) for each NEO and stores them in their respective lists.
        date_key = str(Start_Date)
        for NEO in NEO_json["near_earth_objects"][date_key]:
            ID_List.append(NEO["id"])
            NEO_Name_List.append(NEO["name"])
            Individual_NEO_Data_API = requests.get(
                "https://api.nasa.gov/neo/rest/v1/neo/"
                + NEO["id"]
                + "?api_key="
                + Check_Input_Data[9])
            Individual_NEO_Data_Json = Individual_NEO_Data_API.json()
            Semi_Major_Axis_List.append(Individual_NEO_Data_Json["orbital_data"]["semi_major_axis"])
            Eccentricity_List.append(Individual_NEO_Data_Json["orbital_data"]["eccentricity"])
            Inclination_List.append(Individual_NEO_Data_Json["orbital_data"]["inclination"])
            Perihelion_Distance_List.append(Individual_NEO_Data_Json["orbital_data"]["perihelion_distance"])
            Aphelion_Distance_List.append(Individual_NEO_Data_Json["orbital_data"]["aphelion_distance"])

            Start_Date += timedelta(days=1)
    NEO_Data = {"ID:": ID_List, "Name:": NEO_Name_List, "Semi Major Axis (a):": Semi_Major_Axis_List, "Eccentricity (e):": Eccentricity_List, "Inclination (i):": Inclination_List, "Perihelion Distance (q):": Perihelion_Distance_List, "Aphelion Distance (Q):": Aphelion_Distance_List}
    return NEO_Data


def NEO_Grouping(NEO_Data):
    # This function will group the NEOs based on their orbital characteristics, such as their semi-major axis, eccentricity, and inclination. The NEOs can be grouped into different categories, such as Apollo, Amor, and Aten asteroids, which are based on their orbital characteristics. The grouping can provide insight into the potential impact risk of the NEOs and can help to identify any patterns or trends in the data. USE THIS WEBSITE: https://cneos.jpl.nasa.gov/about/neo_groups.html

    for n in range (len(NEO_Data["ID:"])):
        a = float(NEO_Data["Semi Major Axis (a):"][n])
        q = float(NEO_Data["Perihelion Distance (q):"][n])
        Q = float(NEO_Data["Aphelion Distance (Q):"][n])
        i = float(NEO_Data["Inclination (i):"][n])
        
        if a < 1.0:
            if Q < .983: # Atira Asteriod
                print(NEO_Data["ID:"][n], NEO_Data["Name:"][n], "is an Atira Asteroid")
            else: # Aten Asteroid
                print(NEO_Data["ID:"][n], NEO_Data["Name:"][n], "is an Aten Asteroid")
            
        elif a >= 1.0:
            if q < 1.017: # Apollo Asteroid
                U_T(Q, i)
            
            elif q >= 1.017 and q < 1.3: # Amor Asteroid
                U_T(Q, i)
                
            else:
                print("Rare NEO")
        
# The following section of code will be the calculations for Delta V depending on the different type of NEO. I will be using the Shoemaker-Helin method for this. Here are the important equations:
# F = U_L + U_R which is the total Delta V

def U_T(Q, i):
     # U_T is the normalized velocity used to predict the Delta V for misions to Amor and Apollo asteroids.
     UT = (3 - (2/(Q + 1)) - (2 * math.sqrt((2 * Q) / (Q + 1))) * (math.cos(math.radians(i / 2))))
     return UT

def U_t(Q, i):
main()

# Things to add:
# - Estimated Kinetic Energy of the NEOs
# - Potential Impact Risk of the NEOs
# - delta v of the NEOs using the Hohmann Transfer Orbit which the equation is: delta_v = sqrt((2 * G * M) / r) - sqrt(G * M / r) where G is the gravitational constant, M is the mass of the Earth, and r is the distance from the NEO to the Earth. We can also use the Vis-viva equation to calculate the velocity of the NEO at different points in its orbit, which can be used to calculate the delta v required for a Hohmann transfer orbit. The Vis-viva equation is: v = sqrt(G * M * (2 / r - 1 / a)) where G is the gravitational constant, M is the mass of the Sun, r is the distance from the NEO to the Sun, and a is the semi-major axis of the NEO's orbit. We can use this equation to calculate the velocity of the NEO at its closest approach to Earth and at its farthest point from Earth, and then use those velocities to calculate the delta v required for a Hohmann transfer orbit.
# - Angular Momentum using the cross product of the position and velocity vectors of the NEO, which can be calculated using the equation: L = r x v where L is the angular momentum, r is the position vector of the NEO relative to Earth, and v is the velocity vector of the NEO relative to Earth. We can use this equation to calculate the angular momentum of the NEO at different points in its orbit, which can provide insight into its orbital characteristics and potential impact risk.

