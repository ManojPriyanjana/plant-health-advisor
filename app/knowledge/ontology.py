AGRI_ONTOLOGY = {
    "Tomato___Bacterial_spot": {
        "crop": "Tomato",
        "pathogen_type": "Bacteria (Xanthomonas spp.)",
        "ontology_terms": [
            {"source": "AGROVOC", "id": "AGROVOC:bacterial_spot", "label": "Bacterial spot"},
        ],
    },
    "Tomato___Early_blight": {
        "crop": "Tomato",
        "pathogen_type": "Fungus (Alternaria solani)",
        "ontology_terms": [
            {"source": "AGROVOC", "id": "AGROVOC:early_blight", "label": "Early blight"},
        ],
    },
    "Tomato___Late_blight": {
        "crop": "Tomato",
        "pathogen_type": "Oomycete (Phytophthora infestans)",
        "ontology_terms": [
            {"source": "AGROVOC", "id": "AGROVOC:late_blight", "label": "Late blight"},
        ],
    },
    "Tomato___Leaf_Mold": {
        "crop": "Tomato",
        "pathogen_type": "Fungus (Passalora fulva)",
        "ontology_terms": [
            {"source": "AGROVOC", "id": "AGROVOC:leaf_mold", "label": "Leaf mold"},
        ],
    },
    "Tomato___Septoria_leaf_spot": {
        "crop": "Tomato",
        "pathogen_type": "Fungus (Septoria lycopersici)",
        "ontology_terms": [
            {"source": "AGROVOC", "id": "AGROVOC:septoria_leaf_spot", "label": "Septoria leaf spot"},
        ],
    },
    "Tomato___Spider_mites Two-spotted_spider_mite": {
        "crop": "Tomato",
        "pathogen_type": "Pest (Tetranychus urticae)",
        "ontology_terms": [
            {"source": "AGROVOC", "id": "AGROVOC:spider_mite", "label": "Two-spotted spider mite"},
        ],
    },
    "Tomato___Target_Spot": {
        "crop": "Tomato",
        "pathogen_type": "Fungus (Corynespora cassiicola)",
        "ontology_terms": [
            {"source": "AGROVOC", "id": "AGROVOC:target_spot", "label": "Target spot"},
        ],
    },
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus": {
        "crop": "Tomato",
        "pathogen_type": "Virus (TYLCV complex)",
        "ontology_terms": [
            {"source": "AGROVOC", "id": "AGROVOC:tomato_yellow_leaf_curl_virus", "label": "TYLCV"},
        ],
    },
    "Tomato___Tomato_mosaic_virus": {
        "crop": "Tomato",
        "pathogen_type": "Virus (ToMV)",
        "ontology_terms": [
            {"source": "AGROVOC", "id": "AGROVOC:tomato_mosaic_virus", "label": "Tomato mosaic virus"},
        ],
    },
    "Tomato___healthy": {
        "crop": "Tomato",
        "pathogen_type": "None",
        "ontology_terms": [
            {"source": "AGROVOC", "id": "AGROVOC:healthy_plant", "label": "Healthy plant"},
        ],
    },
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
