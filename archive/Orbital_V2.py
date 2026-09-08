import requests  # type: ignore
import re
from datetime import date, timedelta, datetime
import julian
import math
import asyncio
import aiohttp
import numpy as np
from astroquery.jplhorizons import Horizons


async def main():
    Input_Data = check_input()  # Calls the check input functino and stores it
    NEO_Data = await find_neo(Input_Data)
    Shoemaker_Helin_result = Shoemaker_Helin(NEO_Data)
    print(Shoemaker_Helin_result)
    Hohmann_Transfer_result = Hohmann_Transfer(NEO_Data)
    print(Hohmann_Transfer_result)
    Lambert_Problem_Variables = Lambert_Problem_Preparation(NEO_Data)
    Lambert_Delta_v_Prograde, Lambert_Delta_v_Retrograde = Lambert_Problem_Solver(
        Lambert_Problem_Variables
    )
    print("Prograde Delta V: ", Lambert_Delta_v_Prograde)
    print("Retrograde Delta V: ", Lambert_Delta_v_Retrograde)


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

    Time_of_Flight_days = input(
        "Enter Time of Flight in days: "
    )  # Time of flight input, this is used for the Lambert problem calculations to determine the delta V required for a mission to intercept a NEO within a specific time frame. The time of flight can provide insight into the potential impact risk of the NEO and can help to identify any patterns or trends in the data.

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
        Time_of_Flight_days,
    ]  # returns the API link and the user inputs for use in the rest of the program. # 0 = API link, 1 = start date, 2 = end date, 3 = start year, 4 = start month, 5 = start day, 6 = end year, 7 = end month, 8 = end day, 9 = API key, 10 = Time of Flight days


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


async def find_neo(Check_Input_Data):
    Start_Date = date(Check_Input_Data[3], Check_Input_Data[4], Check_Input_Data[5])
    End_Date = date(Check_Input_Data[6], Check_Input_Data[7], Check_Input_Data[8])
    NEO_Web_Link = Check_Input_Data[0]
    NEO_json = requests.get(
        NEO_Web_Link
    ).json()  # Retrieves the data from the API link and stores it as a JSON object for use in the rest of the program. The JSON object contains data about the near earth objects that were observed during the specified date range, including their size, distance from Earth, and potential impact risk. The JSON object can be used to extract specific data about the near earth objects and analyze it to determine their potential impact risk and other characteristics.
    # These are the lists which will store the data about the NEOs, the same positional argument in each list will correspond to the same NEO, for example, the NEO with ID_List[0] will have a diameter of Diameter_List[0], a relative velocity of Relative_Velocity_List[0], and a miss distance of Miss_Distance_List[0]:
    Date_List = []  # Date of each NEO's closest approach to Earth
    ID_List = []  # ID of each NEO
    NEO_Name_List = []  # Name of each NEO
    Semi_Major_Axis_List = []  # Semi Majoral Axis of each NEO (a)
    Eccentricity_List = []  # Eccentricity of each NEO (e)
    Inclination_List = []  # Inclination of each NEO (i)
    Perihelion_Distance_List = []  # Perihelion Distance of each NEO (q)
    Aphelion_Distance_List = []  # Aphelion Distance of each NEO (Q)
    Diameter_List = []  # Diameter of each NEO (m)
    Relative_Velocity_List = []  # Relative Velocity of each NEO (km/h)
    Miss_Distance_List = []  # Miss Distance of each NEO (km)
    Orbital_Period_List = []
    Epoch_Osculation_List = (
        []
    )  # Epoch Osculation of each NEO (the date at which the orbital elements are calculated)
    Mean_Motion_List = (
        []
    )  # Mean Motion of each NEO (the average angular velocity of the NEO as it orbits the Sun, usually measured in degrees per day or radians per day)
    Mean_Anomaly_List = (
        []
    )  # Mean Anomaly of each NEO (the angle between the periapsis and the current position of the NEO, usually measured in degrees)
    ascending_node_longitude_list = (
        []
    )  # Longitude of the ascending node of each NEO (the angle between the reference direction and the ascending node of the NEO's orbit, usually measured in degrees)
    Argument_of_Perihelion_List = []

    temp_start = Start_Date  # This loops through each day in the specified date range and retrieves the name and ID of each NEO observed on that day, storing them in their respective lists.
    while temp_start <= End_Date:
        date_key = str(temp_start)
        if date_key in NEO_json["near_earth_objects"]:
            for NEO in NEO_json["near_earth_objects"][date_key]:
                Date_List.append(date_key)
                ID_List.append(NEO["id"])
                NEO_Name_List.append(NEO["name"])
        temp_start += timedelta(days=1)

    async with aiohttp.ClientSession() as Session:  # This functino grabs the complete data for each NEO using their respective IDs. The specific data is then retrieved and stored in lists.
        Tasks = [
            Individual_NEO_Data(Session, NEO_ID, Check_Input_Data[9])
            for NEO_ID in ID_List
        ]
        All_NEO_Data = await asyncio.gather(*Tasks)

    for NEO_Data in All_NEO_Data:
        Semi_Major_Axis_List.append(NEO_Data["orbital_data"]["semi_major_axis"])
        Eccentricity_List.append(NEO_Data["orbital_data"]["eccentricity"])
        Inclination_List.append(NEO_Data["orbital_data"]["inclination"])
        Perihelion_Distance_List.append(NEO_Data["orbital_data"]["perihelion_distance"])
        Aphelion_Distance_List.append(NEO_Data["orbital_data"]["aphelion_distance"])
        Diameter_List.append(
            NEO_Data["estimated_diameter"]["meters"]["estimated_diameter_max"]
        )
        Relative_Velocity_List.append(
            NEO_Data["close_approach_data"][0]["relative_velocity"][
                "kilometers_per_hour"
            ]
        )
        Miss_Distance_List.append(
            NEO_Data["close_approach_data"][0]["miss_distance"]["kilometers"]
        )
        Orbital_Period_List.append(NEO_Data["orbital_data"]["orbital_period"])
        Epoch_Osculation_List.append(NEO_Data["orbital_data"]["epoch_osculation"])
        Mean_Motion_List.append(NEO_Data["orbital_data"]["mean_motion"])
        Mean_Anomaly_List.append(NEO_Data["orbital_data"]["mean_anomaly"])
        ascending_node_longitude_list.append(
            NEO_Data["orbital_data"]["ascending_node_longitude"]
        )
        Argument_of_Perihelion_List.append(
            NEO_Data["orbital_data"]["perihelion_argument"]
        )

    NEO_Data = {
        "Date:": Date_List,
        "ID:": ID_List,
        "Name:": NEO_Name_List,
        "Semi Major Axis (a):": Semi_Major_Axis_List,
        "Eccentricity (e):": Eccentricity_List,
        "Inclination (i):": Inclination_List,
        "Perihelion Distance (q):": Perihelion_Distance_List,
        "Aphelion Distance (Q):": Aphelion_Distance_List,
        "Diameter (m):": Diameter_List,
        "Relative Velocity (km/h):": Relative_Velocity_List,
        "Miss Distance (km):": Miss_Distance_List,
        "Orbital Period (days):": Orbital_Period_List,
        "Epoch_Osculation_List": Epoch_Osculation_List,
        "Mean_Motion_List": Mean_Motion_List,
        "Mean_Anomaly_list": Mean_Anomaly_List,
        "ascending_node_longitude_list": ascending_node_longitude_list,
        "Argument_of_Perihelion_List": Argument_of_Perihelion_List,
        "Time_of_Flight_days": Check_Input_Data[10],
    }
    return NEO_Data


