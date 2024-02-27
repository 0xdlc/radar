from typing import Dict,Any

class deset(dict):


    def __init__(self, flight_details):


        self.id = flight_details['identification'].get("id")
        #self.aircraft_code = flight_details['aircraft']['model'].get("code")
        self.__default_text = "N/A"
        self.aircraft_code = self.__get_details(flight_details.get("registration"))

        aircraft = self.__get_details(flight_details.get("aircraft"))

        # Get airline data.
        airline = self.__get_details(flight_details.get("airline"))

        # Get airport data.
        airport = self.__get_details(flight_details.get("airport"))

        # Get destination data.
        dest_airport = self.__get_details(airport.get("destination"))
        dest_airport_code = self.__get_details(dest_airport.get("code"))
        dest_airport_info = self.__get_details(dest_airport.get("info"))
        dest_airport_position = self.__get_details(dest_airport.get("position"))
        dest_airport_country = self.__get_details(dest_airport_position.get("country"))
        dest_airport_timezone = self.__get_details(dest_airport.get("timezone"))

        # Get origin data.
        orig_airport = self.__get_details(airport.get("origin"))
        orig_airport_code = self.__get_details(orig_airport.get("code"))
        orig_airport_info = self.__get_details(orig_airport.get("info"))
        orig_airport_position = self.__get_details(orig_airport.get("position"))
        orig_airport_country = self.__get_details(orig_airport_position.get("country"))
        orig_airport_timezone = self.__get_details(orig_airport.get("timezone"))

        # Get flight history.
        history = self.__get_details(flight_details.get("flightHistory"))

        # Get flight status.
        status = self.__get_details(flight_details.get("status"))

        # Aircraft information.
        self.aircraft_age = self.__get_info(aircraft.get("age"))
        self.aircraft_country_id = self.__get_info(aircraft.get("countryId"))
        #self.aircraft_history = history.get("aircraft", list())
        self.aircraft_model = self.__get_info(self.__get_details(aircraft.get("model")).get("text"))

        # Airline information.
        self.airline_name = self.__get_info(airline.get("name"))
        self.airline_short_name = self.__get_info(airline.get("short"))

        # Destination airport position.
        self.destination_airport_altitude = self.__get_info(dest_airport_position.get("altitude"))
        self.destination_airport_country_code = self.__get_info(dest_airport_country.get("code"))
        self.destination_airport_country_name = self.__get_info(dest_airport_country.get("name"))
        self.destination_airport_latitude = self.__get_info(dest_airport_position.get("latitude"))
        self.destination_airport_longitude = self.__get_info(dest_airport_position.get("longitude"))

        # Destination airport information.
        self.destination_airport_icao = self.__get_info(dest_airport_code.get("icao"))
        self.destination_airport_baggage = self.__get_info(dest_airport_info.get("baggage"))
        self.destination_airport_gate = self.__get_info(dest_airport_info.get("gate"))
        self.destination_airport_name = self.__get_info(dest_airport.get("name"))
        self.destination_airport_terminal = self.__get_info(dest_airport_info.get("terminal"))
        self.destination_airport_visible = self.__get_info(dest_airport.get("visible"))
        self.destination_airport_website = self.__get_info(dest_airport.get("website"))

        # Destination airport timezone.
        self.destination_airport_timezone_abbr = self.__get_info(dest_airport_timezone.get("abbr"))
        self.destination_airport_timezone_abbr_name = self.__get_info(dest_airport_timezone.get("abbrName"))
        self.destination_airport_timezone_name = self.__get_info(dest_airport_timezone.get("name"))
        self.destination_airport_timezone_offset = self.__get_info(dest_airport_timezone.get("offset"))
        self.destination_airport_timezone_offsetHours = self.__get_info(dest_airport_timezone.get("offsetHours"))

        # Origin airport position.
        self.origin_airport_altitude = self.__get_info(orig_airport_position.get("altitude"))
        self.origin_airport_country_code = self.__get_info(orig_airport_country.get("code"))
        self.origin_airport_country_name = self.__get_info(orig_airport_country.get("name"))
        self.origin_airport_latitude = self.__get_info(orig_airport_position.get("latitude"))
        self.origin_airport_longitude = self.__get_info(orig_airport_position.get("longitude"))

        # Origin airport information.
        self.origin_airport_icao = self.__get_info(orig_airport_code.get("icao"))
        self.origin_airport_baggage = self.__get_info(orig_airport_info.get("baggage"))
        self.origin_airport_gate = self.__get_info(orig_airport_info.get("gate"))
        self.origin_airport_name = self.__get_info(orig_airport.get("name"))
        self.origin_airport_terminal = self.__get_info(orig_airport_info.get("terminal"))
        self.origin_airport_visible = self.__get_info(orig_airport.get("visible"))
        self.origin_airport_website = self.__get_info(orig_airport.get("website"))

        # Origin airport timezone.
        self.origin_airport_timezone_abbr = self.__get_info(orig_airport_timezone.get("abbr"))
        self.origin_airport_timezone_abbr_name = self.__get_info(orig_airport_timezone.get("abbrName"))
        self.origin_airport_timezone_name = self.__get_info(orig_airport_timezone.get("name"))
        self.origin_airport_timezone_offset = self.__get_info(orig_airport_timezone.get("offset"))
        self.origin_airport_timezone_offsetHours = self.__get_info(orig_airport_timezone.get("offsetHours"))

        # Flight status.
        self.status_icon = self.__get_info(status.get("icon"))
        self.status_text = self.__get_info(status.get("text"))

        # Time details.
        #self.time_details = self.__get_details(flight_details.get("time"))

        # Flight trail.


    def __get_details(self, data) -> Dict:
        return dict() if data is None else data

    def __get_info(self, info: Any) -> Any:
        return info if (info or info == 0) and info != self.__default_text else self.__default_text