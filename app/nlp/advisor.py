from app.knowledge.ontology import get_ontology

# Rule-based advisory knowledge base.
KB = {
    "Tomato___Bacterial_spot": {
        "summary": "Bacterial spot causes dark leaf lesions and can reduce yield if unmanaged.",
        "treatments": [
            "Remove heavily infected leaves and sanitize tools after handling plants.",
            "Apply a recommended copper-based bactericide according to local guidance.",
            "Avoid working with wet plants to reduce spread.",
        ],
        "prevention": [
            "Use clean seed/transplants and avoid overhead irrigation.",
            "Rotate away from tomato/pepper crops between seasons.",
            "Improve spacing and airflow in the canopy.",
        ],
    },
    "Tomato___Early_blight": {
        "summary": "Early blight commonly starts on older leaves with concentric ring lesions.",
        "treatments": [
            "Prune and discard infected foliage away from the field.",
            "Use an approved fungicide program when conditions are favorable for disease.",
            "Mulch and stake plants to limit soil splash onto leaves.",
        ],
        "prevention": [
            "Rotate crops and remove crop residue after harvest.",
            "Maintain balanced nutrition and avoid plant stress.",
            "Water at the base of plants instead of overhead watering.",
        ],
    },
    "Tomato___Late_blight": {
        "summary": "Late blight is fast-spreading and can rapidly destroy foliage and fruit.",
        "treatments": [
            "Remove infected tissue immediately and destroy it (do not compost).",
            "Apply locally recommended fungicides promptly when infection risk is high.",
            "Reduce leaf wetness duration by improving airflow and irrigation timing.",
        ],
        "prevention": [
            "Use resistant varieties where available.",
            "Avoid planting tomatoes near potato crops when outbreaks are present.",
            "Monitor plants frequently during cool, humid weather.",
        ],
    },
    "Tomato___Leaf_Mold": {
        "summary": "Leaf mold appears as yellow areas on upper leaf surfaces and mold growth underneath.",
        "treatments": [
            "Remove infected leaves to lower inoculum pressure.",
            "Lower humidity in protected cultivation through ventilation.",
            "Use fungicides labeled for leaf mold where needed.",
        ],
        "prevention": [
            "Avoid prolonged leaf wetness and dense canopy humidity.",
            "Space plants properly and prune for airflow.",
            "Disinfect greenhouse structures and tools between cycles.",
        ],
    },
    "Tomato___Septoria_leaf_spot": {
        "summary": "Septoria leaf spot causes many small circular lesions and progressive defoliation.",
        "treatments": [
            "Remove lower infected leaves early in disease development.",
            "Use a protective fungicide program per local extension advice.",
            "Avoid splashing water from soil to foliage.",
        ],
        "prevention": [
            "Practice crop rotation and remove old plant debris.",
            "Stake and mulch plants to reduce soil contact and splash.",
            "Inspect regularly and manage symptoms at first detection.",
        ],
    },
    "Tomato___Spider_mites Two-spotted_spider_mite": {
        "summary": "Spider mite feeding causes stippling, leaf bronzing, and reduced vigor.",
        "treatments": [
            "Check undersides of leaves and remove heavily infested foliage.",
            "Use approved miticides or biological controls according to label guidance.",
            "Reduce drought stress and dust, which can worsen mite outbreaks.",
        ],
        "prevention": [
            "Scout regularly, especially in hot and dry periods.",
            "Encourage beneficial predators where feasible.",
            "Quarantine new plants before introducing them to production areas.",
        ],
    },
    "Tomato___Target_Spot": {
        "summary": "Target spot causes brown lesions and can lead to leaf drop in humid conditions.",
        "treatments": [
            "Remove infected leaves and improve canopy ventilation.",
            "Apply labeled fungicides in a resistance-aware rotation.",
            "Avoid frequent overhead irrigation that keeps foliage wet.",
        ],
        "prevention": [
            "Manage plant density and prune to increase airflow.",
            "Rotate crops and sanitize plant debris after harvest.",
            "Monitor humidity and leaf wetness duration in protected systems.",
        ],
    },
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus": {
        "summary": "TYLCV causes curling, yellowing, and stunted growth; spread is linked to whiteflies.",
        "treatments": [
            "Rogue severely affected plants to reduce virus reservoirs.",
            "Control whitefly vectors using integrated pest management.",
            "Use reflective mulches or exclusion netting where practical.",
        ],
        "prevention": [
            "Use resistant/tolerant cultivars when available.",
            "Maintain strict whitefly control and weed host management.",
            "Start with clean transplants and protect nurseries from vectors.",
        ],
    },
    "Tomato___Tomato_mosaic_virus": {
        "summary": "Tomato mosaic virus causes mottling and distortion and can spread mechanically.",
        "treatments": [
            "Remove infected plants and avoid touching healthy plants after handling diseased ones.",
            "Disinfect tools and hands regularly during crop work.",
            "Use sanitation-focused management because curative control is limited.",
        ],
        "prevention": [
            "Use certified disease-free seed/transplants.",
            "Avoid tobacco contamination and maintain strict hygiene.",
            "Control volunteer plants and weed hosts around production areas.",
        ],
    },
    "Tomato___healthy": {
        "summary": "The plant appears healthy with no major disease symptoms detected.",
        "treatments": [
            "No treatment is required at this time.",
            "Continue regular monitoring and good crop hygiene.",
        ],
        "prevention": [
            "Keep balanced irrigation, nutrition, and airflow management.",
            "Inspect plants weekly for early symptom detection.",
            "Maintain sanitation and remove debris to reduce disease pressure.",
        ],
    },
}


def build_advisory_response(disease_name: str):
    onto = get_ontology(disease_name)
    kb = KB.get(
        disease_name,
        {
            "summary": "No specific entry found. Consult local agricultural guidance.",
            "treatments": ["Consult an expert or extension service."],
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