async def Individual_NEO_Data(
    Session, NEO_ID, API_Key
):  # This function simultaneously retrieves the complete data for each NEO using their respectiv IDs per the request from the find_neo function.
    url = f"https://api.nasa.gov/neo/rest/v1/neo/{NEO_ID}?api_key={API_Key}"
    async with Session.get(url) as response:
        return await response.json()


def Shoemaker_Helin(NEO_Data):
    # This function will group the NEOs based on their orbital characteristics, such as their semi-major axis, eccentricity, and inclination. The NEOs can be grouped into different categories, such as Apollo, Amor, and Aten asteroids, which are based on their orbital characteristics. Using such classifications, the Shoemaker-Helin method is used to calculate the round trip Delta V in Km/s. The source used to classify such NEOS is: https://cneos.jpl.nasa.gov/about/neo_groups.html

    results = {}

    for n in range(
        len(NEO_Data["ID:"])
    ):  # Loops through each NEO and calculates their respective delta V using the Shoemaker-Helin method, which is a method for calculating the delta V required to intercept a NEO based on its orbital characteristics. The method uses the semi-major axis, eccentricity, inclination, perihelion distance, and aphelion distance of the NEO to calculate the delta V required for a mission to intercept the NEO. The delta V can provide insight into the potential impact risk of the NEO and can help to identify any patterns or trends in the data.
        date = NEO_Data["Date:"][n]
        a = float(NEO_Data["Semi Major Axis (a):"][n])
        q = float(NEO_Data["Perihelion Distance (q):"][n])
        Q = float(NEO_Data["Aphelion Distance (Q):"][n])
        i = float(NEO_Data["Inclination (i):"][n])
        e = float(NEO_Data["Eccentricity (e):"][n])
        Name = NEO_Data["Name:"][n]

        if a < 1.0:
            if Q < 0.983:  # Atira Asteroid
                U_L_Value = U_L(U_t_sq(Q, i))
                U_c_value = U_Aten_and_Atira(Q, i, a, e)["U_c_sq"]
                U_r_value = U_Aten_and_Atira(Q, i, a, e)["U_r_sq"]
                Type = "Atira"

            else:  # Aten Asteroid
                U_L_Value = U_L(U_t_sq(Q, i))
                U_c_value = U_Aten_and_Atira(Q, i, a, e)["U_c_sq"]
                U_r_value = U_Aten_and_Atira(Q, i, a, e)["U_r_sq"]
                Type = "Aten"

        elif a >= 1.0:
            if q < 1.017:  # Apollo Asteroid
                U_L_Value = U_L(U_T_sq(q, i))
                U_c_value = U_Apollo(q, i, a, e)["U_c_sq"]
                U_r_value = U_Apollo(q, i, a, e)["U_r_sq"]
                Type = "Apollo"

            elif 1.017 <= q < 1.3:  # Amor Asteroid
                U_L_Value = U_L(U_T_sq(q, i))
                U_c_value = U_Amor(q, i, a, e)["U_c_sq"]
                U_r_value = U_Amor(q, i, a, e)["U_r_sq"]
                Type = "Amor"

            else:
                U_L_Value = U_L(U_T_sq(q, i))
                U_c_value = U_Amor(q, i, a, e)["U_c_sq"]
                U_r_value = U_Amor(q, i, a, e)["U_r_sq"]
                Type = "Uncommon NEO"
            # This is an uncommon NEO - it does not fit into any of the common groups, but it can still be analyzed using the Shoemaker-Helin method to calculate its Delta V and potential impact risk. For the calculation we will use the same equations as the Amor astroids as they are more likely to be further from the sun (1 <a) and therefore will fit more closely with their corresponding equations.

        U_R_Value = U_R(U_c_value, U_r_value, i)
        Delta_V_KmS = 29.78 * (
            U_L_Value + (2 * U_R_Value)
        )  # Delta_v_kmS is the minimum possible delta V for an entire round trip mission to the NEO and back to Earth.

        results[Name] = (
            "Date: "
            + date
            + " Asteroid Type: "
            + Type
            + ", Delta V (km/s): "
            + str(Delta_V_KmS)
        )

    return results


# The following section of code will be the calculations for Delta V depending on the different type of NEO. I will be using the Shoemaker-Helin method for this. Here are the important equations:
# F = U_L + U_R which is the total Delta V


def U_T_sq(q, i):
    # U_T_sq is the normaliized hyperbolic excess velocity when espcaping Earth, usually selected to reach targes with a > 1.0 such as apollo and amor asteroids. Uses the perihelion distance (q) to represent the closest distance to Earth.
    U_T_sq = (
        3
        - (2 / (q + 1))
        - (2 * math.sqrt((2 * q) / (q + 1))) * (math.cos(math.radians(i / 2)))
    )  # Equation 3 from the 1978 Shoemaker-Helin paper
    return U_T_sq


def U_t_sq(
    Q, i
):  # U_t_sq is the normaliized hyperbolic excess velocity when espcaping Earth, usually selected to reach targes with a < 1.0 such as atira and aten asteroids. Uses the aphelion distance (Q) to represent the closest distance to Earth.
    # U_t_sq is the normaliized hyperbolic excess velocity when espcaping Earth, usually selected to reach targes with a < 1.0 such as atira and aten asteroids.
    U_t_sq = 2 - (
        2 * (math.sqrt((2 * Q) - (Q**2))) * (math.cos(math.radians(i / 2)))
    )  # Equation 9 from the 1978 Shoemaker-Helin paper
    return U_t_sq


def U_L(Normalized_Hyperbolic_Excess_Velocity_sq):
    # U_L is the Normalized Low Earth Orbit (LEO) departure delta-V required to put a spacecraft on a trajectory to intercept the NEO.
    S = 0.3756  # S is the Normalized Escape Speed of Earth. Shoemaker-Helin method uses a value of 0.3756 which is the escape velocity of Earth (11.186 km/s) divided by the circular velocity of Earth (29.78 km/s).
    U_0 = 0.2596  # U_0 is the Normalized Low Earth Orbit (Approximately 100km circular orbit) Speed. Shoemaker-Helin method uses a value of 0.2596 which is the speed of a low Earth orbit (7.73 km/s) divided by the circular velocity of Earth (29.78 km/s).
    U_L = (
        math.sqrt((Normalized_Hyperbolic_Excess_Velocity_sq) + (S**2))
    ) - U_0  # Equation 2 from the 1978 Shoemaker_Helin paper
    return U_L


