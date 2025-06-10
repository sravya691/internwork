import streamlit as st # type: ignore
import concurrent.futures
import threading
import time

# Import your main module components
import disease
import gene_protein
import cellucose
import kegg
import metanetx
import zooma_ontology
import rnacentral
import bioportal_obi
import organelle_go
import pmid_variants
import rcsb_protein
import gbif_species
import uniprot_protein_search


# Initialize module instances
zooma_instance = zooma_ontology.ZoomaRetriever()
rnacentral_instance = rnacentral.RNACentralGenomeRetriever()
gene_protein_instance = gene_protein.GeneProteinRetriever()
organelle_instance = organelle_go.OrganelleGO()
pmid_instance = pmid_variants.PMIDVariantRetriever()
rcsb_instance = rcsb_protein.RCSBProteinRetriever()
gbif_instance = gbif_species.GBIFSpeciesSearcher()
uniprot_instance = uniprot_protein_search.UniProtProteinSearcher()

modules = {
    "Disease": disease,
    "OrganelleGO": organelle_instance,
    "Cellosaurus": cellucose,
    "KEGG": kegg,
    "MetaNetX": metanetx,
    "Zooma_Ontology": zooma_instance,
    "RNAcentral_Genome": rnacentral_instance,
    "BioPortal_OBI": bioportal_obi.BioPortalOBIRetriever(),
    "gene_protein": gene_protein_instance,
    "PMID_Variants": pmid_instance,
    "RCSB_Protein": rcsb_instance,
    "UniProt": uniprot_instance,
    "GBIF": gbif_instance
}

print_lock = threading.Lock()
completed_count = 0

def map_input_to_modules(annotation_type):
    annotation_type = annotation_type.lower()
    mapping = {
        "disease": ["Disease"],
        "gene": ["RNAcentral_Genome", "gene_protein"],
        "organelle": ["OrganelleGO"],
        "variant": ["PMID_Variants"],
        "rna": ["RNAcentral_Genome"],
        "cell line": ["Cellosaurus"],
        "experimental_reac": ["BioPortal_OBI"],
        "cell": ["Cellosaurus"],
        "metabolite": ["KEGG", "MetaNetX"],
        "compound": ["KEGG", "MetaNetX"],
        "protein": ["KEGG", "Zooma_Ontology", "MetaNetX", "RCSB_Protein", "UniProt"],
        "ontology": ["Zooma_Ontology"],
        "annotation": ["Zooma_Ontology"],
        "drug": ["KEGG", "MetaNetX"],
        "reaction": ["MetaNetX"],
        "pathway": ["KEGG"],
        "species": ["GBIF"],
        "structure": ["RCSB_Protein"]
    }
    return {mod: modules[mod] for mod in mapping.get(annotation_type, [])}

def search_module(name, module, compound_name, annotation):
    global completed_count
    try:
        if name == "BioPortal_OBI":
            result = module.search(compound_name)
        elif name == "KEGG":
            result = module.search(compound_name, annotation)
        elif hasattr(module, "search"):
            result = module.search(compound_name)
        else:
            result = None

        with print_lock:
            completed_count += 1
            result_output = f"{'=' * 50}\nRESULT #{completed_count} - Module: {name}\n{'=' * 50}\n"

            if result:
                if name == "Zooma_Ontology":
                    result_output += zooma_instance.format_results(result)
                elif name == "KEGG":
                    result_output += kegg.format_results(result)
                elif name == "GBIF":
                    result_output += module.format_results(result)
                elif name == "UniProt":
                    result_output += uniprot_instance.format_results(result)
                elif name == "RCSB_Protein":
                    result_output += rcsb_instance.format_results(result)
                elif name == "BioPortal_OBI":
                    result_output += module.format_results(result)

                elif isinstance(result, (list, dict)):
                    items = result if isinstance(result, list) else [result]
                    for item in items:
                        result_output += f"  • {item}\n"
                else:
                    result_output += f"  {result}\n"
            else:
                result_output += "  No results found.\n"

            result_output += f"{'=' * 50}\n"
            return result_output

    except Exception as e:
        with print_lock:
            completed_count += 1
            return f"\n ERROR #{completed_count} - Module: {name}\n   Error: {e}\n"

def search_all_parallel_streamlit(compound_name, selected_modules, annotation, per_module_timeout=10):
    global completed_count
    completed_count = 0
    result_containers = {}

    # Create placeholders for each module
    for name in selected_modules:
        result_containers[name] = st.empty()

    with concurrent.futures.ThreadPoolExecutor(max_workers=min(len(selected_modules), 8)) as executor:
        future_to_name = {
            executor.submit(search_module, name, mod, compound_name, annotation): name
            for name, mod in selected_modules.items()
        }

        for future in concurrent.futures.as_completed(future_to_name):
            name = future_to_name[future]
            try:
                result = future.result(timeout=per_module_timeout)
            except concurrent.futures.TimeoutError:
                result = f"\nTIMEOUT - Module: {name}\n   Skipped due to timeout.\n"
            except Exception as e:
                result = f"\nERROR - Module: {name}\n   Error: {e}\n"

            # Update the placeholder with result
            result_containers[name].text(result)


def main():
    st.title("Multi-Database Parallel Search Tool")
    st.markdown("This interface allows searching multiple biological databases in parallel.")

    compound = st.text_input("Enter a biological entity")
    annotation = st.text_input("Enter its annotation type (e.g. metabolite, gene, disease)")

    if st.button("Search"):
        if not compound or not annotation:
            st.warning("Please provide both entity and annotation type.")
        else:
            st.write(f"Searching based on annotation type: '{annotation}'")

            selected_modules = map_input_to_modules(annotation)
            if not selected_modules:
                st.write("No matching modules found for the annotation type. Searching all modules instead...")
                selected_modules = modules

            start = time.time()
            search_all_parallel_streamlit(compound, selected_modules, annotation)  # ✅ Streaming
            end = time.time()

            st.success(f"Search completed in {round(end - start, 2)} seconds")

if __name__ == "__main__":
    main()
