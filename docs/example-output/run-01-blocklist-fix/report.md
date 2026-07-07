# Run 1 — real run after the water-stress domain blocklist fix

This is an unedited output from an actual run of the tool (`python main.py`), from
**before the self-critique check (ADR-006) existed** — kept as a historical record
because it demonstrates a different, still-relevant finding (see below). For the
self-critique bonus in action, see
[`../run-02-self-critique/report.md`](../run-02-self-critique/report.md). Full design
rationale is in [`docs/adr/`](../../adr/).

## How to read this report

- **✅ MATCH FOUND** — the `Excerpt` was independently re-fetched and verified as a
  literal (normalized) substring of the source page. Verification is deterministic code,
  not a model judgment call — see [ADR-002](../../adr/ADR-002-deterministic-verification.md).
- **❌ [FAILED VALIDATION: reason]** — a candidate source that was tried and rejected.
  These are shown, not hidden, as an audit trail of what the tool attempted
  (`not_relevant`: the LLM found no chunk supporting the claim; `empty_page_content`:
  fetch succeeded but yielded no usable text; `headless_fetch_error`: the optional
  headless fallback wasn't available or timed out — see
  [ADR-005](../../adr/ADR-005-stack-choice.md)).
- **⚠️ INSUFFICIENT SOURCES (n/2 verified)** — the dimension is still reported in full
  rather than omitted; see
  [ADR-003](../../adr/ADR-003-failure-handling-and-contradictions.md)
  for why omission was rejected.
- **Data** is an LLM-authored short summary — it is interpretation, meant to be checked
  against the verbatim **Excerpt** next to it, not trusted on its own.

## What this run demonstrates (validated findings, not gaps)

**Chandler, AZ shows Water Stress at 0/2 and Incidents at 1/2, while both Mexican
locations reach 2/2 on every dimension.** This is a real, expected data point about
source-coverage variance by location, not a pipeline defect: Mexicali and Monterrey have
dense secondary-source coverage (news outlets summarizing WRI Aqueduct data, academic
literature on historical water protests), while Chandler's water-stress coverage is
dominated by GIS/dataset-catalog pages (WRI help-center docs, Google Earth Engine dataset
listings) that carry no location-specific prose to extract. At 1,000-location scale
(ADR-004), this variance is exactly what should be expected and monitored — some
locations will have thin, catalog-only coverage for a given dimension, and the tool
surfaces that honestly via `INSUFFICIENT SOURCES` rather than forcing a result.

