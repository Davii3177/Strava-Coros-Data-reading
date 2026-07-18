"""Region-matched citations for recovery check-ins.

Maps each selectable body area to a short list of peer-reviewed references
drawn strictly from RESEARCH.md (the committed 110-paper literature review)
plus the anchor of the matching region section on the /research page.
Labels and URLs are copied from that document verbatim -- when the review
changes, update both together. Educational reading only, never a diagnosis.
"""

# (label, url) pairs, verbatim from RESEARCH.md rows.
_HEAD = [
    ("Sandoe & Sprenger 2018 · exercise headache review", "https://pubmed.ncbi.nlm.nih.gov/29675548/"),
    ("Upadhyaya et al. 2020 · primary exercise headache", "https://pmc.ncbi.nlm.nih.gov/articles/PMC7160088/"),
]
_NECK = [
    ("Durall 2012 · therapeutic exercise for athlete neck pain", "https://pmc.ncbi.nlm.nih.gov/articles/PMC3435917/"),
    ("Noormohammadpour et al. 2018 · neck pain in athletes", "https://pmc.ncbi.nlm.nih.gov/articles/PMC6284113/"),
]
_UPPER_LIMB = [
    ("Silva et al. 2015 · upper-limb sports injuries", "https://pmc.ncbi.nlm.nih.gov/articles/PMC4799138/"),
    ("Kakouris et al. 2021 · running-related injuries overview", "https://pmc.ncbi.nlm.nih.gov/articles/PMC8500811/"),
]
_TRUNK_FRONT = [
    ("Morton & Callister 2014 · exercise-related transient abdominal pain", "https://pmc.ncbi.nlm.nih.gov/articles/PMC4281377/"),
    ("Eichner 2006 · side stitch causes and solutions", "https://pubmed.ncbi.nlm.nih.gov/17067495/"),
]
_BACK = [
    ("Thornton et al. 2021 · treating low back pain in athletes", "https://pubmed.ncbi.nlm.nih.gov/33355180/"),
    ("Wu et al. 2021 · low back pain in marathon runners", "https://pmc.ncbi.nlm.nih.gov/articles/PMC7920723/"),
]
_SI = [
    ("Pfeiffer et al. 2022 · sacroiliac joint pain in the athlete", "https://pmc.ncbi.nlm.nih.gov/articles/PMC8929229/"),
    ("Abdollahi et al. 2023 · SI dysfunction and lower-limb injury", "https://pmc.ncbi.nlm.nih.gov/articles/PMC10029172/"),
]
_HIP = [
    ("Speers & Bhogal 2017 · greater trochanteric pain syndrome", "https://pmc.ncbi.nlm.nih.gov/articles/PMC5604828/"),
    ("Paluska 2005 · hip injuries in running", "https://pubmed.ncbi.nlm.nih.gov/16271011/"),
]
_GROIN = [
    ("Tyler et al. 2010 · groin injuries in sports medicine", "https://pmc.ncbi.nlm.nih.gov/articles/PMC3445110/"),
    ("Tedeschi et al. 2025 · conservative groin-pain management", "https://pmc.ncbi.nlm.nih.gov/articles/PMC11944235/"),
]
_GLUTE = [
    ("Lempainen et al. 2015 · proximal hamstring tendinopathy", "https://pmc.ncbi.nlm.nih.gov/articles/PMC4396672/"),
    ("Degen 2019 · proximal hamstring injuries", "https://pmc.ncbi.nlm.nih.gov/articles/PMC6542878/"),
]
_HAMSTRING = [
    ("Hickey et al. 2021 · hamstring strain rehabilitation", "https://pmc.ncbi.nlm.nih.gov/articles/PMC8876884/"),
    ("Fredericson et al. 2005 · high hamstring tendinopathy in runners", "https://pubmed.ncbi.nlm.nih.gov/20086362/"),
]
_QUAD = [
    ("Kary 2010 · quadriceps strains and contusions", "https://pmc.ncbi.nlm.nih.gov/articles/PMC2941577/"),
    ("King et al. 2019 · quadriceps tendinopathy treatment", "https://pmc.ncbi.nlm.nih.gov/articles/PMC6409233/"),
]
_ITB = [
    ("Fredericson & Wolf 2005 · iliotibial band syndrome in runners", "https://pubmed.ncbi.nlm.nih.gov/15896092/"),
    ("van der Worp et al. 2012 · ITBS in runners, systematic review", "https://pubmed.ncbi.nlm.nih.gov/22994651/"),
]
_KNEE = [
    ("Mellinger & Neurohr 2019 · knee injuries in runners", "https://pmc.ncbi.nlm.nih.gov/articles/PMC6829001/"),
    ("Santos et al. 2015 · hip strengthening for patellofemoral pain", "https://pmc.ncbi.nlm.nih.gov/articles/PMC4518569/"),
]
_SHIN = [
    ("Galbraith & Lavallee 2009 · shin splints (MTSS) conservative care", "https://pmc.ncbi.nlm.nih.gov/articles/PMC2848339/"),
    ("Winters et al. 2013 · MTSS treatment systematic review", "https://pubmed.ncbi.nlm.nih.gov/23979968/"),
]
_CALF = [
    ("Kahanov et al. 2015 · lower-limb stress fractures in runners", "https://pmc.ncbi.nlm.nih.gov/articles/PMC4384749/"),
    ("Tarabishi et al. 2023 · chronic exertional compartment syndrome", "https://pmc.ncbi.nlm.nih.gov/articles/PMC10676709/"),
]
_ACHILLES = [
    ("Pavone et al. 2019 · Achilles tendinopathy conservative treatment", "https://pubmed.ncbi.nlm.nih.gov/33467361/"),
    ("Beyer et al. 2015 · heavy slow resistance vs eccentric training", "https://pubmed.ncbi.nlm.nih.gov/26018970/"),
]
_ANKLE = [
    ("Ruiz-Sánchez et al. 2022 · ankle sprain practice guidelines", "https://pmc.ncbi.nlm.nih.gov/articles/PMC9592509/"),
]
_HEEL = [
    ("Koc et al. 2023 · plantar fasciitis clinical practice guideline", "https://www.jospt.org/doi/10.2519/jospt.2023.0303"),
    ("Morrissey et al. 2021 · plantar heel pain best practice", "https://pubmed.ncbi.nlm.nih.gov/33785535/"),
]
_FOOT = [
    ("Paavana et al. 2024 · foot stress fractures management", "https://pmc.ncbi.nlm.nih.gov/articles/PMC10904895/"),
    ("Koc et al. 2023 · plantar fasciitis clinical practice guideline", "https://www.jospt.org/doi/10.2519/jospt.2023.0303"),
]
_TOES = [
    ("Rushton & Richie 2024 · friction blister prevention", "https://pmc.ncbi.nlm.nih.gov/articles/PMC10783476/"),
    ("Akella et al. 2023 · subungual hematoma", "https://pmc.ncbi.nlm.nih.gov/articles/PMC10726102/"),
]