def U_Amor(
    q, i, a, e
):  # Calculates the specific U_c_sq and U_r_sq values for Amor asteroids using the equations from the 1978 Shoemaker-Helin paper.
    U_c_sq = (  # U_c is the normalized velocity of an object in a circular orbit with a radius equal to the distance from the sun to where the rendezvous occurs, which in the case for Amor asteroids is at the perihelion distance (q) of the asteroid's orbit. Essentially this step alligns the inclination of the spacecraft's trajectory with the inclination of the asteroid's orbit at the point of rendezvous, which is important for minimizing the delta V required for the mission. Represented by Equation 5 from the 1978 Shoemaker-Helin paper. Used Pehelion distance (q) for the calculation as that is the closest point to Earth and therefore the most likely point of rendezvous.
        (3 / q)
        - (2 / (q + 1))
        - ((2 / q) * math.sqrt((2 / (q + 1))) * (math.cos(math.radians(i / 2))))
    )
    U_r_sq = (  # U_r is the normalized relative velocity between the spacecraft and the asteroid at the point of rendezvous. It essentially represents the burn required to match the velocity of the NEO. Represented by Equation 6 from the 1978 Shoemaker-Helin paper. Used Pehelion distance (q) for the calculation as that is the closest point to Earth and therefore the most likely point of rendezvous.
        (3 / q) - (1 / a) - ((2 / q) * math.sqrt((a / q) * (1 - e**2)))
    )
    return {"U_c_sq": U_c_sq, "U_r_sq": U_r_sq}


def U_Apollo(q, i, a, e):
    U_c_sq = (  # Same concept as U_c_sq for Amor asteroids, but without the inclinaion component as Shoemaker-Helin's method uses a slightly different route to approach such objects. Represented by Equation 7 from the 1978 Shoemaker-Helin paper. Used Pehelion distance (q) for the calculation as that is the closest point to Earth and therefore the most likely point of rendezvous.
        (3 / q) - (2 / (q + 1)) - ((2 / q) * math.sqrt((2 / (q + 1))))
    )  # Equation 7 from the 1978 Shoemaker-Helin paper
    U_r_sq = (  # Again, same concept as U_r_sq for Amor asteroids, but this time including the inlcination component as the equations for Apollo asteroids account for the inclination in a slighlty different way than the Amor asteroids. Represented by Equation 8 from the 1978 Shoemaker-Helin paper. Used Pehelion distance (q) for the calculation as that is the closest point to Earth and therefore the most likely point of rendezvous.
        (3 / q)
        - (1 / a)
        - ((2 / q) * math.sqrt((a / q) * (1 - e**2)) * (math.cos(math.radians(i / 2))))
    )  # Equation 8 from the 1978 Shoemaker-Helin paper
    return {"U_c_sq": U_c_sq, "U_r_sq": U_r_sq}


def U_Aten_and_Atira(Q, i, a, e):
    U_c_sq = (  # Same concept as U_c_sq for Amor and Apollo asteroids, but this time using the aphelion distance (Q) for the calculation as that is the closest point to Earth and therefore the most likely point of rendezvous for Aten and Atira asteroids. Represented by Equation 10 from the 1978 Shoemaker-Helin paper.
        (3 / Q) - 1 - ((2 / Q) * math.sqrt(2 - Q)) * (math.cos(math.radians(i / 2)))
    )  # Equation 10 from the 1978 Shoemaker-Helin paper
    U_r_sq = (  # Same concept as U_r_sq for Amor and Apollo asteroids, but this time using the aphelion distance (Q) for the calculation as that is the closest point to Earth and therefore the most likely point of rendezvous for Aten and Atira asteroids. Represented by Equation 11 from the 1978 Shoemaker-Helin paper.
        (3 / Q)
        - (1 / a)
        - ((2 / Q) * math.sqrt((a / Q) * (1 - e**2)) * (math.cos(math.radians(i / 2))))
    )  # Equation 8 from the 1978 Shoemaker-Helin paper
    return {"U_c_sq": U_c_sq, "U_r_sq": U_r_sq}


def U_R(
    U_c_sq, U_r_sq, i
):  # U_R is the rendezvous delta V required to meet the NEO. It is calculated through the burn to match the velocity (U_r_sq) and thge burn to match the inclination (U_c_sq) at the point of rendezvous. Represented by Equation 4 from the 1978 Shoemaker-Helin paper. This valkue can also be used to estimate the return trip delta V, as the required burns to get to the object are often similar to the required burns to return from the object and intercept Earth again.
    U_R_value = math.sqrt(
        U_c_sq
        - (2 * math.sqrt(U_c_sq) * math.sqrt(U_r_sq) * math.cos(math.radians(i / 2)))
        + U_r_sq
    )  # Equation 4 from the 1978 Shoemaker-Helin paper
    return U_R_value


def Hohmann_Transfer(NEO_Data):
    r_1 = 149597870.7  # km, this is the average distance from the Earth to the Sun, which is used as the radius of Earth's orbit in the Hohmann transfer calculations.
    µ = 1.32712440018e11  # km^3/s^2, this is the standard gravitational parameter of the Sun, which is used in the Hohmann transfer calculations to determine the velocities of the spacecraft at different points in the transfer orbit.

    results = {}

    for n in range(len(NEO_Data["ID:"])):
        date = NEO_Data["Date:"][n]

        r_2 = (
            float(NEO_Data["Semi Major Axis (a):"][n]) * 149597870.7
        )  # km, this is the semi-major axis of the NEO's orbit, which is used as the radius of the NEO's orbit in the Hohmann transfer calculations. The approximation assumes a circular orbit.
        Name = NEO_Data["Name:"][n]

        v_1 = math.sqrt(
            µ / r_1
        )  # km/s, this is the velocity of the spacecraft in Earth's orbit before the transfer burn, calculated using the vis-viva equation.
        v_2 = math.sqrt(
            µ / r_2
        )  # km/s, this is the velocity of the spacecraft in the NEO's orbit after the transfer burn, calculated using the vis-viva equation.

        v_transfer_1 = math.sqrt(
            (2 * µ) * ((1 / r_1) - (1 / (r_1 + r_2)))
        )  # The velocity of the circular transfer orbit as it leaves the initial orbit, calculated using the vis-viva equation.
        v_transfer_2 = math.sqrt(
            (2 * µ) * ((1 / r_2) - (1 / (r_1 + r_2)))
        )  # The velocity of the circular transfer orbit as it enters the final orbit, calculated using the vis-viva equation.

        Δv_1 = math.fabs(
            v_transfer_1 - v_1
        )  # km/s, this is the delta V required for the first burn to leave Earth's orbit and enter the transfer orbit, calculated as the difference between the transfer orbit velocity and the initial orbit velocity.
        Δv_2 = math.fabs(
            v_2 - v_transfer_2
        )  # km/s, this is the delta V required for the second burn to leave the transfer orbit and enter the NEO's orbit, calculated as the difference between the final orbit velocity and the transfer orbit velocity

        Total_Δv = (
            Δv_1 + Δv_2
        )  # km/s, this is the total delta V required for the Hohmann transfer mission, calculated as the sum of the delta V for the first and second burns.

        t = math.pi * math.sqrt(
            ((r_1 + r_2) ** 3) / (8 * µ)
        )  # seconds, this is the time of flight for the Hohmann transfer, calculated using Kepler's third law.
        t_days = t / (
            60 * 60 * 24
        )  # days, this is the time of flight for the Hohmann transfer converted from seconds to days.

        results[Name] = (
            "Date: "
            + date
            + ", Total Δv (km/s): "
            + str(Total_Δv)
            + ", Time of Flight (days): "
            + str(t_days)
        )
    return results


