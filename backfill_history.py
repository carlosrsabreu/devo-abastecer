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
)
from functions import (
    replace_gas_keys_names,
    retrieve_week_by_date,
    return_next_week_by_date,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

HISTORY_JSON = "history/gas_info_history.json"
HISTORY_CSV = "history/gas_info_history.csv"

# Shared resources
all_history = {}
history_lock = Lock()
new_entries_count = 0


def process_pdf(year, pdf_filename, pdf_date):
    global new_entries_count
    start_date, end_date = retrieve_week_by_date(return_next_week_by_date(pdf_date))

    with history_lock:
        if start_date in all_history:
            # Check if any data is missing
            entry = all_history[start_date]
            gas_data = entry.get(GAS_KEY, {})
            if (
                GASOLINE_95 in gas_data
                and DIESEL in gas_data
                and COLORED_DIESEL in gas_data
                and GASOLINE_98 in gas_data
                and PDF_URL_KEY in entry
                and entry[PDF_URL_KEY]
            ):
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
                gas_data[k] = float(v.replace(",", "."))
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
    if os.path.exists(HISTORY_JSON):
        with open(HISTORY_JSON, "r") as f:
            all_history = json.load(f)
            for k, v in all_history.items():
                if "Fuel" in v and GAS_KEY not in v:
                    v[GAS_KEY] = v.pop("Fuel")

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
                entry = all_history.get(start_date)
                is_incomplete = False
                if entry:
                    gas_data = entry.get(GAS_KEY, {})
                    is_incomplete = not (
                        GASOLINE_95 in gas_data
                        and DIESEL in gas_data
                        and COLORED_DIESEL in gas_data
                        and GASOLINE_98 in gas_data
                        and PDF_URL_KEY in entry
                        and entry[PDF_URL_KEY]
                    )
                is_missing = start_date not in all_history or is_incomplete

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
            with open(HISTORY_JSON, "w") as f:
                json.dump(sorted_history, f, indent=2, ensure_ascii=False)

    # Final update of both JSON and CSV
    with history_lock:
        sorted_history = dict(sorted(all_history.items()))
        with open(HISTORY_JSON, "w") as f:
            json.dump(sorted_history, f, indent=2, ensure_ascii=False)

        with open(HISTORY_CSV, "w") as f:
            f.write(
                "start_date,end_date,gasolina_IO95,gasoleo_rodoviario,gasoleo_colorido_marcado,gasolina_IO98,pdf_url\n"
            )
            for start_date in sorted(sorted_history.keys()):
                entry = sorted_history[start_date]
                gd = entry.get(GAS_KEY, {})
                p95 = gd.get(GASOLINE_95, "")
                diesel = gd.get(DIESEL, "")
                colored = gd.get(COLORED_DIESEL, "")
                p98 = gd.get(GASOLINE_98, "")
                url = entry.get(PDF_URL_KEY, "")
                f.write(
                    f"{start_date},{entry[END_DATE_KEY]},{p95},{diesel},{colored},{p98},{url}\n"
                )

    logging.info(
        f"Backfill process complete. Total entries: {len(sorted_history)}. New entries added: {new_entries_count}"
    )


if __name__ == "__main__":
    backfill()