# body area -> (region anchor on /research, references)
AREA_REFS = {
    "head_face": ("region-1", _HEAD),
    "jaw": ("region-1", _HEAD),
    "neck": ("region-1", _NECK),
    "collarbones": ("region-2", _UPPER_LIMB),
    "shoulders": ("region-2", _UPPER_LIMB),
    "biceps_triceps": ("region-2", _UPPER_LIMB),
    "elbows": ("region-2", _UPPER_LIMB),
    "forearms": ("region-2", _UPPER_LIMB),
    "wrists_hands": ("region-2", _UPPER_LIMB),
    "chest": ("region-3", _TRUNK_FRONT),
    "ribs": ("region-3", _TRUNK_FRONT),
    "abdomen": ("region-3", _TRUNK_FRONT),
    "upper_back": ("region-3", _BACK),
    "mid_back": ("region-3", _BACK),
    "lower_back": ("region-3", _BACK),
    "sacrum_si": ("region-4", _SI),
    "hips": ("region-4", _HIP),
    "hip_flexors": ("region-4", _HIP),
    "glutes": ("region-5", _GLUTE),
    "groin_adductors": ("region-4", _GROIN),
    "groin": ("region-4", _GROIN),
    "quads": ("region-6", _QUAD),
    "inner_thighs": ("region-4", _GROIN),
    "outer_thighs": ("region-7", _ITB),
    "hamstrings": ("region-5", _HAMSTRING),
    "kneecap": ("region-7", _KNEE),
    "inner_knee": ("region-7", _KNEE),
    "outer_knee": ("region-7", _ITB),
    "knees": ("region-7", _KNEE),
    "shins": ("region-8", _SHIN),
    "calves": ("region-8", _CALF),
    "achilles": ("region-9", _ACHILLES),
    "ankles": ("region-9", _ANKLE),
    "heels": ("region-10", _HEEL),
    "feet": ("region-10", _FOOT),
    "toes": ("region-11", _TOES),
}


def for_areas(body_areas: list[str]) -> dict:
    """Region-matched educational references for the selected body areas.

    Returns {"references": [{"label", "url"}, ...], "research_anchors": [anchor, ...]}
    with order preserved, duplicates removed, and references capped so the
    check-in result stays readable.
    """
    references, anchors, seen_urls, seen_anchors = [], [], set(), set()
    for area in body_areas:
        anchor_refs = AREA_REFS.get(area)
        if anchor_refs is None:
            continue
        anchor, refs = anchor_refs
        if anchor not in seen_anchors:
            seen_anchors.add(anchor)
            anchors.append(anchor)
        for label, url in refs:
            if url in seen_urls:
                continue
            seen_urls.add(url)
            references.append({"label": label, "url": url})
    return {"references": references[:6], "research_anchors": anchors[:4]}
