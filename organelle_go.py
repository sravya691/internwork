# organelle_go.py

import requests

class OrganelleGO:
    def search(self, query, limit=10):
        if not query:
            return "Please enter a valid term (e.g., organelle, function, process)."

        url = "https://www.ebi.ac.uk/QuickGO/services/ontology/go/search"
        params = {
            "query": query,
            "limit": limit,
            "page": 1
        }

        try:
            response = requests.get(url, params=params, headers={"Accept": "application/json"})
            response.raise_for_status()
        except requests.RequestException as e:
            return f"Request failed: {e}"

        data = response.json()
        results = data.get("results", [])

        if not results:
            return "No results found."

        lines = [f"\nTop {len(results)} GO results for query: '{query}'\n"]
        for res in results:
            go_id = res.get("id")
            name = res.get("name")
            aspect = res.get("aspect", "N/A")
            go_url = f"https://www.ebi.ac.uk/QuickGO/term/{go_id}"
            lines.append(f"GO ID     : {go_id}  →  {go_url}")
            lines.append(f"Name      : {name}")
            lines.append(f"Aspect    : {aspect}")
            lines.append("-" * 60)

        return "\n".join(lines)
    
    def format_results(self, result):
        """Format the variant retrieval result as a string (pass-through for now)."""
        return result if isinstance(result, str) else str(result)

    def print_results(self, result):
        print(self.format_results(result))
