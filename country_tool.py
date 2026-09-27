import os
import json
import requests


# Load configuration

try:
    with open("config.json", "r") as file:
        config = json.load(file)

    API_URL = config["api_url"]

except (FileNotFoundError, json.JSONDecodeError, KeyError):
    print("Error: Could not load API configuration from config.json.")
    exit()


# Get API key from environment variable

API_KEY = os.getenv("REST_COUNTRIES_API_KEY")

if not API_KEY:
    print("Error: REST_COUNTRIES_API_KEY is not configured.")
    print("Please set your API key as an environment variable.")
    exit()


HEADERS = {
    "Authorization": f"Bearer {API_KEY}"
}


# Get country data

def get_country(country_name):

    try:
        # Main country request
        url = API_URL + country_name

        response = requests.get(
            url,
            headers=HEADERS,
            timeout=10
        )

        # Handle HTTP errors
        if response.status_code == 404:
            return {"error": f"Country '{country_name}' was not found."}

        if response.status_code == 401:
            return {"error": "Invalid or unauthorized API key."}

        if response.status_code == 429:
            return {"error": "API rate limit exceeded. Please try again later."}

        response.raise_for_status()

        # Convert JSON response
        data = response.json()

        # Check expected response structure
        country_list = data.get("data", {}).get("objects", [])

        if not country_list:
            return {"error": f"Country '{country_name}' was not found."}

        country = country_list[0]

        # Country name
        names = country.get("names", {})

        country_common_name = names.get(
            "common",
            country_name
        )

        # Capital
        capitals = country.get("capitals", [])

        if capitals and isinstance(capitals[0], dict):
            capital = capitals[0].get(
                "name",
                "Not available"
            )
        else:
            capital = "Not available"

        # Population
        population = country.get(
            "population",
            "Not available"
        )

        # Region
        region = country.get(
            "region",
            "Not available"
        )

        # Languages
        languages_data = country.get("languages", [])

        languages = []

        if isinstance(languages_data, list):

            for language in languages_data:

                if isinstance(language, dict):
                    language_name = language.get("name")

                    if language_name:
                        languages.append(language_name)

        if languages:
            languages_text = ", ".join(languages)
        else:
            languages_text = "Not available"

        # Currencies
        currencies_data = country.get("currencies", [])

        currencies = []

        if isinstance(currencies_data, list):

            for currency in currencies_data:

                if isinstance(currency, dict):

                    currency_name = currency.get(
                        "name",
                        "Unknown currency"
                    )

                    currency_code = currency.get(
                        "code",
                        ""
                    )

                    symbol = currency.get(
                        "symbol",
                        ""
                    )

                    if currency_code:
                        currencies.append(
                            f"{currency_name} ({currency_code})"
                        )

                    elif symbol:
                        currencies.append(
                            f"{currency_name} ({symbol})"
                        )

                    else:
                        currencies.append(
                            currency_name
                        )

        if currencies:
            currencies_text = ", ".join(currencies)
        else:
            currencies_text = "Not available"

        # Neighbouring countries
        borders = country.get("borders", [])

        neighbour_names = []

        if isinstance(borders, list):

            for border_code in borders:

                try:
                    neighbour_url = (
                        "https://api.restcountries.com/"
                        "countries/v5/codes.alpha_3/"
                        + border_code
                    )

                    neighbour_response = requests.get(
                        neighbour_url,
                        headers=HEADERS,
                        timeout=10
                    )

                    if neighbour_response.status_code == 200:

                        neighbour_data = (
                            neighbour_response.json()
                        )

                        neighbour_list = (
                            neighbour_data
                            .get("data", {})
                            .get("objects", [])
                        )

                        if neighbour_list:

                            neighbour = neighbour_list[0]

                            neighbour_name = (
                                neighbour
                                .get("names", {})
                                .get("common")
                            )

                            if neighbour_name:
                                neighbour_names.append(
                                    neighbour_name
                                )
                            else:
                                neighbour_names.append(
                                    border_code
                                )

                        else:
                            neighbour_names.append(
                                border_code
                            )

                    else:
                        # If neighbour lookup fails,
                        # keep the original country code.
                        neighbour_names.append(
                            border_code
                        )

                except (
                    requests.RequestException,
                    ValueError,
                    KeyError,
                    TypeError
                ):
                    neighbour_names.append(
                        border_code
                    )

        if neighbour_names:
            neighbours_text = ", ".join(neighbour_names)
        else:
            neighbours_text = "None"

        # Return clean dictionary
        return {
            "country": country_common_name,
            "capital": capital,
            "currency": currencies_text,
            "population": population,
            "languages": languages_text,
            "region": region,
            "neighbours": neighbours_text
        }


    # Network error
    except requests.RequestException:
        return {
            "error": "Network error. Please check your internet connection."
        }

    # Invalid JSON
    except ValueError:
        return {
            "error": "The API returned an invalid JSON response."
        }

    # Unexpected response structure
    except (KeyError, TypeError):
        return {
            "error": "Unexpected response format from the API."
        }


# Display travel snapshot
def display_snapshot(country_data):

    if "error" in country_data:
        print()
        print("Error:", country_data["error"])
        return

    print()
    print("========== COUNTRY TRAVEL SNAPSHOT ==========")

    print(
        f"Country     : {country_data['country']}"
    )

    print(
        f"Capital     : {country_data['capital']}"
    )

    print(
        f"Currency    : {country_data['currency']}"
    )

    print(
        f"Population  : {country_data['population']:,}"
        if isinstance(country_data["population"], int)
        else f"Population  : {country_data['population']}"
    )

    print(
        f"Languages   : {country_data['languages']}"
    )

    print(
        f"Region      : {country_data['region']}"
    )

    print(
        f"Neighbours  : {country_data['neighbours']}"
    )

    print("=============================================")


def main():

    country_name = input(
        "Enter country name: "
    ).strip()

    if not country_name:
        print("Error: Country name cannot be empty.")
        return

    country_data = get_country(country_name)

    display_snapshot(country_data)


if __name__ == "__main__":
    main()