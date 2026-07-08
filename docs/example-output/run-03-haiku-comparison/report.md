# Run 3 — same pipeline, cheaper model (Haiku 4.5), for cost/quality comparison

Unedited output from an actual run of `python main.py` with `CLAUDE_MODEL` overridden to
`claude-haiku-4-5-20251001` (the cheapest current Claude model — see the `CLAUDE_MODEL` env
var added after this tool was built, `README.md` "Configuration"). Same locations, same
code, same day, only the model changed from Sonnet 5 (used in
[`../run-02-self-critique/report.md`](../run-02-self-critique/report.md)) to Haiku 4.5.

## How to read this report

Same legend as [run-02](../run-02-self-critique/report.md#how-to-read-this-report):
`✅ MATCH FOUND` = deterministically verified (ADR-002); `⚠️ LOW RELEVANCE: reason` = the
self-critique step (ADR-006) flagged a verified excerpt as not substantively relevant;
`❌ [FAILED VALIDATION: reason]` = a tried-and-rejected candidate, kept as an audit trail;
`⚠️ INSUFFICIENT SOURCES (n/2 verified)` = the dimension is still reported in full rather
than omitted (ADR-003).

## What this run demonstrates

Two observed differences from the Sonnet run, both consistent with Haiku being a smaller,
cheaper model rather than random variance:

1. **The self-critique check produced zero `LOW RELEVANCE` flags in this run**, including
   on the exact same `fox10phoenix.com` Chandler "water-splashed at a protest" source that
   Sonnet flagged as low relevance in run-02. Here Haiku's `critique_relevance` call judged
   it relevant with no caveat. This doesn't prove Haiku is wrong on this particular case —
   the source *is* about a Chandler incident — but it does mean the safety margin the
   self-critique check exists to provide is thinner with a weaker judge model. Per ADR-006
   the check is still additive and non-blocking either way, so this isn't a data-integrity
   regression, just a lower-recall second opinion.
2. **Water Stress under-sourced for two of three locations** (Mexicali 1/2, Chandler 0/2
   verified) versus 2/2 for all three locations in the Sonnet runs. `select_chunk` on
   Haiku abstained (`not_relevant`) on candidates that a stronger model was more often able
   to extract a usable excerpt from — same abstain-rather-than-hallucinate behavior as
   ADR-003 describes, just triggered more often.

Net: Haiku is materially cheaper per run but trades away some of the self-critique layer's
effectiveness and some Water Stress sourcing yield. For this take-home's scale (3
locations), the cost difference is negligible, so Sonnet remains the default in
`config.py`; the trade-off would be worth revisiting at 1000-location scale where per-run
cost compounds (see ADR-004).

---

# 📍 Location: Mexicali, Mexico

## 💧 Dimension: Water Stress

**⚠️ INSUFFICIENT SOURCES (1/2 verified)**

- **Data:** Mexico is mentioned among countries experiencing extremely high water stress, using over 80% of renewable water supply.
  - **Source:** https://www.wri.org/insights/highest-water-stressed-countries
  - **Excerpt:** "Is Felt Locally, its Causes Are Increasingly Global Insights March 20, 2024 Which Countries Face the Worst Water Stress? Our data shows that 25 countries are currently exposed to extremely high water stress annually, meaning they use over 80% of their renewable water supply for irrigation, livestock"
  - **Validation:** ✅ MATCH FOUND

- **Source:** https://www.wri.org/aqueduct
  - **Validation:** ❌ [FAILED VALIDATION: not_relevant]

- **Source:** https://mexiconewsdaily.com/news/14-mexican-states-could-face-extreme-water-stress-2030/
  - **Validation:** ❌ [FAILED VALIDATION: not_relevant]

- **Source:** https://www.wri.org/data/aqueduct-40-country-rankings
  - **Validation:** ❌ [FAILED VALIDATION: not_relevant]

- **Source:** https://www.wri.org/data/aqueduct-water-risk-atlas
  - **Validation:** ❌ [FAILED VALIDATION: not_relevant]

