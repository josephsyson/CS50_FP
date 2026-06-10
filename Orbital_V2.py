import requests  # type: ignore
import re
from datetime import date, timedelta
import math
import asyncio
import aiohttp


async def main():
    Input_Data = check_input()  # Calls the check input functino and stores it
    NEO_Data = await find_neo(Input_Data)
    Shoemaker_Helin_result = Shoemaker_Helin(NEO_Data)
    print(Shoemaker_Helin_result)
    Hohmann_Transfer_result = Hohmann_Transfer(NEO_Data)
    print(Hohmann_Transfer_result)


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


async def find_neo(Check_Input_Data):
    Start_Date = date(Check_Input_Data[3], Check_Input_Data[4], Check_Input_Data[5])
    End_Date = date(Check_Input_Data[6], Check_Input_Data[7], Check_Input_Data[8])
    NEO_Web_Link = Check_Input_Data[0]
    NEO_json = requests.get(
        NEO_Web_Link
    ).json()  # Retrieves the data from the API link and stores it as a JSON object for use in the rest of the program. The JSON object contains data about the near earth objects that were observed during the specified date range, including their size, distance from Earth, and potential impact risk. The JSON object can be used to extract specific data about the near earth objects and analyze it to determine their potential impact risk and other characteristics.
    # These are the lists which will store the data about the NEOs, the same positional argument in each list will correspond to the same NEO, for example, the NEO with ID_List[0] will have a diameter of Diameter_List[0], a relative velocity of Relative_Velocity_List[0], and a miss distance of Miss_Distance_List[0]:
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
    Orbiting_Body_List = []  # Orbiting Body of each NEO (Earth, Mars, etc.)

    temp_start = Start_Date  # This loops through each day in the specified date range and retrieves the name and ID of each NEO observed on that day, storing them in their respective lists.
    while temp_start <= End_Date:
        date_key = str(temp_start)
        if date_key in NEO_json["near_earth_objects"]:
            for NEO in NEO_json["near_earth_objects"][date_key]:
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

    NEO_Data = {
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

        results[Name] = "Asteroid Type: " + Type + ", Delta V (km/s): " + str(Delta_V_KmS)

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
        r_2 = float(NEO_Data["Semi Major Axis (a):"][n]) * 149597870.7  # km, this is the semi-major axis of the NEO's orbit, which is used as the radius of the NEO's orbit in the Hohmann transfer calculations. The approximation assumes a circular orbit.
        Name = NEO_Data["Name:"][n]

        v_1 = math.sqrt(µ / r_1)  # km/s, this is the velocity of the spacecraft in Earth's orbit before the transfer burn, calculated using the vis-viva equation.
        v_2 = math.sqrt(µ / r_2)  # km/s, this is the velocity of the spacecraft in the NEO's orbit after the transfer burn, calculated using the vis-viva equation.
        
        v_transfer_1 = math.sqrt((2 * µ) * ((1 / r_1) - (1 / (r_1 + r_2)))) # The velocity of the circular transfer orbit as it leaves the initial orbit, calculated using the vis-viva equation.
        v_transfer_2 = math.sqrt((2 * µ) * ((1 / r_2) - (1 / (r_1 + r_2)))) # The velocity of the circular transfer orbit as it enters the final orbit, calculated using the vis-viva equation.

        Δv_1 = math.fabs(v_transfer_1 - v_1)  # km/s, this is the delta V required for the first burn to leave Earth's orbit and enter the transfer orbit, calculated as the difference between the transfer orbit velocity and the initial orbit velocity.
        Δv_2 = math.fabs(v_2 - v_transfer_2)  # km/s, this is the delta V required for the second burn to leave the transfer orbit and enter the NEO's orbit, calculated as the difference between the final orbit velocity and the transfer orbit velocity

        Total_Δv = Δv_1 + Δv_2  # km/s, this is the total delta V required for the Hohmann transfer mission, calculated as the sum of the delta V for the first and second burns.

        t = math.pi * math.sqrt(((r_1 + r_2) ** 3) / (8 * µ))  # seconds, this is the time of flight for the Hohmann transfer, calculated using Kepler's third law.
        t_days = t / (60 * 60 * 24)  # days, this is the time of flight for the Hohmann transfer converted from seconds to days.

        results[Name] = "Total Δv (km/s): " + str(Total_Δv) + ", Time of Flight (days): " + str(t_days)
    return results

asyncio.run(main())
