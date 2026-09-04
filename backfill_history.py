import joram
import datetime
import logging
import json
import os
import re
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
from constants import (
    GASOLINE_95,
    DIESEL,
    COLORED_DIESEL,
    GASOLINE_98,
    DIFFERENCE_95_98_PRICE,
    START_DATE_KEY,
    END_DATE_KEY,
    GAS_KEY,
    PDF_URL_KEY,
    CURRENT_GAS_HISTORY_JSON_FILE,
    CURRENT_GAS_HISTORY_CSV_FILE,
    CSV_HEADER,
)
from functions import (
    replace_gas_keys_names,
    retrieve_week_by_date,
    return_next_week_by_date,
    parse_price,
    csv_row,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# Shared resources
all_history = {}
history_lock = Lock()
new_entries_count = 0


def entry_complete(entry):
    if not entry:
        return False
    gas_data = entry.get(GAS_KEY, {})
    return all(
        k in gas_data for k in (GASOLINE_95, DIESEL, COLORED_DIESEL, GASOLINE_98)
    ) and bool(entry.get(PDF_URL_KEY))


def process_pdf(year, pdf_filename, pdf_date):
    global new_entries_count
    start_date, end_date = retrieve_week_by_date(return_next_week_by_date(pdf_date))

    with history_lock:
        if start_date in all_history and entry_complete(all_history[start_date]):
            return

    pdf_url = f"https://joram.madeira.gov.pt/joram/2serie/Ano de {year}/{pdf_filename}"
    try:
        prices_gen = joram.read_pdf_prices(pdf_url)
        prices_dict = dict(prices_gen)
    except Exception as e:
        logging.warning(f"Error reading {pdf_url}: {e}")
        return

    if prices_dict:
        prices_dict = replace_gas_keys_names(prices_dict)

        gas_data = {}
        for k, v in prices_dict.items():
            try:
                gas_data[k] = parse_price(v)
            except (ValueError, AttributeError) as e:
                logging.error(f"Error parsing price for {k}: {v}. Error: {e}")

        if GASOLINE_95 in gas_data:
            gas_data[GASOLINE_98] = round(
                gas_data[GASOLINE_95] + DIFFERENCE_95_98_PRICE, 3
            )

        if gas_data:
            with history_lock:
                # Add or update entry
                is_new = start_date not in all_history
                all_history[start_date] = {
                    START_DATE_KEY: start_date,
                    END_DATE_KEY: end_date,
                    GAS_KEY: gas_data,
                    PDF_URL_KEY: pdf_url,
                }
                if is_new:
                    new_entries_count += 1
                    logging.info(f"  Added entry for {start_date} from {pdf_filename}")
                else:
                    logging.info(
                        f"  Updated entry for {start_date} from {pdf_filename}"
                    )


def backfill():
    global all_history, new_entries_count
    if os.path.exists(CURRENT_GAS_HISTORY_JSON_FILE):
        with open(CURRENT_GAS_HISTORY_JSON_FILE, "r") as f:
            all_history = json.load(f)

    current_year = datetime.datetime.now().year
    new_entries_count = 0

    for year in range(current_year, 2007, -1):
        url = f"https://joram.madeira.gov.pt/joram/2serie/Ano de {year}/"
        logging.info(f"Processing year {year}...")
        try:
            links = joram.get_sorted_pdf_links(url)
        except Exception as e:
            logging.error(f"Error fetching links for {year}: {e}")
            continue

        tasks = []
        for link in reversed(links):
            pdf_filename = link["href"].split("/")[-1]
            date_match = re.search(r"\d{4}-\d{2}-\d{2}", pdf_filename)
            if not date_match:
                continue

            try:
                pdf_date = datetime.datetime.strptime(date_match.group(), "%Y-%m-%d")
            except ValueError:
                continue

            if pdf_date > datetime.datetime.now():
                continue

            # Heuristic: Price updates usually happen on Fridays/Saturdays/Mondays.
            # But if we have missing data, we check all days to be more thorough.
            start_date, _ = retrieve_week_by_date(return_next_week_by_date(pdf_date))
            with history_lock:
                is_missing = not entry_complete(all_history.get(start_date))

            if not is_missing and pdf_date.weekday() not in [0, 4, 5]:
                continue

            tasks.append((year, pdf_filename, pdf_date))

        # Use ThreadPoolExecutor for concurrent PDF processing
        with ThreadPoolExecutor(max_workers=5) as executor:
            for task in tasks:
                executor.submit(process_pdf, *task)

        # Save progress after each year
        with history_lock:
            sorted_history = dict(sorted(all_history.items()))
            with open(CURRENT_GAS_HISTORY_JSON_FILE, "w") as f:
                json.dump(sorted_history, f, indent=2, ensure_ascii=False)

    # Final update of both JSON and CSV
    with history_lock:
        sorted_history = dict(sorted(all_history.items()))
        with open(CURRENT_GAS_HISTORY_JSON_FILE, "w") as f:
            json.dump(sorted_history, f, indent=2, ensure_ascii=False)

        with open(CURRENT_GAS_HISTORY_CSV_FILE, "w") as f:
            f.write(CSV_HEADER)
            for start_date in sorted(sorted_history.keys()):
                entry = sorted_history[start_date]
                f.write(
                    csv_row(
                        start_date,
                        entry[END_DATE_KEY],
                        entry.get(GAS_KEY, {}),
                        entry.get(PDF_URL_KEY, ""),
                    )
                )

    logging.info(
        f"Backfill process complete. Total entries: {len(sorted_history)}. New entries added: {new_entries_count}"
    )


if __name__ == "__main__":
    backfill()