## ⚠️ Dimension: Incidents

- **Data:** Mexicali farmers protesting water payment disputes, staged sit-in at CONAGUA offices demanding millions in owed compensation
  - **Source:** https://voiceofsandiego.org/2026/02/27/mexican-farmers-gave-up-water-to-protect-the-colorado-river-they-claim-payment-is-still-due/
  - **Excerpt:** "ail a link to a friend (Opens in new window) Email Print (Opens in new window) Print Illustration by Adriana Heldiz for Voice of San Diego. Sign up for The Morning Report with all your must-read news for the day . This post has been updated. Farmers in Mexicali are protesting again, arguing they hav"
  - **Validation:** ✅ MATCH FOUND

- **Data:** Highway blockades in Baja California near Mexicali protesting highway insecurity and rising business costs including fuel prices and extortion.
  - **Source:** https://mexiconewsdaily.com/news/blockades-mexican-highways/
  - **Excerpt:** "to you. Home El Bajío El Bajío News Northern Border Zone Blockade update: Protests still impacting 4 Mexican highways By MND Staff April 7, 2026 2 Farmers in Costa Rica, Sinaloa, protested unfair prices for their harvests and insecurity on the highways. (José Betanzos Zarate/Cuartoscuro) Protesting "
  - **Validation:** ✅ MATCH FOUND

- **Source:** https://mavensnotebook.com/2026/02/27/voice-of-san-diego-mexican-farmers-gave-up-water-to-protect-the-colorado-river-they-claim-payment-is-still-due/
  - **Validation:** ❌ [FAILED VALIDATION: not_relevant]

## 📜 Dimension: Regulations

- **Data:** Constellation Brands brewery project in Mexicali cancelled due to water scarcity concerns and local referendum, highlighting LAN's limitations on industrial water allocation
  - **Source:** https://mexiconewsdaily.com/water-in-mexico/mexicos-national-water-law-and-industry/
  - **Excerpt:** "o respond to Mexico News Daily over questions about potential changes to the LAN. The agency’s federal budget for fiscal year 2025 is projected to decrease by 40%, raising concerns about its capacity to manage water resources effectively. The Constellation Brands controversy The LAN’s limitations we"
  - **Validation:** ✅ MATCH FOUND

- **Data:** Mexican environmental laws regulate water usage by industrial projects, requiring permits from SEMARNAT covering water usage aspects.
  - **Source:** https://napsintl.com/mexico-manufacturing-news/mexican-environmental-laws-compliance-for-sustainable-operations/
  - **Excerpt:** "NAT (Secretariat of Environment and Natural Resources) and cover various aspects, including air emissions, water usage, and waste management. Environmental Impact Assessments (EIA) An Environmental Impact Assessment (EIA) is required for many industrial projects. This process evaluates the potential"
  - **Validation:** ✅ MATCH FOUND

- **Source:** https://ccn-law.com/en/amendments-to-mexicos-national-waters-law/
  - **Validation:** ❌ [FAILED VALIDATION: empty_page_content]

- **Source:** https://www.mexicoreport.com/2025/12/amendments-to-mexicos-national-waters-law-key-considerations-for-industrial-water-concessionaires/
  - **Validation:** ❌ [FAILED VALIDATION: headless_fetch_error: Page.goto: Timeout 20000ms exceeded.
Call log:
  - navigating to "https://www.mexicoreport.com/2025/12/amendments-to-mexicos-national-waters-law-key-considerations-for-industrial-water-concessionaires/", waiting until "networkidle"
]

- **Source:** https://www.theworldlawgroup.com/news/responsible-exploitation-of-water-in-mexico
  - **Validation:** ❌ [FAILED VALIDATION: not_relevant]


# 📍 Location: Monterrey, Mexico

## 💧 Dimension: Water Stress

