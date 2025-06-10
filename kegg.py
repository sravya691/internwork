import requests
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache

KEGG_DATABASES = {
    "gene": ["genes"],
    "protein": ["enzyme", "ko"],
    "metabolite": ["compound", "reaction", "rclass"],
    "compound": ["compound", "drug", "reaction"],
    "pathway": ["pathway", "module", "network"],
    "drug": ["drug", "disease"],
    "disease": ["disease"],
    "variant": ["variant"],
    "species": ["genome"],
    "ontology": ["brite"],
}

@lru_cache(maxsize=1000)
def cached_find_query(db, query):
    url = f"http://rest.kegg.jp/find/{db}/{query}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.text.strip()
    return ""

@lru_cache(maxsize=1000)
def cached_get_entry(entry_id):
    url = f"http://rest.kegg.jp/get/{entry_id}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.text.strip()
    return ""

def fetch_kegg_results(db, query, k=5):
    try:
        result_text = cached_find_query(db, query)
        if result_text:
            lines = result_text.split('\n')[:k]
            return (db, lines)
        return (db, [])
    except Exception as e:
        return (db, [f"Error querying KEGG → {db}: {e}"])

def get_kegg_entry_details(entry_id):
    try:
        details = cached_get_entry(entry_id)
        if details:
            return f"\nDetails for {entry_id}\n" + "=" * 60 + "\n" + details
        return f"No details found for {entry_id}"
    except Exception as e:
        return f"Error fetching entry details: {e}"

def search(compound_name, annotation_type):
    """Main entry point. Searches only relevant KEGG databases for a given annotation type."""
    annotation_type = annotation_type.lower() if annotation_type else ""
    relevant_dbs = KEGG_DATABASES.get(annotation_type, [])
    results = []

    if not relevant_dbs:
        return [("KEGG", [f"No relevant KEGG databases found for annotation type: '{annotation_type}'"])]
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(fetch_kegg_results, db, compound_name) for db in relevant_dbs]
        for future in futures:
            db, lines = future.result()
            if lines:
                results.append((db, lines))
    return results

def print_results(result_list):
    if isinstance(result_list, list):
        for db, lines in sorted(result_list):
            if not lines:
                continue

            print(f"\nKEGG → {db.upper()}")
            print("-" * (12 + len(db)))

            for line in lines:
                if '\t' in line:
                    entry_id, description = line.split('\t', 1)
                    primary_name = description.split(";")[0].strip()
                    print(f"  • {entry_id:<12} {primary_name}")
                else:
                    print(f"  • {line.strip()}")


def format_results(result_list):
    if isinstance(result_list, str):
        return result_list

    if not result_list:
        return "No KEGG results found."

    output = []
    for db, lines in sorted(result_list):
        if not lines:
            continue

        output.append(f"\nKEGG → {db.upper()}")
        output.append("-" * (12 + len(db)))

        for line in lines:
            if '\t' in line:
                entry_id, description = line.split('\t', 1)
                primary_name = description.split(";")[0].strip()
                output.append(f"  • {entry_id:<12} {primary_name}")
            else:
                output.append(f"  • {line.strip()}")

    return "\n".join(output)