def Lambert_Problem_Preparation(
    NEO_Data,
):  # Gathers the necessary data for solving the Lambert problem including solving for the postions and velocities of each NEO as well as the Earth for that specific date. The corresponding functions used to convert the API data from the 6 orbital elements to position and velocity vectors use the equations explained in: https://www.youtube.com/watch?v=zi0FGTGnbB4&t=3290s.
    Lambert_Variables = {}
    for n in range(len(NEO_Data["ID:"])):
        name = NEO_Data["Name:"][n]
        date = NEO_Data["Date:"][n]
        epoch_osculation = NEO_Data["Epoch_Osculation_List"][n]
        mean_motion = NEO_Data["Mean_Motion_List"][n]
        initial_mean_anomaly = NEO_Data["Mean_Anomaly_list"][n]
        e = float(NEO_Data["Eccentricity (e):"][n])
        a = float(NEO_Data["Semi Major Axis (a):"][n])
        Raan = math.radians(float(NEO_Data["ascending_node_longitude_list"][n]))
        Argument_of_Perihelion = math.radians(
            float(NEO_Data["Argument_of_Perihelion_List"][n])
        )
        inclination = math.radians(float(NEO_Data["Inclination (i):"][n]))

        Time_of_Flight_days = float(NEO_Data["Time_of_Flight_days"])
        Format_Date = datetime.strptime(date, "%Y-%m-%d")
        Arrival_Date = Format_Date + timedelta(days=Time_of_Flight_days)
        Arrival_Date_String = Arrival_Date.strftime("%Y-%m-%d")

        Mean_Anomaly = Mean_Anomaly_of_Inputted_Date(
            epoch_osculation, Arrival_Date_String, mean_motion, initial_mean_anomaly
        )
        Eccentric_Anomaly = Eccentric_Anomaly_Calculation(Mean_Anomaly, e)
        True_Anomaly = True_Anomaly_Calculation(Eccentric_Anomaly, e)

        r_NEO = (a * (1 - e**2)) / (
            1 + (e * math.cos(True_Anomaly))
        )  # This is the equation to calculate the distance from the sun to the NEO at the inputted date, which is needed to calculate the position and velocity vectors for the Lambert problem solution.

        True_Anomaly_dot = True_Anomaly_Dot_Calculation(a, e, r_NEO)

        r_dot_NEO = (
            ((a * (1 - e**2)) * (e * math.sin(True_Anomaly)))
            / (1 + (e * math.cos(True_Anomaly))) ** 2
        ) * (
            True_Anomaly_dot
        )  # This is the equation to calculate the rate of change of the distance from the sun to the NEO.

        x_perifocal_NEO = r_NEO * math.cos(
            True_Anomaly
        )  # The x component of the NEO's position vector in the perifocal reference frame.
        y_perifocal_NEO = r_NEO * math.sin(
            True_Anomaly
        )  # The y component of the NEO's position vector in the perifocal reference frame.
        z_perifocal_NEO = 0  # The z component of the NEO's position vector in the perifocal reference frame, which is 0 because the NEO's orbit is assumed to be in the plane of the ecliptic.

        x_dot_periofocal_NEO = (r_dot_NEO * math.cos(True_Anomaly)) - (
            r_NEO * math.sin(True_Anomaly) * True_Anomaly_dot
        )  # The x component of the NEO's velocity vector in the perifocal reference frame.

        y_dot_periofocal_NEO = (r_dot_NEO * math.sin(True_Anomaly)) + (
            r_NEO * math.cos(True_Anomaly) * True_Anomaly_dot
        )  # The y component of the NEO's velocity vector in the perifocal reference frame.

        z_dot_periofocal_NEO = 0  # The z component of the NEO's velocity vector in the perifocal reference frame, which is 0 because the NEO's orbit is assumed to be in the plane of the ecliptic.

        r_perifocal_NEO = np.array(
            [x_perifocal_NEO, y_perifocal_NEO, z_perifocal_NEO]
        )  # The NEO's position vector in the perifocal reference frame.

        v_perifocal_NEO = np.array(
            [x_dot_periofocal_NEO, y_dot_periofocal_NEO, z_dot_periofocal_NEO]
        )  # The NEO's velocity vector in the perifocal reference frame.

        # The following functions are the rotation matrices to convert the NEO's position vector from the perifocal reference frame to the geocentric equatorial reference frame, which is needed for the Lambert problem solution. The rotation is done in the order of Raan, Inclination, and Argument of Perihelion and the matrices are in the order of 3-1-3, which is the standard order for orbital mechanics calculations.
        C_3_Raan = C_3(Raan)
        C_1_Inclination = C_1(inclination)
        C_3_Argument_of_Perihelion = C_3(Argument_of_Perihelion)

        C_pi = (
            C_3_Argument_of_Perihelion @ C_1_Inclination @ C_3_Raan
        )  # The combined rotation matrix to convert from the perifocal reference frame to the inertial reference frame.

        C_ip = C_pi.T

        r_inertial_NEO = (
            C_ip @ r_perifocal_NEO
        )  # The NEO's position vector in the inertial reference frame, which is needed for the Lambert problem solution in AU

        v_intertial_NEO = (
            C_ip @ v_perifocal_NEO
        )  # The NEO's velocity vector in the inertial reference frame, which is needed for the Lambert problem solution in AU/s

        r_Earth, v_Earth = Earth_Data(
            date
        )  # The position and velocity vectors of the Earth in the inertial reference frame at the inputted date, which is needed for the Lambert problem solution. The poistion is in AU and the velocity is in AU/day.

        AU_to_Km = 149597870.7  # This is the conversion factor from astronomical units (AU) to kilometers (km), which is used to convert the position vectors from AU to km for the Lambert problem solution.

        r_NEO_km = (
            r_inertial_NEO * AU_to_Km
        )  # The NEO's position vector in the inertial reference frame in km.
        v_NEO_km = (
            v_intertial_NEO * AU_to_Km
        )  # The NEO's velocity vector in the inertial reference frame in km/s.
        r_Earth_km = (
            r_Earth * AU_to_Km
        )  # The Earth's position vector in the inertial reference frame in km.
        v_Earth_km = (
            v_Earth * AU_to_Km / 86400
        )  # The Earth's velocity vector in the inertial reference frame in km/s.

        Lambert_Variables[name] = {
            "r_Earth": r_Earth_km,
            "v_Earth": v_Earth_km,
            "r_NEO": r_NEO_km,
            "v_NEO": v_NEO_km,
            "Time_of_Flight_days": Time_of_Flight_days,
        }

    return Lambert_Variables


def Mean_Anomaly_of_Inputted_Date(
    epoch_osculation, date, mean_motion, initial_mean_anomaly
):
    # The epoch osculation is the date at which the orbital elements of the NEO are calculated, the unit is days.
    # This step converts the inputted date into Julian Date format.
    dt = datetime.strptime(date, "%Y-%m-%d")
    JD = julian.to_jd(dt, fmt="jd")
    time_elapsed = JD - float(
        epoch_osculation
    )  # This step calculates the time elapsed between tine input date and the epoch osculation in days.

    Mean_Anomaly = (
        float(initial_mean_anomaly) + (float(mean_motion) * time_elapsed)
    ) % 360  # This step calculates the mean anomaly of the NEO at the inputted date using the mean motion and the time elapsed since the epoch osculation. The result is taken modulo 360 to ensure that it is within the range of 0 to 360 degrees.

    Mean_Anomaly_Radians = math.radians(
        Mean_Anomaly
    )  # This step converts the mean anomaly from degrees to radians, which is the unit typically used in orbital mechanics calculations.

    return Mean_Anomaly_Radians


