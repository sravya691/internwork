# BioSearchTool

This is a Streamlit-based application that enables parallel search across multiple biological databases using respective unique Id's


## Biological Entity and Database Mapping

| Biological Entity       | Relevant Databases/Tools                                                                                       | Unique ID Present |
|-------------------------|----------------------------------------------------------------------------------------------------------------|-------------------|
| Gene Symbols            | GenBank, UniProt                                                                                               | Yes               |
| Disease                 | EBIOntologyLookupService (OLS: MONDO, DOID, EFO, NCIT, ORDO), UniProt                                          | Yes               |
| Chemical / Metabolite   | MetaNetX, KEGG                                                                                                 | Yes               |
| Species                 | Global Biodiversity Information Facility (GBIF)                                                                | Yes               |
| Cell Line               | Cellosaurus                                                                                                   | Yes               |
| Organelle               | EBI QuickGO                                                                                                   | Yes               |
| Experimental Techniques | BioPortal (Ontology: OBI)                                                                                     | Yes               |
| Protein                 | UniProt                                                                                                       | Yes               |
| Variant                 | Ensembl Variants from PMIDs and KEGG                                                                          | Yes               |
| Non-coding RNA          | RNAcentral                                                                                                    | Yes               |
| Ontology Annotation     | Zooma Ontology from EMBL-EBI                                                                                  | Yes               |

## KEGG Module Mapping

```python
KEGG_DATABASES = {
    "gene": ["genes"],
    "protein": ["enzyme", "ko"],
    "metabolite": ["compound", "reaction", "rclass"],
    "compound": ["compound", "drug", "reaction"],
    "pathway": ["pathway", "module", "network"],
    "drug": ["drug", "disease"],
    "disease": ["disease"],
    "variant": ["variant"],
    "species": ["genome"],
    "ontology": ["brite"],
}
```
## Installation

Install my-project with npm

```bash
# 1. Clone the repository
git clone url
cd multidb-search-tool

# 2. Set up a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

```
    
## Usage/Examples

```bash
streamlit run search_app.py
```

