import requests
import json

def get_cell_line_details(search_term):
    base_url = "https://api.cellosaurus.org/search/cell-line"
    params = {
        "q": search_term,
        "fields": "id,sy,ac,dr,cc,ox,sx,ag,ca,di,ch,rx,ref,oi,hi,dt",
        "format": "json"
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()
        results = data.get("Cellosaurus", {}).get("cell-line-list", [])

        if not results:
            return {"status": "No results found", "data": None}

        
        first_match = results[0]
        first_accession = next((a["value"] for a in first_match.get("accession-list", []) if a["type"] == "primary"), None)

        detailed_result = {
            "accession": first_accession,
            "url": f"https://www.cellosaurus.org/{first_accession}" if first_accession else None,
            "names": first_match.get("name-list", []),
            "category": first_match.get("category", ""),
            "sex": first_match.get("sex", ""),
            "age": first_match.get("age", ""),
            "species": first_match.get("species-list", []),
            "characteristics": [c.get("value", "") for c in first_match.get("comment-list", []) if c.get("category") == "Characteristics"],
            "derived_from": first_match.get("derived-from", []),
            "references": first_match.get("reference-list", []),
            "xrefs": first_match.get("xref-list", []),
            "created": first_match.get("created", ""),
            "last_updated": first_match.get("last-updated", ""),
            "entry_version": first_match.get("entry-version", "")
        }

        # Process remaining matches with minimal info (limit to 5)
        partial_matches = []
        for match in results[1:6]:  
            accession = next((a["value"] for a in match.get("accession-list", []) if a["type"] == "primary"), None)
            identifier = next((n["value"] for n in match.get("name-list", []) if n["type"] == "identifier"), "")

            partial_matches.append({
                "accession": accession,
                "identifier": identifier,
                "url": f"https://www.cellosaurus.org/{accession}" if accession else None
            })

        return {
            "status": "success",
            "total_results": len(results),
            "first_match_details": detailed_result,
            "partial_matches": partial_matches
        }

    except requests.RequestException as e:
        return {"status": "error", "message": f"Request error: {e}"}
    except Exception as e:
        return {"status": "error", "message": f"Error: {e}"}

def format_output(result):
    """Format the result for better readability"""
    if result["status"] != "success":
        return result["status"] + (f": {result.get('message', '')}" if result.get('message') else "")

    output = []
    output.append(f"=== SEARCH RESULTS ({result['total_results']} found) ===\n")

    # First match details
    details = result["first_match_details"]
    output.append("FIRST MATCH (Full Details):")
    output.append(f"Accession: {details['accession']}")
    output.append(f"URL: {details['url']}")

    if details['names']:
        identifier = next((n['value'] for n in details['names'] if n['type'] == 'identifier'), '')
        if identifier:
            output.append(f"Name: {identifier}")

    if details['category']:
        output.append(f"Category: {details['category']}")
    if details['sex']:
        output.append(f"Sex: {details['sex']}")
    if details['age']:
        output.append(f"Age: {details['age']}")

    if details['species']:
        species_info = details['species'][0] if details['species'] else {}
        if species_info.get('label'):
            output.append(f"Species: {species_info['label']}")

    if details['characteristics']:
        output.append("Characteristics:")
        for char in details['characteristics']:
            output.append(f"  • {char}")

    if details['derived_from']:
        derived = details['derived_from'][0]
        output.append(f"Derived from: {derived.get('label', '')} ({derived.get('accession', '')})")

    if details['created']:
        output.append(f"Created: {details['created']}")
    if details['last_updated']:
        output.append(f"Last Updated: {details['last_updated']}")

    # Partial matches
    if result["partial_matches"]:
        output.append(f"\nOTHER MATCHES ({len(result['partial_matches'])} shown):")
        for i, match in enumerate(result["partial_matches"], 2):
            output.append(f"{i}. {match['identifier']} | {match['accession']} | {match['url']}")

    return "\n".join(output)

def search(term):
    """Main search function"""
    if not term:
        return "Please provide a search term."

    result = get_cell_line_details(term)
    return format_output(result)

# Standalone test mode
if __name__ == "__main__":
    user_input = input("Enter search term: ").strip()
    result = search(user_input)
    print(result)