**The Chandler Incidents match on `abc15.com` is what originally motivated building the
self-critique bonus (ADR-006).** The verified excerpt is real (it does appear verbatim on
the page) but is largely site navigation chrome ("Let's Talk Things To Do Operation Safe
Roads Smart Shopper...") with the actual article text at the tail end. Verification did
its job correctly — the excerpt is genuinely on the page — but nothing in the pipeline
*at the time this run was captured* judged whether the selected chunk was actually good
signal versus incidentally-verifiable boilerplate. That gap is now closed: see
[`../run-02-self-critique/report.md`](../run-02-self-critique/report.md) for a later run
with the self-critique check live, catching similar (and different) low-relevance cases.

---

# 📍 Location: Mexicali, Mexico

## 💧 Dimension: Water Stress

- **Data:** Mexicali is in Baja California; state's water depletion category not explicitly listed but Sonora (extremely high, >80%) is neighboring; chunk gives WRI 0-5 scale definitions
  - **Source:** https://mexiconewsdaily.com/news/14-mexican-states-could-face-extreme-water-stress-2030/
  - **Excerpt:** "ent to help mitigate the crisis. (Cuartoscuro) In assessing water availability for agricultural, domestic and industrial use, the WRI uses a rating scale from 0 to 5, with 0 representing low water stress and 5 indicating extremely high stress. Based on those indicators , the following states are pro"
  - **Validation:** ✅ MATCH FOUND

- **Data:** Mexico listed among countries/places experiencing water shortage crises; part of 25 countries with extremely high water stress (>80% of renewable supply used)
  - **Source:** https://www.wri.org/insights/highest-water-stressed-countries
  - **Excerpt:** "Is Felt Locally, its Causes Are Increasingly Global Insights March 20, 2024 Which Countries Face the Worst Water Stress? Our data shows that 25 countries are currently exposed to extremely high water stress annually, meaning they use over 80% of their renewable water supply for irrigation, livestock"
  - **Validation:** ✅ MATCH FOUND

- **Source:** https://www.wri.org/aqueduct
  - **Validation:** ❌ [FAILED VALIDATION: not_relevant]

- **Source:** https://www.wri.org/data/aqueduct-water-risk-atlas
  - **Validation:** ❌ [FAILED VALIDATION: not_relevant]

- **Source:** https://www.wri.org/data/aqueduct-40-country-rankings
  - **Validation:** ❌ [FAILED VALIDATION: not_relevant]

## ⚠️ Dimension: Incidents

- **Data:** Mexicali Resiste blockaded Constellation Brands aqueduct construction over water crisis concerns for over a year.
  - **Source:** https://itsgoingdown.org/mexicali-resiste-blockade/
  - **Excerpt:** "’s note: For more than one year, residents of Mexicali have been organizing against the construction of a brewery and aqueduct by the U.S. company Constellation Brands. If completed, the facility would produce beer for export to the U.S. and consume seven to thirty million cubic meters of water annu"
  - **Validation:** ✅ MATCH FOUND

- **Data:** Chihuahua residents violently protested/occupied La Boquilla dam over water diversion to US amid drought
  - **Source:** https://www.aljazeera.com/news/2020/9/9/mexico-two-killed-in-clash-with-military-police-near-dam-protest
  - **Excerpt:** ", the National Guard has said, as tensions rose between protesters and officials in the drought-hit region. Mexicans in the northern border state of Chihuahua, angry at the water being funnelled across the border, on Tuesday evening had hurled Molotov cocktails and rocks at security forces, eventual"
  - **Validation:** ✅ MATCH FOUND

## 📜 Dimension: Regulations

- **Data:** Constellation Brands' Mexicali brewery project cancelled in 2020 after referendum over water scarcity concerns, despite holding LAN permits.
  - **Source:** https://mexiconewsdaily.com/water-in-mexico/mexicos-national-water-law-and-industry/
  - **Excerpt:** "o respond to Mexico News Daily over questions about potential changes to the LAN. The agency’s federal budget for fiscal year 2025 is projected to decrease by 40%, raising concerns about its capacity to manage water resources effectively. The Constellation Brands controversy The LAN’s limitations we"
  - **Validation:** ✅ MATCH FOUND

- **Data:** Mexican environmental laws regulate industrial water extraction/use and air emissions; companies must monitor and report water consumption to authorities.
  - **Source:** https://napsintl.com/mexico-manufacturing-news/mexican-environmental-laws-compliance-for-sustainable-operations/
  - **Excerpt:** ". Waste Management Managing hazardous and non-hazardous waste is a critical aspect of compliance. Companies must develop comprehensive waste management plans that adhere to Mexican regulations, ensuring safe storage, transportation, and disposal of materials. Water Usage and Air Emissions Mexican en"
  - **Validation:** ✅ MATCH FOUND

- **Source:** https://ccn-law.com/en/amendments-to-mexicos-national-waters-law/
  - **Validation:** ❌ [FAILED VALIDATION: empty_page_content]

- **Source:** https://www.mexicoreport.com/2025/12/amendments-to-mexicos-national-waters-law-key-considerations-for-industrial-water-concessionaires/
  - **Validation:** ❌ [FAILED VALIDATION: headless_fetch_error: Page.goto: Timeout 20000ms exceeded.
Call log:
  - navigating to "https://www.mexicoreport.com/2025/12/amendments-to-mexicos-national-waters-law-key-considerations-for-industrial-water-concessionaires/", waiting until "networkidle"
]


# 📍 Location: Monterrey, Mexico

## 💧 Dimension: Water Stress

- **Data:** Mexico cited as example of country experiencing water stress/shutoffs; part of 25 countries facing extremely high water stress (>80% of renewable supply used).
  - **Source:** https://www.wri.org/insights/highest-water-stressed-countries
  - **Excerpt:** "Is Felt Locally, its Causes Are Increasingly Global Insights March 20, 2024 Which Countries Face the Worst Water Stress? Our data shows that 25 countries are currently exposed to extremely high water stress annually, meaning they use over 80% of their renewable water supply for irrigation, livestock"
  - **Validation:** ✅ MATCH FOUND

- **Data:** Nuevo León (Monterrey's state) projected medium-high water depletion, 20-40%, per WRI Aqueduct scale.
  - **Source:** https://mexiconewsdaily.com/news/14-mexican-states-could-face-extreme-water-stress-2030/
  - **Excerpt:** "ent to help mitigate the crisis. (Cuartoscuro) In assessing water availability for agricultural, domestic and industrial use, the WRI uses a rating scale from 0 to 5, with 0 representing low water stress and 5 indicating extremely high stress. Based on those indicators , the following states are pro"
  - **Validation:** ✅ MATCH FOUND

- **Source:** https://www.wri.org/data/aqueduct-40-country-rankings
  - **Validation:** ❌ [FAILED VALIDATION: not_relevant]

- **Source:** https://www.wri.org/aqueduct
  - **Validation:** ❌ [FAILED VALIDATION: not_relevant]

## ⚠️ Dimension: Incidents

- **Data:** Protests over water concentrated 1978-1985, involved blockading streets and kidnapping water service vehicles/personnel.
  - **Source:** https://networks.h-net.org/node/23910/reviews/54156/klesner-bennett-politics-water-urban-protest-gender-and-power-monterrey
  - **Excerpt:** "e have been particularly strong in Mexico, as scholars have shown.  Monterrey itself had one of the strongest urban popular movements, the Frente Popular Tierra y Libertad, created to support those engaging in land invasions.  Bennett shows that protests over water were concentrated in the 1978-1985"
  - **Validation:** ✅ MATCH FOUND

- **Data:** Poor women in Monterrey organized protests over the 1980s water crisis, drawing national attention and prompting government response.
  - **Source:** https://muse.jhu.edu/pub/49/monograph/book/88641
  - **Excerpt:** "e of poor women to the water crisis, analyzing who participated in protests, the strategies they used, and how the government responded.  And, finally, she considers the dynamics of planning water services for the private sector and the government in investment and management.  In the end, Monterrey"
  - **Validation:** ✅ MATCH FOUND

## 📜 Dimension: Regulations

- **Data:** Industrial parks in Monterrey (among others) must comply with strict water recycling requirements per Ampip report.
  - **Source:** https://mexiconewsdaily.com/water-in-mexico/mexicos-national-water-law-and-industry/
  - **Excerpt:** "f these measures, noting that industrial parks — primarily located in Monterrey, Tijuana, Querétaro, and San Luis Potosí — must comply with strict water recycling requirements. Yet, challenges persist. According to the Ministry of Foreign Affairs in the Netherlands, only 1% of Mexico’s wastewater is"
  - **Validation:** ✅ MATCH FOUND

- **Data:** National Water Law (LAN) established Conagua and a concession system enabling companies to access water for industrial use.
  - **Source:** https://www.prodensa.com/insights/blog/water-management-and-industrial-development-in-mexico-a-strategic-overview
  - **Excerpt:** "n , modernized Mexico’s water regulation by replacing the previous system of allocations (public use) and concessions (commercial use) with a unified framework focused on economic liberalization. It also created the National Water Commission (Conagua) as the primary authority and established a conce"
  - **Validation:** ✅ MATCH FOUND


# 📍 Location: Chandler, Arizona, USA

## 💧 Dimension: Water Stress

**⚠️ INSUFFICIENT SOURCES (0/2 verified)**

- **Source:** https://www.wri.org/aqueduct/help-center/water-risk-indicators
  - **Validation:** ❌ [FAILED VALIDATION: not_relevant]

- **Source:** https://www.wri.org/data/aqueduct-water-stress-projections-data
  - **Validation:** ❌ [FAILED VALIDATION: not_relevant]

- **Source:** https://developers.google.com/earth-engine/datasets/catalog/WRI_Aqueduct_Water_Risk_V4_baseline_monthly
  - **Validation:** ❌ [FAILED VALIDATION: not_relevant]

- **Source:** https://developers.google.com/earth-engine/datasets/catalog/WRI_Aqueduct_Water_Risk_V4_future_annual
  - **Validation:** ❌ [FAILED VALIDATION: not_relevant]

- **Source:** https://developers.google.com/earth-engine/datasets/catalog/WRI_Aqueduct_Water_Risk_V4_baseline_annual
  - **Validation:** ❌ [FAILED VALIDATION: not_relevant]

## ⚠️ Dimension: Incidents

**⚠️ INSUFFICIENT SOURCES (1/2 verified)**

- **Data:** Describes a high school ICE protest in Chandler, AZ where an off-duty officer confronted students.
  - **Source:** https://www.abc15.com/news/local-news/investigations/body-camera-video-shows-phoenix-sgt-at-high-school-protest-wanted-students-to-assault-him
  - **Excerpt:** "Let's Talk Things To Do Operation Safe Roads Smart Shopper The Spot - Arizona 61 Contests DirecTV has removed ABC15 Arizona – Here’s how to keep watching News Local News Investigations Actions Facebook Tweet Email Body camera video shows Phoenix Sgt. at high school protest, wanted students to assaul"
  - **Validation:** ✅ MATCH FOUND

- **Source:** https://www.fox10phoenix.com/news/video-shows-phoenix-police-sergeants-encounter-students-anti-ice-protest
  - **Validation:** ❌ [FAILED VALIDATION: not_relevant]

- **Source:** https://www.azfamily.com/2026/04/09/armed-masked-man-hamilton-high-protest-identified-phoenix-police-sergeant/
  - **Validation:** ❌ [FAILED VALIDATION: not_relevant]

- **Source:** https://www.12news.com/article/news/local/valley/phoenix-officer-on-leave-for-involvement-chandler-protest-police-chief-says/75-0ed9ed46-4120-4963-a906-806377d625c1
  - **Validation:** ❌ [FAILED VALIDATION: not_relevant]

- **Source:** https://www.abc15.com/news/region-southeast-valley/mesa/police-two-juveniles-arrested-after-anti-ice-protest-in-mesa
  - **Validation:** ❌ [FAILED VALIDATION: not_relevant]

## 📜 Dimension: Regulations

- **Data:** Chandler industrial wastewater discharge governed by 40 CFR Part 403, AZ Admin Code Title 18, and City Code Ch. 50-13, 51-6, 51-13, 51-24, 51-25.
  - **Source:** https://www.chandleraz.gov/residents/water/water-quality/industrial-pretreatment-program/federal-standards
  - **Excerpt:** "Act, Title 40, Code of Federal Regulations (40 CFR) Part 403 “General Pretreatment Regulations for Existing and New Sources of Pollution,” Arizona Administrative Code Title 18 “Environmental Quality,” Chandler City Code Chapters 50-13, 51-6, 51-13, 51-24, 51-25, and governs discharges into a POTW by"
  - **Validation:** ✅ MATCH FOUND

- **Data:** Chandler's Industrial Pretreatment Program, adopted via Ordinance 4503/City Code Ch. 51-24, regulates industrial wastewater discharge per federal/state law.
  - **Source:** https://www.chandleraz.gov/residents/water/water-quality/industrial-pretreatment-program
  - **Excerpt:** "s Water Water Quality Industrial Pretreatment Program The purpose of the Industrial Pretreatment Program (IPP) is to protect the Publicly Owned Treatment Works (POTW) – the sanitary sewer system that conveys and the treatment plants that receive wastewater – from pollutants that may cause harm or in"
  - **Validation:** ✅ MATCH FOUND

