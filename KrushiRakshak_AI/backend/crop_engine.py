"""Transparent prototype rules. Review this catalogue with local agriculture experts before field use."""
CATALOGUE = [
    {'name':'Sorghum (Jowar)','seasons':['Kharif','Rabi'],'soils':['Black soil','Mixed/unknown','Red soil'],'water':['Low','Moderate'],'note':'Consider only where local season, variety and rainfall suit the field.'},
    {'name':'Pearl millet (Bajra)','seasons':['Kharif'],'soils':['Sandy soil','Red soil','Mixed/unknown'],'water':['Low','Moderate'],'note':'A candidate to discuss for suitable warm-season and lower-water conditions.'},
    {'name':'Pigeon pea (Tur)','seasons':['Kharif'],'soils':['Black soil','Red soil','Mixed/unknown'],'water':['Low','Moderate'],'note':'Check local variety, sowing window and drainage with an extension officer.'},
    {'name':'Chickpea (Harbhara)','seasons':['Rabi'],'soils':['Black soil','Alluvial soil','Mixed/unknown'],'water':['Low','Moderate'],'note':'Confirm residual soil moisture, sowing window and local disease risks.'},
    {'name':'Wheat','seasons':['Rabi'],'soils':['Black soil','Alluvial soil','Mixed/unknown'],'water':['Moderate','High'],'note':'Confirm local temperature window and irrigation access.'},
    {'name':'Rice','seasons':['Kharif'],'soils':['Alluvial soil','Laterite soil','Mixed/unknown'],'water':['Moderate','High'],'note':'Only consider where local rainfall, water supply and land conditions are suitable.'},
    {'name':'Groundnut','seasons':['Kharif','Summer'],'soils':['Sandy soil','Red soil','Mixed/unknown'],'water':['Low','Moderate'],'note':'Check drainage, seed availability and locally recommended varieties.'},
    {'name':'Soybean','seasons':['Kharif'],'soils':['Black soil','Red soil','Mixed/unknown'],'water':['Moderate','High'],'note':'Check rainfall distribution, drainage and current local advisories.'},
    {'name':'Vegetables (local selection)','seasons':['Kharif','Rabi','Summer','Year-round / protected'],'soils':['Alluvial soil','Black soil','Red soil','Mixed/unknown'],'water':['Moderate','High'],'note':'Crop choice depends strongly on market, temperature, soil testing and reliable water.'},
]

def get_recommendations(data):
    candidates=[]
    for crop in CATALOGUE:
        score=0; reasons=[]
        if data.season in crop['seasons']:
            score += 2; reasons.append(f"season ({data.season}) matches the catalogue")
        if data.soil_type in crop['soils'] or data.soil_type == 'Mixed/unknown':
            score += 1; reasons.append(f"soil selection ({data.soil_type}) is compatible with this sample rule")
        if data.water_availability in crop['water']:
            score += 1; reasons.append(f"water availability ({data.water_availability}) matches the sample rule")
        if data.crop_preference and data.crop_preference.lower() in crop['name'].lower():
            score += 3; reasons.append('matches your optional crop preference')
        if score >= 3:
            candidates.append({'crop':crop['name'],'score':score,'reasons':reasons,'consideration':crop['note']})
    candidates.sort(key=lambda x:x['score'], reverse=True)
    return {'candidates':candidates[:5], 'explanation':'Candidates are ranked using only the season, soil category, water availability and optional preference you entered. These are prototype rules, not a validated agronomic model.', 'limitations':'This prototype does not use live weather, laboratory soil data, market prices, cultivar data or block-level agronomic recommendations. It cannot guarantee yield or profit. Confirm decisions with the nearest Krishi Vigyan Kendra or qualified agriculture officer.'}

def problem_guidance(data):
    symptoms=[s.lower() for s in data.symptoms]
    causes=[]
    if any('yellow' in s for s in symptoms): causes.append('Nutrient imbalance, water stress, natural ageing, or a pest/disease may cause yellowing; inspect where it starts and whether it spreads.')
    if any('spot' in s or 'patch' in s for s in symptoms): causes.append('Leaf spots can have fungal, bacterial, insect, or non-living causes; note shape, spread and recent weather.')
    if any('wilt' in s or 'droop' in s for s in symptoms): causes.append('Wilting may be related to soil moisture, root damage, heat, or disease; check soil moisture and roots without disturbing the crop extensively.')
    if any('insect' in s or 'holes' in s for s in symptoms): causes.append('Chewing insects or other pests may be present; inspect both sides of leaves and look for insects or frass.')
    if not causes: causes=['The selected symptoms are not enough to narrow down the cause. Several pests, diseases and environmental stresses can look similar.']
    guidance=['Photograph affected and healthy plants in daylight and record when symptoms began.','Check whether the issue is isolated or spreading across the field.','Avoid applying pesticides or mixing chemicals based on this prototype.','For rapid spread, severe damage, or uncertainty, contact a qualified agriculture officer or Krishi Vigyan Kendra and share the observations.']
    return {'possible_causes':causes,'observable_checks':['Compare affected and healthy plants of the same crop.','Check leaf upper and lower surfaces, stem and nearby soil.','Record recent rainfall, irrigation and any inputs already applied.'],'guidance':guidance,'notice':'This is symptom-based educational guidance, not a diagnosis. No image-based diagnosis or chemical treatment is provided.'}

def irrigation_guidance(data):
    tips=['Check soil moisture at root depth before irrigating; surface appearance alone can mislead.','Consider crop stage, soil texture, recent rainfall and forecast from a trusted local source.','Prefer uniform application and avoid runoff or prolonged waterlogging.']
    if data.soil_type=='Sandy soil': tips.append('Sandy soils often drain faster; check moisture more frequently and avoid assuming one long interval fits every field.')
    if data.soil_type=='Black soil': tips.append('Black soils may retain water; check for waterlogging and allow field conditions to guide timing.')
    if data.water_availability=='Low': tips.append('With limited water, prioritise checking critical crop stages and ask a local officer about locally validated scheduling options.')
    if data.irrigation_method=='Drip': tips.append('Inspect emitters and filters for blockages and check that water reaches the intended root zone.')
    return {'guidance':tips,'notice':'No exact irrigation volume or schedule is calculated. Actual needs vary with local weather, crop variety, soil profile and field conditions.'}
