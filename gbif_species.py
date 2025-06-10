import requests

class GBIFSpeciesSearcher:
    def search(self, name, limit=10):
        """Search GBIF species by name and return results."""
        url = "https://api.gbif.org/v1/species/search"
        params = {
            "q": name,
            "limit": limit
        }
        try:
            resp = requests.get(url, params=params)
            resp.raise_for_status()
            return resp.json().get("results", [])
        except requests.RequestException as e:
            return {"error": f"GBIF API error: {e}"}

    def format_results(self, results):
        """Return a formatted string of search results."""
        if isinstance(results, dict) and "error" in results:
            return f"❌ {results['error']}"
        if not results:
            return "No results found."

        lines = []
        for entry in results:
            lines.append(f"usageKey: {entry.get('key')}")
            lines.append(f"  scientificName:  {entry.get('scientificName')}")
            lines.append(f"  canonicalName:   {entry.get('canonicalName')}")
            lines.append(f"  rank:            {entry.get('rank')}")
            lines.append(f"  status:          {entry.get('taxonomicStatus')}")
            lines.append(f"  kingdom:         {entry.get('kingdom')}")
            lines.append(f"  phylum:          {entry.get('phylum')}")
            lines.append(f"  class:           {entry.get('class')}")
            lines.append(f"  order:           {entry.get('order')}")
            lines.append(f"  family:          {entry.get('family')}")
            lines.append(f"  genus:           {entry.get('genus')}")
            lines.append(f"  species:         {entry.get('species')}")
            lines.append("-" * 40)
        return "\n".join(lines)

    def print_results(self, results):
        """Print formatted search results."""
        print(self.format_results(results))


# CLI Example
if __name__ == "__main__":
    gbif = GBIFSpeciesSearcher()
    print("GBIF Species Search Tool")
    while True:
        query = input("\nEnter species name to search (or 'q' to quit): ").strip()
        if query.lower() in ["q", "quit", "exit"]:
            print("Exiting.")
            break
        results = gbif.search(query, limit=10)
        gbif.print_results(results)
