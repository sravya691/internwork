# zooma_ontology.py

import requests
from typing import Dict, List, Any

class ZoomaRetriever:
    def __init__(self):
        self.base_url = "https://www.ebi.ac.uk/spot/zooma/v2/api"
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })

    def predict_annotation(self, property_value: str, property_type: str = None,
                           required_sources: List[str] = None,
                           preferred_sources: List[str] = None,
                           ontologies: List[str] = None) -> List[Dict[str, Any]]:
        url = f"{self.base_url}/services/annotate"
        params = {'propertyValue': property_value}

        if property_type:
            params['propertyType'] = property_type

        filter_parts = []
        if required_sources:
            filter_parts.append(f"required:[{','.join(required_sources)}]")
        if preferred_sources:
            filter_parts.append(f"preferred:[{','.join(preferred_sources)}]")
        if ontologies:
            filter_parts.append(f"ontologies:[{','.join(ontologies)}]")

        if filter_parts:
            params['filter'] = ','.join(filter_parts)

        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error making request: {e}")
            return []

    def extract_ontology_info(self, annotation_result: List[Dict]) -> Dict[str, Any]:
        if not annotation_result:
            return {"error": "No annotations found"}

        extracted_info = []

        for annotation in annotation_result:
            info = {
                "input_term": annotation.get("annotatedProperty", {}).get("propertyValue"),
                "property_type": annotation.get("annotatedProperty", {}).get("propertyType"),
                "confidence": annotation.get("confidence"),
                "semantic_tags": [],
                "accessions": [],
                "ontology_uris": [],
                "provenance": {},
                "derived_from": None
            }

            for tag in annotation.get("semanticTags", []):
                info["semantic_tags"].append(tag)
                info["ontology_uris"].append(tag)
                if "/" in tag:
                    info["accessions"].append(tag.split("/")[-1])

            provenance = annotation.get("provenance", {})
            if provenance:
                info["provenance"] = {
                    "source_name": provenance.get("source", {}).get("name"),
                    "source_type": provenance.get("source", {}).get("type"),
                    "source_uri": provenance.get("source", {}).get("uri"),
                    "evidence": provenance.get("evidence"),
                    "accuracy": provenance.get("accuracy"),
                    "generator": provenance.get("generator"),
                    "annotator": provenance.get("annotator")
                }

            derived = annotation.get("derivedFrom")
            if derived:
                info["derived_from"] = {
                    "uri": derived.get("uri"),
                    "original_property_value": derived.get("annotatedProperty", {}).get("propertyValue"),
                    "original_property_type": derived.get("annotatedProperty", {}).get("propertyType"),
                    "source_database": derived.get("provenance", {}).get("source", {}).get("name")
                }

            extracted_info.append(info)

        return {"annotations": extracted_info}

    def search(self, input_term: str) -> Dict[str, Any]:
        annotations = self.predict_annotation(property_value=input_term)
        return self.extract_ontology_info(annotations)

    def print_results(self, results: Dict[str, Any]):
        if "error" in results:
            print(f"Error: {results['error']}")
            return

        for i, annotation in enumerate(results.get("annotations", []), 1):
            print(f"\n=== Annotation {i} ===")
            print(f"Input Term: {annotation.get('input_term')}")
            print(f"Property Type: {annotation.get('property_type')}")
            print(f"Confidence: {annotation.get('confidence')}")

            print("\nOntology Information:")
            for j, (acc, uri) in enumerate(zip(annotation.get('accessions', []), annotation.get('ontology_uris', [])), 1):
                print(f"  {j}. Accession: {acc}")
                print(f"     URI: {uri}")

            provenance = annotation.get("provenance")
            if provenance:
                print("\nProvenance:")
                print(f"  Source: {provenance.get('source_name')} ({provenance.get('source_type')})")
                print(f"  Evidence: {provenance.get('evidence')}")
                print(f"  Generator: {provenance.get('generator')}")

            derived = annotation.get("derived_from")
            if derived:
                print("\nDerived From:")
                print(f"  Original Term: {derived.get('original_property_value')}")
                print(f"  Source Database: {derived.get('source_database')}")

    def format_results(self, results: Dict[str, Any]) -> str:
        if "error" in results:
            return f"Error: {results['error']}"

        output = []
        for i, annotation in enumerate(results.get("annotations", []), 1):
            output.append(f"\n=== Annotation {i} ===")
            output.append(f"Input Term: {annotation.get('input_term')}")
            output.append(f"Property Type: {annotation.get('property_type')}")
            output.append(f"Confidence: {annotation.get('confidence')}")

            output.append("\nOntology Information:")
            for j, (acc, uri) in enumerate(zip(annotation.get('accessions', []), annotation.get('ontology_uris', [])), 1):
                output.append(f"  {j}. Accession: {acc}")
                output.append(f"     URI: {uri}")

            provenance = annotation.get("provenance")
            if provenance:
                output.append("\nProvenance:")
                output.append(f"  Source: {provenance.get('source_name')} ({provenance.get('source_type')})")
                output.append(f"  Evidence: {provenance.get('evidence')}")
                output.append(f"  Generator: {provenance.get('generator')}")

            derived = annotation.get("derived_from")
            if derived:
                output.append("\nDerived From:")
                output.append(f"  Original Term: {derived.get('original_property_value')}")
                output.append(f"  Source Database: {derived.get('source_database')}")

        return "\n".join(output)