- **Data:** Mexico listed among countries experiencing extremely high water stress, using over 80% of renewable water supply.
  - **Source:** https://www.wri.org/insights/highest-water-stressed-countries
  - **Excerpt:** "Is Felt Locally, its Causes Are Increasingly Global Insights March 20, 2024 Which Countries Face the Worst Water Stress? Our data shows that 25 countries are currently exposed to extremely high water stress annually, meaning they use over 80% of their renewable water supply for irrigation, livestock"
  - **Validation:** ✅ MATCH FOUND

- **Data:** WRI Aqueduct scale 0-5; 14 states have extremely high water stress (5), including Nuevo León at medium-high (3) level by 2030.
  - **Source:** https://mexiconewsdaily.com/news/14-mexican-states-could-face-extreme-water-stress-2030/
  - **Excerpt:** "ent to help mitigate the crisis. (Cuartoscuro) In assessing water availability for agricultural, domestic and industrial use, the WRI uses a rating scale from 0 to 5, with 0 representing low water stress and 5 indicating extremely high stress. Based on those indicators , the following states are pro"
  - **Validation:** ✅ MATCH FOUND

- **Source:** https://www.wri.org/data/aqueduct-40-country-rankings
  - **Validation:** ❌ [FAILED VALIDATION: not_relevant]

- **Source:** https://www.wri.org/aqueduct
  - **Validation:** ❌ [FAILED VALIDATION: not_relevant]

- **Source:** https://developers.google.com/earth-engine/datasets/catalog/WRI_Aqueduct_Water_Risk_V4_future_annual
  - **Validation:** ❌ [FAILED VALIDATION: not_relevant]

## ⚠️ Dimension: Incidents

- **Data:** Water-related protests in Monterrey occurred 1978-1985, involving blockading streets and kidnapping water service vehicles and personnel.
  - **Source:** https://networks.h-net.org/node/23910/reviews/54156/klesner-bennett-politics-water-urban-protest-gender-and-power-monterrey
  - **Excerpt:** "e have been particularly strong in Mexico, as scholars have shown.  Monterrey itself had one of the strongest urban popular movements, the Frente Popular Tierra y Libertad, created to support those engaging in land invasions.  Bennett shows that protests over water were concentrated in the 1978-1985"
  - **Validation:** ✅ MATCH FOUND

- **Data:** Poor women in Monterrey used protests to address the 1980s water crisis, making it national news.
  - **Source:** https://muse.jhu.edu/pub/49/monograph/book/88641
  - **Excerpt:** "ty raises serious questions about the process of planning urban services in Mexico.  Bennett uses the water crisis of the 1980s as a lens through which to reveal this planning process and the provision of public services in Monterrey.  She finds three groups who were central to the evolution of the "
  - **Validation:** ✅ MATCH FOUND

## 📜 Dimension: Regulations

- **Data:** Industrial parks in Monterrey must comply with strict water recycling requirements under Mexican regulations.
  - **Source:** https://mexiconewsdaily.com/water-in-mexico/mexicos-national-water-law-and-industry/
  - **Excerpt:** "bal average of four liters. Industrial parks in northern and central Mexico, which host manufacturers from aerospace to agriculture, often build on-site water treatment systems to ensure a reliable supply. However, some regions face acute water challenges. Overexploitation of aquifers is widespread;"
  - **Validation:** ✅ MATCH FOUND

- **Data:** National Water Law establishes legal framework for water management in Mexico, creates Conagua as regulator, and introduces industrial-use concessions with uniform payment system.
  - **Source:** https://www.prodensa.com/insights/blog/water-management-and-industrial-development-in-mexico-a-strategic-overview
  - **Excerpt:** "ates from the 2024-2030 National Water Plan. 1992 💧 Enactment of the National Water Law Establishes the legal framework for water management in Mexico. Creates Conagua , responsible for administering and regulating water resources. Introduces industrial-use concessions , removing previous limits and"
  - **Validation:** ✅ MATCH FOUND


# 📍 Location: Chandler, Arizona, USA

## 💧 Dimension: Water Stress

**⚠️ INSUFFICIENT SOURCES (0/2 verified)**

