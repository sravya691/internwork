import requests
from concurrent.futures import ThreadPoolExecutor

class GeneProteinRetriever:
    def search(self, gene_symbol):
        gene_symbol = gene_symbol.strip().upper()
        gene_info = self.get_gene_info(gene_symbol)
        protein_info = self.get_protein_info(gene_symbol)

        result = []
        if gene_info:
            result.append(self.format_gene_output(gene_info))
        if protein_info:
            result.append(self.format_protein_output(protein_info))
        return "\n".join(result)

    def get_gene_info(self, gene_symbol):
        try:
            url = f"https://api.ncbi.nlm.nih.gov/datasets/v2/gene/symbol/{gene_symbol}/taxon/9606"
            headers = {"Accept": "application/json"}
            response = requests.get(url, headers=headers)
            if response.status_code != 200:
                return None
            data = response.json()
            if 'reports' not in data or not data['reports']:
                return None

            gene_report = data['reports'][0].get('gene', {})

            result = {
                'Gene ID': gene_report.get('gene_id', 'N/A'),
                'Symbol': gene_report.get('symbol', 'N/A'),
                'Full Name': gene_report.get('description', 'N/A'),
                'Gene Type': gene_report.get('type', 'N/A'),
                'Transcript Count': gene_report.get('transcript_count', 'N/A'),
                'Synonyms': ', '.join(gene_report.get('synonyms', [])) or 'N/A',
                'Chromosome Location': ', '.join(gene_report.get('chromosomes', [])) or 'N/A',
                'HGNC ID': gene_report.get('nomenclature_authority', {}).get('identifier', 'N/A') if gene_report.get('nomenclature_authority', {}).get('authority') == 'HGNC' else 'N/A',
                'OMIM ID': ', '.join(gene_report.get('omim_ids', [])) or 'N/A',
                'Ensembl ID': ', '.join(gene_report.get('ensembl_gene_ids', [])) or 'N/A',
                'Swiss-Prot Accession': ', '.join(gene_report.get('swiss_prot_accessions', [])) or 'N/A'
            }
            return result
        except:
            return None

    def get_protein_info(self, gene_name, limit=5):
        try:
            gc_url = "https://rest.uniprot.org/genecentric/search"
            gc_params = {"query": f"gene:{gene_name}", "fields": "accession,gene_name,proteome_id", "size": limit}
            gc_response = requests.get(gc_url, params=gc_params)
            if gc_response.status_code != 200:
                return None
            results = gc_response.json().get("results", [])[:limit]
            if not results:
                return None

            with ThreadPoolExecutor() as executor:
                return list(executor.map(self.fetch_protein_details, results))
        except:
            return None

    def fetch_protein_details(self, entry):
        try:
            protein_info = entry.get("canonicalProtein", {})
            accession = protein_info.get("id")
            gene = protein_info.get("geneName", "N/A")
            proteome_id = entry.get("proteomeId", "N/A")
            protein_url = f"https://rest.uniprot.org/uniprotkb/{accession}.json"
            protein_response = requests.get(protein_url)
            if protein_response.status_code == 200:
                protein_data = protein_response.json()
                protein_name = protein_data.get("proteinDescription", {}).get("recommendedName", {}).get("fullName", {}).get("value", "N/A")
            else:
                protein_name = "N/A"
            return {
                "Gene": gene,
                "Protein Name": protein_name,
                "Accession": accession,
                "Proteome ID": proteome_id,
                "Link": f"https://www.uniprot.org/uniprotkb/{accession}/entry"
            }
        except:
            return {"Error": "Failed to fetch protein detail."}

    def format_gene_output(self, gene_data):
        lines = ["=" * 50, "GENE INFORMATION", "=" * 50]
        for key, value in gene_data.items():
            lines.append(f"{key:<25}: {value}")
        lines.append("=" * 50)
        return "\n".join(lines)

    def format_protein_output(self, protein_data):
        if not protein_data:
            return "No protein data found."
        lines = ["PROTEIN INFORMATION (Top 5)", "=" * 50]
        for entry in protein_data:
            if "Error" in entry:
                lines.append(f"Error fetching protein: {entry['Error']}")
                continue
            lines.append(f"Gene             : {entry['Gene']}")
            lines.append(f"Protein Name     : {entry['Protein Name']}")
            lines.append(f"Accession        : {entry['Accession']}")
            lines.append(f"Proteome ID      : {entry['Proteome ID']}")
            lines.append(f"Link             : {entry['Link']}")
            lines.append("-" * 50)
        return "\n".join(lines)
    
    def format_results(self, result):
        """Format result string (already in printable format)."""
        return result if isinstance(result, str) else str(result)

    def print_results(self, result):
        print(self.format_results(result))