def Eccentric_Anomaly_Calculation(
    Mean_Anomaly, e
):  # Using the Newton-Raphson method to solve for the eccentric anomaly given the mean anomaly and eccentricity of the NEO's orbit (x_n+1 = x_n - f(x_n)/f'(x_n)). The eccentric anomaly is an angular parameter that describes the position of a body in an elliptical orbit as a function of time.
    E = Mean_Anomaly  # Initial guess for the eccentric anomaly
    while True:
        f_E = (
            E - e * math.sin(E) - Mean_Anomaly
        )  # This is Kepler's equation, which relates the mean anomaly, eccentric anomaly, and eccentricity of an orbit.
        f_prime_E = 1 - e * math.cos(
            E
        )  # This is the derivative of Kepler's equation with respect to the eccentric anomaly.
        E_next = (
            E - f_E / f_prime_E
        )  # This is the Newton-Raphson iteration step to refine the estimate of the eccentric anomaly.
        if (
            abs(E_next - E) < 1e-8
        ):  # This checks for convergence of the solution, where 1e-8 is a small threshold value that is commonly used in orbital mechanics calculations.
            break
        E = E_next
    return E


def True_Anomaly_Calculation(
    Eccentric_Anomaly, e
):  # This function calculates the true anomaly of the NEO at the inputted date using the eccentric anomaly and eccentricity of the NEO's orbit. The true anomaly is the angle between the direction of periapsis and the current position of the body in its orbit, measured at the focus of the ellipse (where the central body is located).
    Right_Side_of_Equation = math.sqrt((1 + e) / (1 - e)) * math.tan(
        Eccentric_Anomaly / 2
    )  # This is the right side of the equation that relates the true anomaly, eccentric anomaly, and eccentricity of an orbit.
    True_Anomaly = 2 * math.atan(Right_Side_of_Equation)  # The true Anomaly.
    return True_Anomaly


def True_Anomaly_Dot_Calculation(
    a, e, r
):  # This function calculates the rate of change of the true anomaly with respect to time using the semi-latus rectum of the orbit, the specific angular momentum of the orbit, and the distance from the central body to the NEO at the inputted date. The rate of change of the true anomaly is a measure of how quickly the NEO is moving along its orbit.
    μ = 1.32712440018e11 / (
        149597870.7**3
    )  # AU^3/s^2, this is the standard gravitational parameter of the Sun.

    p = a * (
        1 - e**2
    )  # The semi-latus rectum of the orbit, which geometrically represents the radius of the orbit measured from the central body at a perpendicular angle to to the major axis of the ellipse.

    h = math.sqrt(
        μ * p
    )  # The specific angular momentum of the orbit, which is a measure of the inertial strength of the orbiting body.

    theta_dot = h / (
        r**2
    )  # The rate of change of the true anomaly with respect to time, which is a measure of how quickly the orbiting body is moving along its orbit.

    return theta_dot


def C_1(angle):  # The rotation matrix for a rotation about the x-axis by a given angle.
    cos_angle = math.cos(angle)
    sin_angle = math.sin(angle)
    C_1_Matrix = np.array(
        [[1.0, 0.0, 0.0], [0.0, cos_angle, sin_angle], [0.0, -sin_angle, cos_angle]]
    )
    return C_1_Matrix


def C_3(angle):  # The rotation matrix for a rotation about the z-axis by a given angle.
    cos_angle = math.cos(angle)
    sin_angle = math.sin(angle)
    C_3_Matrix = np.array(
        [[cos_angle, sin_angle, 0.0], [-sin_angle, cos_angle, 0.0], [0.0, 0.0, 1.0]]
    )
    return C_3_Matrix


def Earth_Data(
    date,
):  # This function pulls the position and velocity vectors of the Earth with respect to the Sun at the inputted date. Using the astropy library https://astroquery.readthedocs.io/en/latest/api/astroquery.jplhorizons.HorizonsClass.html#astroquery.jplhorizons.HorizonsClass.vectors
    date_time = datetime.strptime(date, "%Y-%m-%d")
    jd_date = julian.to_jd(
        date_time, fmt="jd"
    )  # converts the inputted date into Julian Date which is the format used by the astropy library to calculate the position and velocity vectors of the Earth with respect to the Sun.

    obj = Horizons(
        id="399", location="500@10", epochs=jd_date
    )  # This is the astropy library function that pulls the position and velocity vectors of the Earth with respect to the Sun at the inputted date. The id='399' is the ID for Earth in the JPL Horizons system, and the location='500@10' specifies that we want the position and velocity vectors of Earth with respect to the Sun. The epochs=jd_date specifies the date for which we want the position and velocity vectors.
    vectors = obj.vectors()

    position_vector = np.array(
        [vectors["x"][0], vectors["y"][0], vectors["z"][0]]
    )  # The position vector of the Earth with respect to the Sun at the inputted date.
    velocity_vector = np.array(
        [vectors["vx"][0], vectors["vy"][0], vectors["vz"][0]]
    )  # The velocity vector of the Earth with respect to the Sun at the inputted date.

    return [
        position_vector,
        velocity_vector,
    ]  # Returns the position and velocity vectors of the Earth with respect to the Sun at the inputted date.


