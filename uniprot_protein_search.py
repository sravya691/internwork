import requests

class UniProtProteinSearcher:
    def search(self, keyword, max_results=10):
        """Search UniProt by protein name keyword."""
        if not keyword:
            print("Please provide a valid search keyword.")
            return []

        url = "https://rest.uniprot.org/uniprotkb/search"
        params = {
            "query": f'protein_name:"{keyword}"',
            "fields": "accession,protein_name,gene_names,organism_name",
            "format": "json",
            "size": max_results
        }

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            return data.get("results", [])
        except requests.RequestException as e:
            print(f"UniProt API error: {e}")
            return []

    def print_results(self, results):
        """Pretty print UniProt protein search results."""
        print(self.format_results(results))

    def format_results(self, results):
        """Return a formatted string of UniProt search results."""
        if not results:
            return "No results found."

        output = []
        for entry in results:
            accession = entry.get("primaryAccession", "N/A")
            protein_desc = entry.get("proteinDescription", {}).get("recommendedName", {})
            protein_full_name = protein_desc.get("fullName", {}).get("value", "N/A")

            genes = entry.get("genes", [])
            gene_name = "N/A"
            if genes and "geneName" in genes[0]:
                gene_name = genes[0]["geneName"].get("value", "N/A")

            organism = entry.get("organism", {}).get("scientificName", "N/A")
            uniprot_link = f"https://www.uniprot.org/uniprotkb/{accession}/entry"

            output.append(f"Accession: {accession}")
            output.append(f"Protein Name: {protein_full_name}")
            output.append(f"Gene Name: {gene_name}")
            output.append(f"Organism: {organism}")
            output.append(f"UniProt Link: {uniprot_link}")
            output.append("-" * 40)

        return "\n".join(output)


def main():
    print("UniProt Protein Search Tool")
    print("=" * 40)

    searcher = UniProtProteinSearcher()

    while True:
        keyword = input("\nEnter protein name or keyword (or 'q' to quit): ").strip()
        if keyword.lower() in ['q', 'quit', 'exit']:
            print("Goodbye.")
            break

        results = searcher.search(keyword)
        print(f"\nTop UniProt results for '{keyword}':\n")
        searcher.print_results(results)


if __name__ == "__main__":
    main()
