import requests
from urllib.parse import quote

def get_ols_disease_info(disease_name, ontologies=["mondo", "doid", "efo", "ncit", "ordo"]):
    exact_results = []
    similar_results = []

    for ontology in ontologies:
        url = "https://www.ebi.ac.uk/ols/api/search"
        exact_params = {
            "q": disease_name,
            "ontology": ontology,
            "type": "class",
            "exact": "true",
            "size": 1
        }
        similar_params = {
            "q": disease_name,
            "ontology": ontology,
            "type": "class",
            "exact": "false",
            "size": 5
        }

        try:
            # Exact match
            response = requests.get(url, params=exact_params)
            response.raise_for_status()
            data = response.json()
            if data.get("response", {}).get("docs"):
                doc = data["response"]["docs"][0]
                iri = doc.get("iri", "")
                term_id = iri.split("/")[-1] if iri else "N/A"
                label = doc.get("label", "N/A")
                ontology_url = f"https://www.ebi.ac.uk/ols/ontologies/{ontology}/terms?iri={quote(iri)}"

                exact_results.append({
                    "ontology": ontology.upper(),
                    "label": label,
                    "id": term_id,
                    "url": ontology_url
                })

            # Similar matches
            response = requests.get(url, params=similar_params)
            response.raise_for_status()
            data = response.json()
            for doc in data.get("response", {}).get("docs", [])[:3]:
                iri = doc.get("iri", "")
                term_id = iri.split("/")[-1] if iri else "N/A"
                label = doc.get("label", "N/A")
                if any(e['id'] == term_id for e in exact_results):
                    continue
                ontology_url = f"https://www.ebi.ac.uk/ols/ontologies/{ontology}/terms?iri={quote(iri)}"
                similar_results.append({
                    "ontology": ontology.upper(),
                    "label": label,
                    "id": term_id,
                    "url": ontology_url
                })

        except Exception as e:
            return f"OLS error for {ontology.upper()}: {e}"

    return exact_results, similar_results


def get_uniprot_disease_info(disease_name, limit=5):
    url = "https://rest.uniprot.org/diseases/search"
    params = {
        "query": disease_name,
        "fields": "id,name",
        "size": limit
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        results = []
        for entry in data.get("results", [])[:limit]:
            results.append({
                "id": entry.get("id"),
                "name": entry.get("name", "N/A"),
                "url": f"https://www.uniprot.org/diseases/{entry.get('id')}"
            })

        return results
    except Exception as e:
        return f"UniProt error: {e}"


def format_combined_output(disease_name, ols_exact, ols_similar, uniprot_matches):
    lines = []
    lines.append("=" * 90)
    lines.append(f"DISEASE SEARCH RESULTS FOR: {disease_name}")
    lines.append("=" * 90)

    # OLS Exact
    lines.append("\nOLS EXACT MATCHES:")
    if ols_exact:
        for res in ols_exact:
            lines.append(f"[{res['ontology']}] {res['id']}")
            lines.append(f"  Label: {res['label']}")
            lines.append(f"  Link : {res['url']}\n")
    else:
        lines.append("  No exact matches found.")

    # OLS Similar
    lines.append("\nOLS SIMILAR MATCHES:")
    if ols_similar:
        grouped = {}
        for item in ols_similar:
            grouped.setdefault(item["ontology"], []).append(item)
        for ont in ["MONDO", "DOID", "EFO", "NCIT", "ORDO"]:
            if ont in grouped:
                lines.append(f"\n  {ont}:")
                for res in grouped[ont]:
                    lines.append(f"    {res['id']} - {res['label']}")
                    lines.append(f"      Link: {res['url']}")
    else:
        lines.append("  No similar matches found.")

    # UniProt
    lines.append("\nUNIPROT MATCHES:")
    if isinstance(uniprot_matches, str):
        lines.append(f"  {uniprot_matches}")
    elif uniprot_matches:
        for res in uniprot_matches:
            lines.append(f"  {res['id']}: {res['name']}")
            lines.append(f"    Link: {res['url']}")
    else:
        lines.append("  No UniProt disease matches found.")

    lines.append("=" * 90)
    return "\n".join(lines)


def search(disease_name):
    if not disease_name:
        return "Please enter a disease name."

    ols_result = get_ols_disease_info(disease_name)
    if isinstance(ols_result, str):
        return ols_result
    ols_exact, ols_similar = ols_result

    uniprot_result = get_uniprot_disease_info(disease_name)

    return format_combined_output(disease_name, ols_exact, ols_similar, uniprot_result)


# Standalone CLI run
if __name__ == "__main__":
    disease_input = input("Enter disease name: ").strip()
    if disease_input:
        result = search(disease_input)
        print(result)
    else:
        print("No input provided.")
