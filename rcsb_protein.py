import requests

class RCSBProteinRetriever:
    def search(self, query):
        if not query:
            return "❌ Search term cannot be empty."

        if query.isupper():
            attribute = "chem_comp.name"
            service = "text_chem"
            operator = "exact_match"
        else:
            attribute = "struct.title"
            service = "text"
            operator = "contains_phrase"

        search_query = {
            "query": {
                "type": "terminal",
                "label": service,
                "service": service,
                "parameters": {
                    "attribute": attribute,
                    "operator": operator,
                    "negation": False,
                    "value": query
                }
            },
            "return_type": "entry",
            "request_options": {
                "paginate": {"start": 0, "rows": 10},
                "results_content_type": ["experimental"],
                "sort": [{"sort_by": "score", "direction": "desc"}],
                "scoring_strategy": "combined"
            }
        }

        try:
            response = requests.post("https://search.rcsb.org/rcsbsearch/v2/query", json=search_query)
            response.raise_for_status()
            data = response.json()
            results = data.get("result_set", [])
            if not results:
                return []

            output = []
            for r in results:
                pdb_id = r.get("identifier", "N/A")
                structure_link = f"https://www.rcsb.org/structure/{pdb_id}"
                summary_url = f"https://data.rcsb.org/rest/v1/core/entry/{pdb_id}"

                try:
                    title_resp = requests.get(summary_url)
                    title_resp.raise_for_status()
                    title = title_resp.json().get("struct", {}).get("title", "No title available")
                except:
                    title = "No title available"

                output.append({
                    "pdb_id": pdb_id,
                    "title": title,
                    "link": structure_link
                })

            return output

        except Exception as e:
            return f"❌ RCSB Search Error: {e}"

    def print_results(self, results):
        if isinstance(results, str):
            print(results)
        elif not results:
            print("No structures found.")
        else:
            print("\nTop Matching Structures from RCSB PDB:\n")
            for i, entry in enumerate(results, 1):
                print(f"{i:>2}. PDB ID   : {entry['pdb_id']}")
                print(f"    Title    : {entry['title']}")
                print(f"    Link     : {entry['link']}\n")

    def format_results(self, results):
        """Format RCSB search results as a readable string."""
        if isinstance(results, str):
            return results
        elif not results:
            return "No structures found."

        lines = ["\nTop Matching Structures from RCSB PDB:\n"]
        for i, entry in enumerate(results, 1):
            lines.append(f"{i:>2}. PDB ID   : {entry['pdb_id']}")
            lines.append(f"    Title    : {entry['title']}")
            lines.append(f"    Link     : {entry['link']}\n")
        return "\n".join(lines)

