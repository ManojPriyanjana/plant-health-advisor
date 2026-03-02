from app.knowledge.ontology import get_ontology

# Simple “KB” advice (you can expand)
KB = {
    "Tomato___Late_blight": {
        "summary": "Late blight is a fast-spreading disease that causes dark lesions on leaves and fruit.",
        "treatments": [
            "Remove infected leaves and destroy them (do not compost).",
            "Use recommended fungicide (follow local agricultural guidance).",
            "Avoid overhead watering and improve airflow.",
        ],
        "prevention": [
            "Use disease-resistant varieties if available.",
            "Rotate crops and avoid planting tomatoes near potatoes.",
            "Keep leaves dry; water at the base of the plant.",
        ],
    }
}


def build_advisory_response(disease_name: str):
    onto = get_ontology(disease_name)
    kb = KB.get(
        disease_name,
        {
            "summary": "No specific entry found. Consult local agricultural guidance.",
            "treatments": ["Consult an expert / extension service."],
            "prevention": ["Maintain good crop hygiene and monitor plants regularly."],
        },
    )

    return {
        "disease_name": disease_name,
        "crop": onto["crop"],
        "pathogen_type": onto["pathogen_type"],
        "ontology_terms": onto["ontology_terms"],
        "summary": kb["summary"],
        "recommended_treatments": kb["treatments"],
        "prevention_tips": kb["prevention"],
    }