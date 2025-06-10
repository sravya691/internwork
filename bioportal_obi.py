import requests

class BioPortalOBIRetriever:
    def __init__(self, api_key=None):
        self.api_key = api_key or "acd630fb-33b7-494e-9102-8da2e4e34222"
        self.base_url = "https://data.bioontology.org/search"

    def search(self, term, pagesize=10):
        if not term:
            return {"error": "Please enter a search term."}

        params = {
            "q": term,
            "ontologies": "OBI",
            "apikey": self.api_key,
            "pagesize": pagesize
        }

        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()

            results = []
            for result in data.get("collection", []):
                name = result.get("prefLabel", "N/A")
                full_id = result.get("@id", "")
                short_id = full_id.split("/")[-1].lower() if full_id else "N/A"
                link = full_id

                results.append({
                    "name": name,
                    "id": short_id,
                    "url": link
                })

            if not results:
                return {"error": "No results found."}

            return {"term": term, "results": results}

        except Exception as e:
            return {"error": f"BioPortal error: {e}"}

    def format_results(self, result):
        if "error" in result:
            return f"❌ {result['error']}\n"

        lines = []
        lines.append("=" * 80)
        lines.append(f"BIOPORTAL OBI SEARCH RESULTS FOR: {result['term']}")
        lines.append("=" * 80)

        for res in result["results"]:
            lines.append(f"Name : {res['name']}")
            lines.append(f"ID   : {res['id']}")
            lines.append(f"Link : {res['url']}")
            lines.append("-" * 40)

        return "\n".join(lines)

    def print_results(self, result):
        print(self.format_results(result))


# CLI Test
if __name__ == "__main__":
    retriever = BioPortalOBIRetriever()
    term = input("Enter query: ").strip()
    result = retriever.search(term)
    retriever.print_results(result)