def Lambert_Problem_Solver(
    Lambert_Problem_Variables,
):  # This function solves the Lambert problem for each NEO using the variables found in the Lambert_Problem_Preparation function. The Lambert problem is a classical problem in orbital mechanics that involves finding the orbit that connects two points in space in a given time. The solution to the Lambert problem provides the initial and final velocities required to transfer from one point to another in a specified time, which is essential for planning interplanetary missions. The equations are cited from Section 5.3 of https://www.hlevkin.com/hlevkin/90MathPhysBioBooks/Mechanics/Curtis_OrbitamMechForEngineeringStudents.pdf

    Prograde_Results = {}
    Retrograde_Results = {}
    for name, variables in Lambert_Problem_Variables.items():
        r_Earth = variables["r_Earth"]
        v_Earth = variables["v_Earth"]
        r_NEO = variables["r_NEO"]
        v_NEO = variables["v_NEO"]
        Time_of_Flight_days = variables["Time_of_Flight_days"]
        mu = 1.32712440018e11  # km^3/s^2, this is the standard gravitational parameter of the Sun.
        cross_product_r = np.cross(r_Earth, r_NEO)
        r_Earth_norm = np.linalg.norm(r_Earth)
        r_NEO_norm = np.linalg.norm(r_NEO)

        cos_ratio = np.dot(r_Earth, r_NEO) / (
            r_Earth_norm * r_NEO_norm
        )  # This calculates the cosine of the angle between the position vectors of Earth and the NEO using the dot product formula.
        cos_ratio = np.clip(
            cos_ratio, -1.0, 1.0
        )  # Ensure the value is within the valid range for arccos

        prograde_delta_theta = prograde(cos_ratio, cross_product_r)

        retrograde_delta_theta = retrograde(cos_ratio, cross_product_r)

        A_Prograde = math.sin(prograde_delta_theta) * math.sqrt(
            (r_Earth_norm * r_NEO_norm) / (1 - math.cos(prograde_delta_theta))
        )  # A is a notation used in the Lambert problem to represent the distance between the two position vectors of Earth and the NEO.
        A_Retrograde = math.sin(retrograde_delta_theta) * math.sqrt(
            (r_Earth_norm * r_NEO_norm) / (1 - math.cos(retrograde_delta_theta))
        )

        Y_Prograde = z_Solver_Prograde(
            r_Earth_norm, r_NEO_norm, A_Prograde, Time_of_Flight_days, mu
        )
        Y_Retrograde = z_Solver_Retrograde(
            r_Earth_norm, r_NEO_norm, A_Retrograde, Time_of_Flight_days, mu
        )

        Prograde_v1, Prograde_v2 = Lambert_Langrange_Solver(
            r_Earth_norm, r_NEO_norm, r_Earth, r_NEO, mu, Y_Prograde, A_Prograde
        )
        Retrograde_v1, Retrograde_v2 = Lambert_Langrange_Solver(
            r_Earth_norm, r_NEO_norm, r_Earth, r_NEO, mu, Y_Retrograde, A_Retrograde
        )

        Total_Delta_v_Prograde = Lambert_Delta_V_Solver(
            Prograde_v1, Prograde_v2, v_Earth, v_NEO
        )
        Total_Delta_v_Retrograde = Lambert_Delta_V_Solver(
            Retrograde_v1, Retrograde_v2, v_Earth, v_NEO
        )

        Prograde_Results[name] = Total_Delta_v_Prograde
        Retrograde_Results[name] = Total_Delta_v_Retrograde

    return Prograde_Results, Retrograde_Results


def prograde(
    cos_ratio, cross_product_r
):  # Prograde is defined as the motion of an object in the same direction as the rotation of the primary body, which in this case is the Sun. In orbital mechanics, prograde motion is typically associated with lower energy requirements for orbital transfers and is often preferred for interplanetary missions. The function checks the z-component of the cross product of the position vectors of Earth and the NEO to determine if the transfer orbit is prograde or retrograde.
    if cross_product_r[2] >= 0:
        delta_theta = math.acos(cos_ratio)
    else:
        delta_theta = (2 * math.pi) - math.acos(cos_ratio)
    return delta_theta


def retrograde(
    cos_ratio, cross_product_r
):  # Retrograde is defined as the motion of an object in the opposite direction to the rotation of the primary body, which in this case is the Sun. In orbital mechanics, retrograde motion is typically associated with higher energy requirements for orbital transfers and is often avoided for interplanetary missions. The function checks the z-component of the cross product of the position vectors of Earth and the NEO to determine if the transfer orbit is prograde or retrograde.
    if cross_product_r[2] < 0:
        delta_theta = math.acos(cos_ratio)
    else:
        delta_theta = (2 * math.pi) - math.acos(cos_ratio)
    return delta_theta


def Stumpff_C(
    z,
):  # The Stumpff function for C(Z) is a mathematical function which relates to hyperbolic and elliptical orbits in orbital mechanics. C(Z) specifically relates cosine to such orbits. Equation 3.50 in Curtis, H. D. (2014). Orbital Mechanics for Engineering Students (3rd ed.). Butterworth-Heinemann.
    if z > 0:
        C = (1 - math.cos(math.sqrt(z))) / z
    elif z < 0:
        C = (math.cosh(math.sqrt(-z)) - 1) / (-z)
    else:
        C = 1 / 2
    return C


def Stumpff_S(
    z,
):  # The Stumpff function for S(Z) is a mathematical function which relates to hyperbolic and elliptical orbits in orbital mechanics. S(Z) specifically relates sine to such orbits. Equation 3.49 in Curtis, H. D. (2014). Orbital Mechanics for Engineering Students (3rd ed.). Butterworth-Heinemann.
    if z > 0:
        S = (math.sqrt(z) - math.sin(math.sqrt(z))) / (z ** (3 / 2))
    elif z < 0:
        S = (math.sinh(math.sqrt(-z)) - math.sqrt(-z)) / ((-z) ** (3 / 2))
    else:
        S = 1 / 6
    return S


def y_of_z(
    z, r_1, r_2, A
):  # This function calculates the y(z) value used in the Lambert problem solution. The y(z) value is a function of the Stumpff functions C(z) and S(z), the distance between the position vectors of Earth and the NEO (A), and the norms of the position vectors of Earth and the NEO (r_1 and r_2). The y(z) value is used to determine the time of flight for the transfer orbit.
    C = Stumpff_C(z)
    S = Stumpff_S(z)
    y = r_1 + r_2 + (A * ((z * S - 1) / math.sqrt(C)))

    if (
        A > 0 and y < 0
    ):  # If these conditions are met, the calculated z value will be impossible. This part of the function adjusts the z value in order to avoid square rooting nevative values within the z_Solver functions.
        while y < 0:
            z += 0.1
            C = Stumpff_C(z)
            S = Stumpff_S(z)
            y = r_1 + r_2 + (A * ((z * S - 1) / math.sqrt(C)))

    return z, y


