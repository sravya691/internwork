# rnacentral.py
import requests

class RNACentralGenomeRetriever:
    def __init__(self, max_matches=3, verbose=False, max_pages=None):
        self.api_url = "https://rnacentral.org/api/v1/genomes/?format=json"
        self.max_matches = max_matches
        self.verbose = verbose
        self.max_pages = max_pages

    def search(self, genome_name):
        results = []
        url = self.api_url
        genome_name_lower = genome_name.lower()
        page_count = 0

        while url:
            if self.verbose:
                print(f"Fetching: {url}")
            response = requests.get(url)
            if response.status_code != 200:
                raise Exception(f"API error {response.status_code}")

            data = response.json()
            found_on_this_page = False

            for genome in data["results"]:
                common_name = genome.get("common_name", "").lower()
                if genome_name_lower in common_name:
                    results.append(genome)
                    found_on_this_page = True
                    if len(results) >= self.max_matches:
                        return results

            if not found_on_this_page:
                break

            page_count += 1
            if self.max_pages and page_count >= self.max_pages:
                break

            url = data.get("next")

        return results

    def format_results(self, results):
        if not results:
            return "❌ No matches found in RNAcentral Genome."

        output_lines = []
        for genome in results:
            output_lines.append("=" * 60)
            output_lines.append("🧬 From RNAcentral Genome module:")
            output_lines.append("-------------------------------------")
            output_lines.append(f"Common Name                : {genome.get('common_name')}")
            output_lines.append(f"Assembly ID                : {genome.get('assembly_id')}")
            output_lines.append(f"Assembly Full Name         : {genome.get('assembly_full_name')}")
            output_lines.append(f"GCA Accession              : {genome.get('gca_accession')}")
            output_lines.append(f"Taxonomy ID                : {genome.get('taxid')}")
            output_lines.append(f"Ensembl URL Path           : {genome.get('ensembl_url')}")
            output_lines.append(f"Division                   : {genome.get('division')}")
            output_lines.append(f"Subdomain                  : {genome.get('subdomain')}")
            output_lines.append(f"Human-readable Ensembl URL: {genome.get('human_readable_ensembl_url')}")
            output_lines.append("=" * 60)

        return "\n".join(output_lines)
