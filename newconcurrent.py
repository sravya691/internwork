import concurrent.futures
import disease
import gene_protein
import cellucose
import kegg
import metanetx
import zooma_ontology
import rnacentral
import threading
import time
import organelle_go,pmid_variants
import rcsb_protein
import gbif_species, uniprot_protein_search
from bioportal_obi import BioPortalOBIRetriever



# Initialize module instances
zooma_instance = zooma_ontology.ZoomaRetriever()
rnacentral_instance = rnacentral.RNACentralGenomeRetriever()
gene_protein_instance = gene_protein.GeneProteinRetriever() 
organelle_instance = organelle_go.OrganelleGO()
pmid_instance = pmid_variants.PMIDVariantRetriever()
rcsb_instance = rcsb_protein.RCSBProteinRetriever()
gbif_instance = gbif_species.GBIFSpeciesSearcher()
uniprot_instance = uniprot_protein_search.UniProtProteinSearcher()
bioportal_instance = BioPortalOBIRetriever()

modules = {
    "Disease": disease,
    "OrganelleGO": organelle_instance,
    "Cellosaurus": cellucose,
    "KEGG": kegg,
    "MetaNetX": metanetx,
    "Zooma_Ontology": zooma_instance,
    "BioPortal_OBI": bioportal_instance, 
    "RNAcentral_Genome": rnacentral_instance,
 
    "gene_protein":gene_protein_instance,
    "PMID_Variants": pmid_instance,
    "RCSB_Protein": rcsb_instance,
    "UniProt": uniprot_instance,
    "GBIF": gbif_instance
}

# Thread lock and counters
print_lock = threading.Lock()
completed_count = 0
total_searches = 0

def map_input_to_modules(annotation_type):
    """Map annotation category to corresponding module names."""
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
        "protein": ["KEGG", "Zooma_Ontology", "MetaNetX","RCSB_Protein","UniProt"],
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
                    result_output += module.format_results(result)
                elif name == "KEGG":
                    result_output += kegg.format_results(result)
                elif name == "GBIF":
                    result_output += module.format_results(result)
                elif name == "UniProt":
                    result_output += uniprot_instance.format_results(result)
                elif name == "RCSB_Protein":
                    result_output += rcsb_instance.format_results(result)
                elif name == "BioPortal_OBI":
                    result_output += module.format_results(result)  # ✅ format nicely
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

def search_all_parallel(compound_name, selected_modules, annotation, per_module_timeout=10):

    """Search all selected modules in parallel and display results as they come."""
    global completed_count, total_searches
    completed_count = 0
    total_searches = len(selected_modules)

    print(f"\nStarting parallel search for: '{compound_name}'")
    print(f"Searching across {total_searches} database(s)...\n")

    start_time = time.time()
    found_results = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=min(len(selected_modules), 8)) as executor:
        future_to_name = {
            executor.submit(search_module, name, mod, compound_name, annotation): name
            for name, mod in selected_modules.items()
        }


        for future in concurrent.futures.as_completed(future_to_name, timeout=None):
            name = future_to_name[future]
            try:
                # Apply timeout per future result (wrapped in try-except)
                result = future.result(timeout=per_module_timeout)

                if result and not result.strip().lower().startswith("error"):
                    found_results.append((name, result))


            except concurrent.futures.TimeoutError:
                with print_lock:
                    completed_count += 1
                    print(f"\nTIMEOUT #{completed_count} - Module: {name}")
                    print(f"   Skipped due to exceeding {per_module_timeout} second limit.\n")
            except Exception as e:
                with print_lock:
                    completed_count += 1
                    print(f"\n ERROR #{completed_count} - Module: {name}")
                    print(f"   Error: {e}\n")

    end_time = time.time()
    print(f"\nSearch completed in {round(end_time - start_time, 2)} seconds")

    return found_results


def main():
    """Main function to run the search application."""
    print("Multi-Database Parallel Search Tool")
    print("=" * 50)

    while True:
        try:
            # Input
            compound = input("\nEnter a biological entity (or 'quit' to exit): ").strip()
            if compound.lower() in ['quit', 'exit', 'q']:
                print("Goodbye.")
                break
            if not compound:
                print("Please enter a valid term.")
                continue

            annotation = input("Enter its annotation type (e.g. metabolite, gene, disease): ").strip()
            if not annotation:
                print("Please provide a valid annotation type.")
                continue

            # Step 1: Search in relevant modules only
            print(f"\nSearching based on annotation type: '{annotation}'")
            selected_modules = map_input_to_modules(annotation)
            if not selected_modules:
                print("No matching modules found for the annotation type. Searching all modules instead...")
                selected_modules = modules

            results = search_all_parallel(compound, selected_modules,annotation)

            # Step 2: If no results found, fallback to full search
            if not results and selected_modules != modules:
                print("No results found in selected modules. Trying full module search...\n")
                results = search_all_parallel(compound, modules,annotation)

            if not results:
                print("\nNo results found in any module.")

            #if want to continue
            again = input("\nWould you like to search again? (y/n): ").strip().lower()
            if again not in ['y', 'yes']:
                print("Thank you for using the tool.")
                break

        except KeyboardInterrupt:
            print("\nSearch interrupted.")
            break
        except Exception as e:
            print(f"\nUnexpected error: {e}")
            continue

if __name__ == "__main__":
    main()
