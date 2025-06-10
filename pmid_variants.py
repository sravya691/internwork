# pmid_variants.py

import requests

class PMIDVariantRetriever:
    def search(self, pmid):
        if not pmid.isdigit():
            return "Please provide a valid numeric PMID."

        server = "https://rest.ensembl.org"
        ext = f"/variation/human/pmid/{pmid}?"

        try:
            response = requests.get(server + ext, headers={"Content-Type": "application/json"})
            response.raise_for_status()
        except requests.RequestException as e:
            return f"Request failed: {e}"

        data = response.json()
        if not data:
            return f"No variants found for PMID {pmid}."

        lines = [f"Variants associated with PMID {pmid}:", "-" * 50]
        for variant in data:
            var_name = variant.get('name', 'N/A')
            lines.append(f"Variant ID (rsID): {var_name}")
            lines.append(f"  Most severe consequence: {variant.get('most_severe_consequence', 'N/A')}")

            if 'mappings' in variant and variant['mappings']:
                mapping = variant['mappings'][0]
                lines.append(f"  Location: {mapping.get('location', 'N/A')}")
                lines.append(f"  Allele string: {mapping.get('allele_string', 'N/A')}")
            else:
                lines.append("  No mapping data found.")

            synonyms = variant.get('synonyms', [])
            lines.append(f"  Synonyms: {', '.join(synonyms) if synonyms else 'N/A'}")

            clinical = variant.get('clinical_significance', [])
            lines.append(f"  Clinical significance: {', '.join(clinical) if clinical else 'N/A'}")
            lines.append("-" * 50)

        return "\n".join(lines)
