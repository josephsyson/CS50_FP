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
):  # this function will retrieve the data about NEOs from the NASA API which will then be used for the rest of the programs calculations. The plan is to organize certapytin data about each NEO in a time frame and store them in a list which will allow for organized access to the data for the rest of the program.
    Start_Date = date(Check_Input_Data[3], Check_Input_Data[4], Check_Input_Data[5])
    End_Date = date(Check_Input_Data[6], Check_Input_Data[7], Check_Input_Data[8])
    NEO_Web_API = requests.get(Check_Input_Data[0])
    NEO_json = NEO_Web_API.json()
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
    Orbital_Period_List = []  # Orbital Period of each NEO (days)
    while (
        Start_Date <= End_Date
    ):  # Loops through the NEO - Feed API for all the dates within a specific time frame. Retrieves the IDs, calculates the average diameter by using the max and min diameter (meters) and dividing by 2, lists the relative velocity (km/h), and the miss distance (km) for each NEO and stores them in their respective lists.
        date_key = str(Start_Date)
        if date_key in NEO_json["near_earth_objects"]:
            for NEO in NEO_json["near_earth_objects"][date_key]:
                ID_List.append(NEO["id"])
                NEO_Name_List.append(NEO["name"])
                Individual_NEO_Data_API = requests.get(
                    "https://api.nasa.gov/neo/rest/v1/neo/"
                    + NEO["id"]
                    + "?api_key="
                    + Check_Input_Data[9]
                )
                Individual_NEO_Data_Json = Individual_NEO_Data_API.json()
                Semi_Major_Axis_List.append(
                    Individual_NEO_Data_Json["orbital_data"]["semi_major_axis"]
                )
                Eccentricity_List.append(
                    Individual_NEO_Data_Json["orbital_data"]["eccentricity"]
                )
                Inclination_List.append(
                    Individual_NEO_Data_Json["orbital_data"]["inclination"]
                )
                Perihelion_Distance_List.append(
                    Individual_NEO_Data_Json["orbital_data"]["perihelion_distance"]
                )
                Aphelion_Distance_List.append(
                    Individual_NEO_Data_Json["orbital_data"]["aphelion_distance"]
                )

        Start_Date += timedelta(days=1)
    NEO_Data = {
        "ID:": ID_List,
        "Name:": NEO_Name_List,
        "Semi Major Axis (a):": Semi_Major_Axis_List,
        "Eccentricity (e):": Eccentricity_List,
        "Inclination (i):": Inclination_List,
        "Perihelion Distance (q):": Perihelion_Distance_List,
        "Aphelion Distance (Q):": Aphelion_Distance_List,
    }
    return NEO_Data