- **Source:** https://developers.google.com/earth-engine/datasets/catalog/WRI_Aqueduct_Water_Risk_V4_baseline_monthly
  - **Validation:** ❌ [FAILED VALIDATION: not_relevant]

- **Source:** https://www.wri.org/data/aqueduct-water-stress-projections-data
  - **Validation:** ❌ [FAILED VALIDATION: not_relevant]

- **Source:** https://www.wri.org/aqueduct/help-center/water-risk-indicators
  - **Validation:** ❌ [FAILED VALIDATION: not_relevant]

- **Source:** https://developers.google.com/earth-engine/datasets/catalog/WRI_Aqueduct_Water_Risk_V4_baseline_annual
  - **Validation:** ❌ [FAILED VALIDATION: not_relevant]

- **Source:** https://developers.google.com/earth-engine/datasets/catalog/WRI_Aqueduct_Water_Risk_V4_future_annual
  - **Validation:** ❌ [FAILED VALIDATION: not_relevant]

## ⚠️ Dimension: Incidents

- **Data:** Anti-ICE protest in Chandler with incident involving off-duty Phoenix Police sergeant and student protesters.
  - **Source:** https://www.fox10phoenix.com/news/video-shows-phoenix-police-sergeants-encounter-students-anti-ice-protest
  - **Excerpt:** "X 10 Investigates shows what an off-duty Phoenix Police sergeant claimed was an assault that happened during an anti-ICE protest in Chandler. FOX 10 Investigator Justin Lum has more. The Brief New video shows an off-duty Phoenix police sergeant was only splashed with water at a Chandler anti-ICE pro"
  - **Validation:** ✅ MATCH FOUND

- **Data:** Student protest walkout in Chandler at Hamilton High School over immigration enforcement, escalating incident involving armed off-duty police sergeant.
  - **Source:** https://www.azfamily.com/2026/04/09/armed-masked-man-hamilton-high-protest-identified-phoenix-police-sergeant/
  - **Excerpt:** "e incident started as a student walkout similar to many others across the Valley after federal agents in Minneapolis shot and killed Alex Pretti in January . But this one escalated, and the man at the center of it all, according to police, was an armed off-duty Phoenix police sergeant. “Inserting hi"
  - **Validation:** ✅ MATCH FOUND

- **Source:** https://ktar.com/arizona-news/phx-sgt-leave-chandler-ice-protest/5846108/
  - **Validation:** ❌ [FAILED VALIDATION: headless_fetch_error: Page.goto: Timeout 20000ms exceeded.
Call log:
  - navigating to "https://ktar.com/arizona-news/phx-sgt-leave-chandler-ice-protest/5846108/", waiting until "networkidle"
]

## 📜 Dimension: Regulations

- **Data:** Chandler City Code and federal regulations govern industrial wastewater discharge requirements and pretreatment standards for industrial users.
  - **Source:** https://www.chandleraz.gov/residents/water/water-quality/industrial-pretreatment-program/federal-standards
  - **Excerpt:** "Act, Title 40, Code of Federal Regulations (40 CFR) Part 403 “General Pretreatment Regulations for Existing and New Sources of Pollution,” Arizona Administrative Code Title 18 “Environmental Quality,” Chandler City Code Chapters 50-13, 51-6, 51-13, 51-24, 51-25, and governs discharges into a POTW by"
  - **Validation:** ✅ MATCH FOUND

- **Data:** Chandler's Industrial Pretreatment Program protects treatment works from industrial pollutants using Federal Categorical Standards, State Regulations, and local limits authorized by Clean Water Act.
  - **Source:** https://www.chandleraz.gov/residents/water/water-quality/industrial-pretreatment-program
  - **Excerpt:** "s Water Water Quality Industrial Pretreatment Program The purpose of the Industrial Pretreatment Program (IPP) is to protect the Publicly Owned Treatment Works (POTW) – the sanitary sewer system that conveys and the treatment plants that receive wastewater – from pollutants that may cause harm or in"
  - **Validation:** ✅ MATCH FOUND

