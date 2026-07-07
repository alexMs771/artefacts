# FEMA National Risk Index - Data Dictionary (shipped fields)

National Risk Index (NRI), County table, version 1.19.0 (March 2023). Public source: https://www.fema.gov/flood-maps/products-tools/national-risk-index

This reference gives the plain-language meaning of the NRI field codes used as column headers in `ca_wildfire_counties.csv`. Use it to interpret every coded column; the meanings are NOT repeated in the data packet.

## How to read the values

NRI rating fields (the *_RATNG and *_RISKR / *_EALR columns) use a relative, national five-class scale: 'Very Low', 'Relatively Low', 'Relatively Moderate', 'Relatively High', and 'Very High' (for Community Resilience a higher rating means MORE resilient; for risk, expected-annual-loss and social-vulnerability fields a higher rating means WORSE). Score fields (the *_SCORE / *_RISKS / *_EALS columns) are 0-100 values where 100 is the most severe (or, for resilience, the most resilient) county nationally. Dollar fields are in US dollars; WFIR_AFREQ is a count of wildfire events per year; areas are in square miles; population is the 2020 Census count.

## Field definitions

| Field code | Meaning (NRI field alias) | Type | Metric type |
| --- | --- | --- | --- |
| POPULATION | Population (2020) | Integer | n/a |
| BUILDVALUE | Building Value ($) | Double | n/a |
| AGRIVALUE | Agriculture Value ($) | Double | n/a |
| AREA | Area (sq mi) | Double | n/a |
| RISK_SCORE | National Risk Index - Score - Composite | Double | Score |
| RISK_RATNG | National Risk Index - Rating - Composite | String | Rating |
| SOVI_SCORE | Social Vulnerability - Score | Double | Score |
| SOVI_RATNG | Social Vulnerability - Rating | String | Rating |
| RESL_SCORE | Community Resilience - Score | Double | Score |
| RESL_RATNG | Community Resilience - Rating | String | Rating |
| WFIR_AFREQ | Wildfire - Annualized Frequency | Double | Annualized Frequency |
| WFIR_EXP_AREA | Wildfire - Exposure - Impacted Area (sq mi) | Double | Exposure - Area |
| WFIR_EXPB | Wildfire - Exposure - Building Value | Double | Exposure - Building Value |
| WFIR_EXPP | Wildfire - Exposure - Population | Double | Exposure - Population |
| WFIR_HLRB | Wildfire - Historic Loss Ratio - Buildings | Double | Historic Loss Ratio - Buildings |
| WFIR_HLRP | Wildfire - Historic Loss Ratio - Population | Double | Historic Loss Ratio - Population |
| WFIR_EALB | Wildfire - Expected Annual Loss - Building Value | Double | Expected Annual Loss - Building Value |
| WFIR_EALP | Wildfire - Expected Annual Loss - Population | Double | Expected Annual Loss - Population |
| WFIR_EALT | Wildfire - Expected Annual Loss - Total | Double | Expected Annual Loss - Total |
| WFIR_EALS | Wildfire - Expected Annual Loss Score | Double | Expected Annual Loss Score |
| WFIR_EALR | Wildfire - Expected Annual Loss Rating | String | Expected Annual Loss Rating |
| WFIR_ALRB | Wildfire - Expected Annual Loss Rate - Building | Double | Expected Annual Loss Rate - Building |
| WFIR_RISKV | Wildfire - Hazard Type Risk Index Value | Double | Hazard Type Risk Index Value |
| WFIR_RISKS | Wildfire - Hazard Type Risk Index Score | Double | Hazard Type Risk Index Score |
| WFIR_RISKR | Wildfire - Hazard Type Risk Index Rating | String | Hazard Type Risk Index Rating |