def NEO_Grouping(NEO_Data):
    # This function will group the NEOs based on their orbital characteristics, such as their semi-major axis, eccentricity, and inclination. The NEOs can be grouped into different categories, such as Apollo, Amor, and Aten asteroids, which are based on their orbital characteristics. The grouping can provide insight into the potential impact risk of the NEOs and can help to identify any patterns or trends in the data. Furthermore it solves for the minimum delta V required to intercept the NEO. USE THIS WEBSITE: https://cneos.jpl.nasa.gov/about/neo_groups.html

    for n in range(
        len(NEO_Data["ID:"])
    ):  # Loops through each NEO and calculates their respective delta V using the Shoemaker-Helin method, which is a method for calculating the delta V required to intercept a NEO based on its orbital characteristics. The method uses the semi-major axis, eccentricity, inclination, perihelion distance, and aphelion distance of the NEO to calculate the delta V required for a mission to intercept the NEO. The delta V can provide insight into the potential impact risk of the NEO and can help to identify any patterns or trends in the data.
        a = float(NEO_Data["Semi Major Axis (a):"][n])
        q = float(NEO_Data["Perihelion Distance (q):"][n])
        Q = float(NEO_Data["Aphelion Distance (Q):"][n])
        i = float(NEO_Data["Inclination (i):"][n])
        e = float(NEO_Data["Eccentricity (e):"][n])

        if a < 1.0:
            if Q < 0.983:  # Atira Asteroid
                U_L_Value = U_L(U_t_sq(Q, i))
                U_c_value = U_Aten_and_Atira(Q, i, a, e)["U_c_sq"]
                U_r_value = U_Aten_and_Atira(Q, i, a, e)["U_r_sq"]

            else:  # Aten Asteroid
                U_L_Value = U_L(U_t_sq(Q, i))
                U_c_value = U_Aten_and_Atira(Q, i, a, e)["U_c_sq"]
                U_r_value = U_Aten_and_Atira(Q, i, a, e)["U_r_sq"]

        elif a >= 1.0:
            if q < 1.017:  # Apollo Asteroid
                U_L_Value = U_L(U_T_sq(q, i))
                U_c_value = U_Apollo(q, i, a, e)["U_c_sq"]
                U_r_value = U_Apollo(q, i, a, e)["U_r_sq"]

            elif 1.017 <= q < 1.3:  # Amor Asteroid
                U_L_Value = U_L(U_T_sq(q, i))
                U_c_value = U_Amor(q, i, a, e)["U_c_sq"]
                U_r_value = U_Amor(q, i, a, e)["U_r_sq"]
            else:
                U_L_Value = U_L(U_T_sq(q, i))
                U_c_value = U_Amor(q, i, a, e)["U_c_sq"]
                U_r_value = U_Amor(q, i, a, e)["U_r_sq"]
            # This is an uncommon NEO - it does not fit into any of the common groups, but it can still be analyzed using the Shoemaker-Helin method to calculate its Delta V and potential impact risk. For the calculation we will use the same equations as the Amor astroids as they are more likely to be further from the sun (1 <a) and therefore will fit more closely with their corresponding equations.

        U_R_Value = U_R(U_c_value, U_r_value, i)
        F = (
            U_L_Value + U_R_Value
        )  # F is the outboud Delta V required to intercept the NEO, which is the sum of the Low Earth Orbit departure delta V (U_L) and the rendezvous Delta V (U_R).
        Total_Delta_V = (
            F + U_R_Value
        )  # The total Delta V can be estimated by adding the rendevous velocity to the one way delta V

        print(
            "NEO Name: "
            + NEO_Data["Name:"][n]
            + ", F (One Way Delta V): "
            + str(F)
            + ", Total Delta V: "
            + str(Total_Delta_V)
        )


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
    U_c_sq = (  # U_c is the normalized velocity of an object in a circular orbit with a radius equal to the distance from the sun to where the rendezvous occurs, which in the case for Amor asteroids is at the aphelion distance (Q) of the asteroid's orbit. Essentially this step alligns the inclination of the spacecraft's trajectory with the inclination of the asteroid's orbit at the point of rendezvous, which is important for minimizing the delta V required for the mission. Represented by Equation 5 from the 1978 Shoemaker-Helin paper. Used Pehelion distance (q) for the calculation as that is the closest point to Earth and therefore the most likely point of rendezvous.
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
        (3 / Q) - 1 - ((2 / Q) * math.sqrt(2 - Q))
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


main()

# https://ntrs.nasa.gov/api/citations/19780021079/downloads/19780021079.pdf
# Things to add:
# - Estimated Kinetic Energy of the NEOs
# - Potential Impact Risk of the NEOs
# - delta v of the NEOs using the Hohmann Transfer Orbit which the equation is: delta_v = sqrt((2 * G * M) / r) - sqrt(G * M / r) where G is the gravitational constant, M is the mass of the Earth, and r is the distance from the NEO to the Earth. We can also use the Vis-viva equation to calculate the velocity of the NEO at different points in its orbit, which can be used to calculate the delta v required for a Hohmann transfer orbit. The Vis-viva equation is: v = sqrt(G * M * (2 / r - 1 / a)) where G is the gravitational constant, M is the mass of the Sun, r is the distance from the NEO to the Sun, and a is the semi-major axis of the NEO's orbit. We can use this equation to calculate the velocity of the NEO at its closest approach to Earth and at its farthest point from Earth, and then use those velocities to calculate the delta v required for a Hohmann transfer orbit.
# - Angular Momentum using the cross product of the position and velocity vectors of the NEO, which can be calculated using the equation: L = r x v where L is the angular momentum, r is the position vector of the NEO relative to Earth, and v is the velocity vector of the NEO relative to Earth. We can use this equation to calculate the angular momentum of the NEO at different points in its orbit, which can provide insight into its orbital characteristics and potential impact risk.
