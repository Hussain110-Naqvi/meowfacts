import requests
import json
from datetime import datetime, timezone

# --- Base Configuration ---
BASE_URL = "https://meowfacts.herokuapp.com/"
# Supported languages for fetching facts
SUPPORTED_LANGUAGES = [
    "eng", "cze", "ger", "ben", "esp", "rus", "por",
    "fil", "ukr", "urd", "ita", "zho", "kor"
]
# Dictionary to map language codes to full, readable names.
LANGUAGE_CODE_TO_NAME = {
    "eng": "English",
    "cze": "Czech",
    "ger": "German",
    "ben": "Bengali",
    "esp": "Spanish",
    "rus": "Russian",
    "por": "Portuguese",
    "fil": "Filipino",
    "ukr": "Ukrainian",
    "urd": "Urdu",
    "ita": "Italian",
    "zho": "Chinese",
    "kor": "Korean"
}
OUTPUT_FILENAME = "meowfacts_dataset.json"

def get_total_facts_count():
    """
    Determines the total number of unique facts available from the API.
    """
    print("Determining the total number of facts...")
    known_facts = set()
    current_id = 1
    while True:
        try:
            params = {'id': current_id}
            response = requests.get(BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            fact = data['data'][0]

            if fact in known_facts:
                print(f"Found a duplicate fact at ID {current_id}. Total unique facts: {current_id - 1}")
                return current_id - 1
            
            known_facts.add(fact)
            if current_id % 10 == 0:
                print(f"Checked up to ID {current_id}...")
            current_id += 1

        except requests.exceptions.RequestException as e:
            print(f"An error occurred while trying to determine fact count: {e}")
            return current_id - 1
        except (ValueError, IndexError, KeyError):
            print(f"Received unexpected data format at ID {current_id}. Assuming this is the end.")
            return current_id - 1


def fetch_all_facts(total_facts):
    """
    Fetches all facts for all supported languages from the Meowfacts API.
    """
    all_facts_data = []
    print(f"\nFetching {total_facts} facts in {len(SUPPORTED_LANGUAGES)} languages...")

    for lang_code in SUPPORTED_LANGUAGES:
        # Look up the full language name, defaulting to the code if not found.
        language_name = LANGUAGE_CODE_TO_NAME.get(lang_code, lang_code)
        print(f"\n--- Fetching facts for language: {language_name} ({lang_code}) ---")
        
        for i in range(1, total_facts + 1):
            try:
                params = {'id': i}
                if lang_code != 'eng':
                    params['lang'] = lang_code

                response = requests.get(BASE_URL, params=params, timeout=10)
                response.raise_for_status()

                data = response.json()
                fact_text = data['data'][0]

                # [UPDATED] Create a structured record using the full language name.
                fact_record = {
                    "fact_id": i,
                    "language": language_name,
                    "fact": fact_text,
                    "retrieved_at_utc": datetime.now(timezone.utc).isoformat()
                }
                all_facts_data.append(fact_record)

                if i % 25 == 0:
                    print(f"Fetched {i}/{total_facts} facts for '{language_name}'...")

            except requests.exceptions.RequestException as e:
                print(f"Could not fetch fact ID {i} for language '{language_name}'. Error: {e}")
                continue
            except (ValueError, IndexError, KeyError):
                print(f"Could not parse data for fact ID {i} in language '{language_name}'. Skipping.")
                continue

    return all_facts_data

def save_to_json(data):
    """
    Saves the provided data to a JSON file.
    """
    print(f"\nSaving {len(data)} records to '{OUTPUT_FILENAME}'...")
    try:
        with open(OUTPUT_FILENAME, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print("Successfully saved data.")
    except IOError as e:
        print(f"Error saving file: {e}")

def main():
    """
    Main entry point for the script.
    """
    print("Starting Meowfacts data extraction process.")
    
    total_facts = get_total_facts_count()
    
    if total_facts > 0:
        all_data = fetch_all_facts(total_facts)
        if all_data:
            save_to_json(all_data)
        else:
            print("No data was fetched. The output file will not be created.")
    else:
        print("Could not determine the number of facts. Exiting.")
        
    print("\nExtraction process finished.")

if __name__ == "__main__":
    main()

