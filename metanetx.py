from SPARQLWrapper import SPARQLWrapper, JSON
from rapidfuzz.fuzz import ratio
import re

def extract_compounds_from_expression(expression):
    separators = [
        '→', '⟶', '->', '⇒', '⇆', '⇌', '↔', '+', '＋', '⟷', '|', '/', '\\', ',', ';', '⟨', '⟩', '[', ']', '(', ')',
    ]
    for sep in separators:
        expression = expression.replace(sep, '|')

    compounds = []
    for part in expression.split('|'):
        part = part.strip()
        if part:
            part = re.sub(r'^\d+\s*', '', part)  # remove leading stoichiometric coefficients
            part = re.sub(r'\s*(aq|s|l|g)\s*$', '', part)  # remove phase
            part = part.strip()
            if part and len(part) > 1:
                compounds.append(part)

    seen = set()
    unique_compounds = []
    for c in compounds:
        key = c.lower()
        if key not in seen:
            seen.add(key)
            unique_compounds.append(c)
    return unique_compounds

def normalize_compound_name(name):
    subscript_map = {'₀': '0', '₁': '1', '₂': '2', '₃': '3', '₄': '4', '₅': '5', '₆': '6', '₇': '7', '₈': '8', '₉': '9'}
    superscript_map = {'⁰': '0', '¹': '1', '²': '2', '³': '3', '⁴': '4', '⁵': '5', '⁶': '6', '⁷': '7', '⁸': '8', '⁹': '9', '⁺': '+', '⁻': '-'}
    name = name or ""
    for u, r in {**subscript_map, **superscript_map}.items():
        name = name.replace(u, r)
    name = name.replace('–', '-').replace('—', '-').replace('’', "'").replace('‘', "'")
    return name.strip()

def run_query(compound_name, use_contains=False):
    endpoint_url = "https://rdf.metanetx.org/sparql"
    sparql = SPARQLWrapper(endpoint_url)
    filter_clause = (
        f'FILTER(CONTAINS(LCASE(?comment), "{compound_name.lower()}"))'
        if use_contains else
        f'FILTER(LCASE(?comment) = "{compound_name.lower()}")'
    )
    query = f"""
    PREFIX mnx: <https://rdf.metanetx.org/schema/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?metabolite ?label ?comment ?reference
    WHERE {{
        ?metabolite a mnx:CHEM .
        ?metabolite rdfs:label ?label .
        ?metabolite rdfs:comment ?comment .
        {filter_clause}
        ?metabolite mnx:chemRefer ?reference .
    }}
    """
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    try:
        results = sparql.query().convert()
        return results.get("results", {}).get("bindings", [])
    except Exception as e:
        return f"SPARQL query failed: {e}"

def get_external_refs(mnx_id):
    query = f"""
    PREFIX mnx: <https://rdf.metanetx.org/schema/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?xref
    WHERE {{
        ?metabolite a mnx:CHEM .
        ?metabolite rdfs:comment '{mnx_id}' .
        ?metabolite mnx:chemXref ?xref
    }}
    """
    sparql = SPARQLWrapper("https://rdf.metanetx.org/sparql")
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    try:
        results = sparql.query().convert()
        return [r["xref"]["value"] for r in results["results"]["bindings"]]
    except Exception as e:
        return []

def search(compound_input):
    if not compound_input:
        return None

    results = []
    
    # If compound_input is a chemical expression, extract compounds and process each
    if any(x in compound_input for x in ['→', '⟶', '->', '⇒', '⇌', '+']):
        compounds = extract_compounds_from_expression(compound_input)
        for comp in compounds:
            result = search(comp)  # Recursive call for each compound
            if result:
                results.append(f"\nResult for '{comp}':\n{result}")
            else:
                results.append(f"\nNo matches found for '{comp}'.")
        return "\n" + "\n" + ("-" * 60 + "\n").join(results)

    # Single compound handling starts here
    normalized_input = normalize_compound_name(compound_input)
    output = []

    exact_matches = run_query(normalized_input, use_contains=False)
    if isinstance(exact_matches, str):  # error message returned
        return exact_matches

    if exact_matches:
        result = exact_matches[0]
        mnx_id = result.get('comment', {}).get('value', 'N/A')
        output.append(f"Exact match for '{compound_input}':")
        output.append(f"  Label     : {result.get('label', {}).get('value', 'N/A')}")
        output.append(f"  MNX ID    : {mnx_id}")
        output.append(f"  URI       : {result.get('metabolite', {}).get('value', 'N/A')}")
        output.append(f"  Reference : {result.get('reference', {}).get('value', 'N/A')}")
        
        xrefs = get_external_refs(mnx_id)
        if xrefs:
            output.append("\nExternal References:")
            for xref in xrefs:
                output.append(f" - {xref}")
        else:
            output.append("No external references found.")
        return "\n".join(output)

    # No exact matches; try partial matches
    partial_matches = run_query(normalized_input, use_contains=True)
    if isinstance(partial_matches, str):
        return partial_matches

    partial_matches = [
        r for r in partial_matches
        if r.get("comment", {}).get("value", "").lower() != normalized_input.lower()
    ]

    if partial_matches:
        output.append(f"No exact match for '{compound_input}'. Partial matches:")
        scored = []
        for r in partial_matches:
            name = r.get("comment", {}).get("value", "")
            sim = ratio(name.lower(), normalized_input.lower())
            scored.append((sim, r))

        scored = sorted(scored, key=lambda x: -x[0])[:5]
        for i, (score, r) in enumerate(scored, 1):
            output.append(f"\n{i}. Similarity: {round(score)}%")
            output.append(f"   Label     : {r.get('comment', {}).get('value', 'N/A')}")
            output.append(f"   MNX ID    : {r.get('label', {}).get('value', 'N/A')}")
            output.append(f"   Reference : {r.get('reference', {}).get('value', 'N/A')}")
        return "\n".join(output)

    return None  # No matches at all


if __name__ == "__main__":
    user_input = input("Enter a compound name or chemical reaction: ").strip()
    if any(x in user_input for x in ['→', '⟶', '->', '⇒', '+']):
        compounds = extract_compounds_from_expression(user_input)
        for comp in compounds:
            result = search(comp)
            if result:
                print("\n" + result)
                print("-" * 60)
            else:
                print(f"\nNo matches found for '{comp}'.\n" + "-"*60)
    else:
        result = search(user_input)
        if result:
            print(result)
        else:
            print(f"No matches found for '{user_input}'.")
