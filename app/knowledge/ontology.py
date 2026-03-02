# Very simple ontology stub (expand later)
AGRI_ONTOLOGY = {
    "Tomato___Late_blight": {
        "crop": "Tomato",
        "pathogen_type": "Oomycete (Phytophthora infestans)",
        "ontology_terms": [
            {"source": "AGROVOC", "id": "AGROVOC:late_blight", "label": "Late blight"},
        ],
    }
}


def get_ontology(disease_name: str):
    return AGRI_ONTOLOGY.get(
        disease_name,
        {
            "crop": "Unknown",
            "pathogen_type": "Unknown",
            "ontology_terms": [{"source": "LOCAL", "id": "UNKNOWN", "label": disease_name}],
        },
    )