def z_Solver_Prograde(
    r_Earth_norm, r_NEO_norm, A_Prograde, Time_of_Flight_days, mu
):  # This function solves for the z value used in the Lambert problem solution for prograde orbits. The z value is a parameter that relates to the geometry of the transfer orbit and is used to calculate the time of flight for the transfer orbit. The function uses the Newton-Raphson method to iteratively solve for the z value that satisfies the time of flight equation.

    TOF_Seconds = (
        Time_of_Flight_days * 86400
    )  # This converts the time of flight from days to seconds, which is the unit typically used in orbital mechanics calculations. The conversion factor is 86400 seconds per day.

    def F_of_z(
        z_val,
    ):  # This function calculates F(z) for a given z value, which is used in the Newton-Raphson method to iteratively solve for the z value that satisfies the time of flight equation. The function uses the y(z) value calculated from the y_of_z function, as well as the Stumpff functions C(z) and S(z), to calculate F(z). The goal is to find the root of F(z) = 0, which corresponds to the correct z value for the transfer orbit. This equation is cited in equation 5.40 from Curtis, H. D. (2014). Orbital Mechanics for Engineering Students (3rd ed.). Butterworth-Heinemann.
        z_val, Y_val = y_of_z(z_val, r_Earth_norm, r_NEO_norm, A_Prograde)
        C_val = Stumpff_C(z_val)
        S_val = Stumpff_S(z_val)
        return (
            (((Y_val / C_val) ** 1.5) * S_val)
            + (A_Prograde * math.sqrt(Y_val))
            - (math.sqrt(mu) * Time_of_Flight_days * 86400)
        )

    z_lo, z_hi = (
        -10.0,
        10.0,
    )  # Initial bounds for z, chosen to encompass a wide range of possible values for the Lambert problem solution. These bounds are based on typical values encountered in orbital mechanics calculations and are used to ensure that the Newton-Raphson method has a reasonable starting point for convergence.
    F_lo, F_hi = F_of_z(z_lo), F_of_z(
        z_hi
    )  # This calculates the values of F(z) at the inital bounds for z.

    while (
        F_lo * F_hi > 0
    ):  # This checks if the initial bounds for z bracket a root of F(z) = 0. If F(z) has the same sign at both bounds, it indicates that there is no root in the interval, and the bounds need to be adjusted. This is a common practice in numerical methods to ensure that the root-finding algorithm has a valid starting point.
        z_lo *= 2.0  # This expands the lower bound for z by a factor of 2.0
        z_hi *= 2.0  # This expands the upper bound for z by a factor of 2.0
        F_lo, F_hi = F_of_z(z_lo), F_of_z(
            z_hi
        )  # Recalculates the values of F(z) at the adjusted bounds for z.
        if abs(z_hi) > 1e8:
            break  # This checks if the upper bound for z has become excessively large (greater than 1e8). If it has, the loop breaks to prevent infinite expansion of the bounds, which could lead to error.

    z = 0.0  # Initial guess for z, chosen to be 0.0 as a reasonable starting point for the Newton-Raphson method. This value is based on typical values encountered in orbital mechanics calculations and is used to ensure that the method has a reasonable starting point for convergence.
    tolerance = 1e-12  # This is the convergence tolerance for the Newton-Raphson method, more precise than the previously used 1e-8.
    Max_Iterations = 100  # Sufficient number of iterations to ensure convergence of the Newton-Raphson method. This is asafe number of iterations as using the safegaurded Newton-Raphson method with bounds will usually converge within 100 iterations for the Lambert problem solution.

    for iteration in range(Max_Iterations):
        z, Y = y_of_z(z, r_Earth_norm, r_NEO_norm, A_Prograde)
        C = Stumpff_C(z)
        S = Stumpff_S(z)

        F = (
            (((Y / C) ** 1.5) * S)
            + (A_Prograde * math.sqrt(Y))
            - (math.sqrt(mu) * Time_of_Flight_days * 86400)
        )  # The function F(z) is derived from the time of flight equation for the transfer orbit and is used to determine if the current estimate of z satisfies the time of flight requirement. The goal is to find the root of F(z) = 0, which corresponds to the correct z value for the transfer orbit. This equation is cited in equation 5.40 from Curtis, H. D. (2014). Orbital Mechanics for Engineering Students (3rd ed.). Butterworth-Heinemann.

        if (
            F * F_lo > 0
        ):  # This checks if the current estimate of z is on the same side of the root as the lower bound. If it is, the bounds are adjusted to ensure that the root remains bracketed.
            z_lo = z
            F_lo = F

        else:  # This checks if the current estimate of z is on the same side of the root as the upper bound. If it is, the bounds are adjusted to ensure that the root remains bracketed.
            z_hi = z
            F_hi = F

        if z == 0.0:
            dFdz = ((math.sqrt(2) / 40) * (Y**1.5)) + (
                (A_Prograde / 8)
                * ((math.sqrt(Y) + A_Prograde * math.sqrt(1 / (2 * Y))))
            )  # In special cases where z = 0, the derivative of F with respect to z (dFdz) is calculated using a different formula to avoid division by zero errors. This is a common practice in numerical methods when dealing with special cases or singularities in the equations. This method used a series expansion to approximate the value. Cited in D. 11 the solution to the Lambert problem with Equation 5.43in Curtis, H. D. (2014). Orbital Mechanics for Engineering Students (3rd ed.). Butterworth-Heinemann.
        else:
            dFdz = (
                ((Y / C) ** 1.5)
                * (((1 / (2 * z)) * (C - (3 * S / (2 * C)))) + (3 * S**2) / (4 * C))
            ) + (A_Prograde / 8) * (
                (3 * S / C) * math.sqrt(Y) + (A_Prograde / math.sqrt(Y))
            )  # The derivative of F with respect to z (dFdz) is calculated using the chain rule and the derivatives of the Stumpff functions C(z) and S(z). This is a standard approach in numerical methods for solving equations involving special functions. This is cited in equation 5.43 from Curtis, H. D. (2014). Orbital Mechanics for Engineering Students (3rd ed.). Butterworth-Heinemann.

        z_next = z - (
            F / dFdz
        )  # This is the Newton-Raphson iteration step to refine the estimate of z. The Newton-Raphson method is a widely used numerical technique for finding roots of equations, and it is particularly effective for solving nonlinear equations like those encountered in orbital mechanics.
        if not (z_lo < z_next < z_hi):
            z_next = (
                z_lo + z_hi
            ) / 2.0  # If the next estimate of z falls outside the bounds, it is adjusted to be the midpoint of the current bounds. This is a safeguard to ensure that the Newton-Raphson method does not diverge and remains within a reasonable range for convergence.

        if abs(z_next - z) < (
            tolerance * max(1.0, abs(z))
        ):  # This checks if the convergence meets the specified tolderance. The tolerance is scaled by the magnitude of z to ensure that the convergence criterion is relative to the size of the solution, which is a common practice in numerical methods to avoid issues with very small or very large values.
            z = z_next
            break

        z = z_next  # Update the current estimate of z for the next iteration.

    z, Y_Final = y_of_z(
        z, r_Earth_norm, r_NEO_norm, A_Prograde
    )  # This calculates the final value of y(z) using the converged value of z. The y(z) value is used to determine the time of flight for the transfer orbit.
    return Y_Final


def z_Solver_Retrograde(
    r_Earth_norm, r_NEO_norm, A_Retrograde, Time_of_Flight_days, mu
):  # This function solves for the z value used in the Lambert problem solution for retrograde orbits. The z value is a parameter that relates to the geometry of the transfer orbit and is used to calculate the time of flight for the transfer orbit. The function uses the Newton-Raphson method to iteratively solve for the z value that satisfies the time of flight equation.

    TOF_Seconds = (
        Time_of_Flight_days * 86400
    )  # This converts the time of flight from days to seconds, which is the unit typically used in orbital mechanics calculations. The conversion factor is 86400 seconds per day.

    def F_of_z(
        z_val,
    ):  # This function calculates F(z) for a given z value, which is used in the Newton-Raphson method to iteratively solve for the z value that satisfies the time of flight equation. The function uses the y(z) value calculated from the y_of_z function, as well as the Stumpff functions C(z) and S(z), to calculate F(z). The goal is to find the root of F(z) = 0, which corresponds to the correct z value for the transfer orbit. This equation is cited in equation 5.40 from Curtis, H. D. (2014). Orbital Mechanics for Engineering Students (3rd ed.). Butterworth-Heinemann.
        z_val, Y_val = y_of_z(z_val, r_Earth_norm, r_NEO_norm, A_Retrograde)
        C_val = Stumpff_C(z_val)
        S_val = Stumpff_S(z_val)
        return (
            (((Y_val / C_val) ** 1.5) * S_val)
            + (A_Retrograde * math.sqrt(Y_val))
            - (math.sqrt(mu) * Time_of_Flight_days * 86400)
        )

    z_lo, z_hi = (
        -10.0,
        10.0,
    )  # Initial bounds for z, chosen to encompass a wide range of possible values for the Lambert problem solution. These bounds are based on typical values encountered in orbital mechanics calculations and are used to ensure that the Newton-Raphson method has a reasonable starting point for convergence.
    F_lo, F_hi = F_of_z(z_lo), F_of_z(
        z_hi
    )  # This calculates the values of F(z) at the inital bounds for z.

    while (
        F_lo * F_hi > 0
    ):  # This checks if the initial bounds for z bracket a root of F(z) = 0. If F(z) has the same sign at both bounds, it indicates that there is no root in the interval, and the bounds need to be adjusted. This is a common practice in numerical methods to ensure that the root-finding algorithm has a valid starting point.
        z_lo *= 2.0  # This expands the lower bound for z by a factor of 2.0
        z_hi *= 2.0  # This expands the upper bound for z by a factor of 2.0
        F_lo, F_hi = F_of_z(z_lo), F_of_z(
            z_hi
        )  # Recalculates the values of F(z) at the adjusted bounds for z.
        if abs(z_hi) > 1e8:
            break  # This checks if the upper bound for z has become excessively large (greater than 1e8). If it has, the loop breaks to prevent infinite expansion of the bounds, which could lead to error.

    z = 0.0  # Initial guess for z, chosen to be 0.0 as a reasonable starting point for the Newton-Raphson method. This value is based on typical values encountered in orbital mechanics calculations and is used to ensure that the method has a reasonable starting point for convergence.
    tolerance = 1e-12  # This is the convergence tolerance for the Newton-Raphson method, more precise than the previously used 1e-8.
    Max_Iterations = 100  # Sufficient number of iterations to ensure convergence of the Newton-Raphson method. This is asafe number of iterations as using the safegaurded Newton-Raphson method with bounds will usually converge within 100 iterations for the Lambert problem solution.

    for iteration in range(Max_Iterations):
        z, Y = y_of_z(z, r_Earth_norm, r_NEO_norm, A_Retrograde)
        C = Stumpff_C(z)
        S = Stumpff_S(z)

        F = (
            (((Y / C) ** 1.5) * S)
            + (A_Retrograde * math.sqrt(Y))
            - (math.sqrt(mu) * Time_of_Flight_days * 86400)
        )  # The function F(z) is derived from the time of flight equation for the transfer orbit and is used to determine if the current estimate of z satisfies the time of flight requirement. The goal is to find the root of F(z) = 0, which corresponds to the correct z value for the transfer orbit. This equation is cited in equation 5.40 from Curtis, H. D. (2014). Orbital Mechanics for Engineering Students (3rd ed.). Butterworth-Heinemann.

        if (
            F * F_lo > 0
        ):  # This checks if the current estimate of z is on the same side of the root as the lower bound. If it is, the bounds are adjusted to ensure that the root remains bracketed.
            z_lo = z
            F_lo = F

        else:  # This checks if the current estimate of z is on the same side of the root as the upper bound. If it is, the bounds are adjusted to ensure that the root remains bracketed.
            z_hi = z
            F_hi = F

        if z == 0.0:
            dFdz = ((math.sqrt(2) / 40) * (Y**1.5)) + (
                (A_Retrograde / 8)
                * ((math.sqrt(Y) + A_Retrograde * math.sqrt(1 / (2 * Y))))
            )  # In special cases where z = 0, the derivative of F with respect to z (dFdz) is calculated using a different formula to avoid division by zero errors. This is a common practice in numerical methods when dealing with special cases or singularities in the equations. This method used a series expansion to approximate the value. Cited in the solution to the Lambert problem in Curtis, H. D. (2014). Orbital Mechanics for Engineering Students (3rd ed.). Butterworth-Heinemann.
        else:
            dFdz = (
                ((Y / C) ** 1.5)
                * (((1 / (2 * z)) * (C - (3 * S / (2 * C)))) + (3 * S**2) / (4 * C))
            ) + (A_Retrograde / 8) * (
                (3 * S / C) * math.sqrt(Y) + (A_Retrograde / math.sqrt(Y))
            )  # The derivative of F with respect to z (dFdz) is calculated using the chain rule and the derivatives of the Stumpff functions C(z) and S(z). This is a standard approach in numerical methods for solving equations involving special functions. This is cited in equation 5.43 from Curtis, H. D. (2014). Orbital Mechanics for Engineering Students (3rd ed.). Butterworth-Heinemann.

        z_next = z - (
            F / dFdz
        )  # This is the Newton-Raphson iteration step to refine the estimate of z. The Newton-Raphson method is a widely used numerical technique for finding roots of equations, and it is particularly effective for solving nonlinear equations like those encountered in orbital mechanics.
        if not (z_lo < z_next < z_hi):
            z_next = (
                z_lo + z_hi
            ) / 2.0  # If the next estimate of z falls outside the bounds, it is adjusted to be the midpoint of the current bounds. This is a safeguard to ensure that the Newton-Raphson method does not diverge and remains within a reasonable range for convergence.

        if abs(z_next - z) < (
            tolerance * max(1.0, abs(z))
        ):  # This checks if the convergence meets the specified tolderance. The tolerance is scaled by the magnitude of z to ensure that the convergence criterion is relative to the size of the solution, which is a common practice in numerical methods to avoid issues with very small or very large values.
            z = z_next
            break

        z = z_next  # Update the current estimate of z for the next iteration.

    z, Y_Final = y_of_z(
        z, r_Earth_norm, r_NEO_norm, A_Retrograde
    )  # This calculates the final value of y(z) using the converged value of z. The y(z) value is used to determine the time of flight for the transfer orbit.
    return Y_Final


def Lambert_Langrange_Solver(
    r_Earth_norm, r_NEO_norm, r_Earth_Vec, r_NEO_Vec, mu, Y, A
):  # This function solves the Lambert problem using the Langrange method. The Langrange method is an alternative approach to solving the Lambert problem that uses the concept of Lagrange coefficients to determine the initial and final velocities required for the transfer orbit. The function calculates the Lagrange coefficients based on the position vectors of Earth and the NEO, the time of flight, and the gravitational parameter of the Sun. The resulting velocities are then used to determine the delta-v required for the transfer orbit.
    f = 1 - (
        Y / r_Earth_norm
    )  # Lagrange coefficient f, which relates the initial and final position vectors of the transfer orbit.
    g = A * math.sqrt(
        Y / mu
    )  # Lagrange coefficient g, which relates the initial position vector and the time of flight for the transfer orbit.
    g_dot = 1 - (
        Y / r_NEO_norm
    )  # Lagrange coefficient g_dot, which relates the final position vector and the time of flight for the transfer orbit.

    v1 = (1 / g) * (
        r_NEO_Vec - (f * r_Earth_Vec)
    )  # The initial velocity vector required for the transfer orbit, calculated using the Lagrange coefficients and the position vectors of Earth and the NEO. Cited in equation 5.28 from Curtis, H. D. (2014). Orbital Mechanics for Engineering Students (3rd ed.). Butterworth-Heinemann.
    v2 = (1 / g) * ((g_dot * r_NEO_Vec) - r_Earth_Vec)

    return v1, v2


def Lambert_Delta_V_Solver(v1, v2, v_Earth, v_NEO):
    Delta_V_Departure = math.fabs(np.linalg.norm(v1 - v_Earth))
    Delta_V_Arrival = math.fabs(np.linalg.norm(v2 - v_NEO))
    Total_Delta_V = Delta_V_Departure + Delta_V_Arrival

    return Total_Delta_V


asyncio.run(main())
