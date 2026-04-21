# ICE Detention Discrepancies

An interactive data storytelling tool that helps general audiences understand patterns and disparities in the US Immigration and Customs Enforcement (ICE) detention system. Built for CS7250 Information Visualization at Northeastern University.

**Live site:** https://ice-discrepancies.vercel.app

---

## Overview

This tool allows users to explore ICE detention data across demographic groups, compare outcomes between populations, and read documented accounts of individual detention cases drawn from named media sources. It is designed for laypeople with no prior knowledge of the immigration system.

The tool is organized as a scrolling narrative with the following sections:

- **System Scale** — detention volume over time and facility footprint across the US
- **Outcomes Comparison** — breakdown of release, removal, transfer, and continued detention by demographic group
- **Detention Length** — distribution of how long individuals remain detained across selected groups
- **Individual Cases** — seven documented vignettes of named individuals drawn from reported sources
- **System Pathways** — Sankey diagrams tracing booking-to-outcome and conviction-to-release flows
- **Insight Panel** — summary statistics for the current filter selection

---

## Data

The dataset is sourced from the **Deportation Detention Project**, which cleaned and structured a FOIA-released ICE data dump for public use. The processed data is stored as static JSON files in `public/data/` and loaded client-side at runtime.

| File | Contents |
|------|----------|
| `public/data/processedData.json` | Individual detention records with demographic fields, facility IDs, booking years, outcomes, and detention lengths |
| `public/data/convictionReleaseSankey.json` | Pre-aggregated node/link data for the conviction-to-release Sankey diagram |
| `public/data/stats_df.json` | Aggregate summary statistics broken down by demographic groups, used primarily by the Infographic component. Includes detention counts, average lengths, outcome distributions, and demographic composition across all filterable dimensions |

Each record in `processedData.json` includes the following fields:

| Field | Description |
|-------|-------------|
| `sex` | Sex of detainee |
| `age_group` | Age bracket |
| `region_of_origin` | World region |
| `criminal_history` | Criminal history category |
| `first_booking_type` | How the individual entered detention |
| `booking_year` | Year of initial booking |
| `detention_length_days` | Total days detained |
| `outcome` | Released, Removed, Transferred, or Still Detained |
| `facility_id` | Facility identifier, joined to facility metadata |
| `transfer_type` | Type of transfer if applicable |

### Datasets in `src/data/data/`

The `data/` subdirectory contains processed outputs, reference lookups, and source data files:

**Processed & Generated Data:**
| File | Contents |
|------|----------|
| `processedData.json` | Individual detention records (primary dataset) exported as JSON for web consumption |
| `convictionReleaseSankey.json` | Pre-aggregated node/link pairs for Sankey flow diagram visualization |
| `stats_df.json` | Summary statistics aggregated by demographic dimensions for infographic display |
| `stats_df.xlsx` | Spreadsheet version of summary statistics |
| `mockData.json` | Mock/sample data used in development and testing |

**Reference Lookups & Mappings:**
| File | Purpose |
|------|---------|
| `facility_code_map_with_coordinates.csv` | Maps ICE facility codes to facility names and geographic coordinates (latitude/longitude) |
| `cleaned_us_city_state_county_zip.csv` | City, state, county, and ZIP code reference table for location standardization |
| `country_to_region_map.xlsx` | Maps countries to broader world regions for demographic grouping |
| `detention_release_reason_map.xlsx` | Maps release reason codes to human-readable categories |
| `most_serious_conviction_map.xlsx` | Maps conviction codes to conviction type categories |
| `religion_cleaning_map.xlsx` | Standardizes religion field values |

**Raw & Working Data Files:**
| File | Description |
|------|-------------|
| `detention-stays-latest.csv/.xlsx` | Raw detention stay records from Deportation Detention Project |
| `detention-stints-latest.csv/.xlsx` | Raw detention stint records (episodes within a stay) |
| `detainers-latest.xlsx` | Detainer records from ICE data |
| `arrests-latest.xlsx` | Arrest records from ICE data |
| `facilities-daily-population-latest.xlsx` | Daily population counts per facility |
| `detention_stays_df.pkl` | Serialized Python DataFrame of detention stays for processing |
| `facility_enriched.xlsx` | Facility metadata after enrichment with external data |
| `super mini cleaned df.xlsx` | Minimal cleaned subset used for testing/demo |

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Framework | React 18 |
| Build tool | Vite 5 |
| Visualization | D3 v7, d3-sankey |
| Maps | TopoJSON, us-atlas |
| Routing | react-router-dom |
| Deployment | Vercel |

---

## Project Structure

```
ice_discrepancies/
├── public/
│   └── data/                        # Static JSON data files
│       ├── processedData.json
│       ├── convictionReleaseSankey.json
│       ├── stats_df.json
│       └── *.png                    # Images used by Infographic
│   ├── kilmar-abrego-garcia.webp    # Vignette portrait images
│   ├── godfrey-wade.avif
│   ├── any-lucia-lopez-belloza.avif
│   └── mohammed-hoque.png
├── src/
│   ├── App.jsx                      # Root component, page layout and section order
│   ├── main.jsx                     # React entry point
│   ├── styles.css                   # Global styles and design tokens
│   ├── components/
│   │   ├── Hero.jsx                 # Landing section
│   │   ├── Filters.jsx              # Sidebar demographic filter controls
│   │   ├── LineChart.jsx            # Detention volume over time
│   │   ├── MapPlaceholder.jsx       # US facility map
│   │   ├── StackedBar.jsx           # Outcomes comparison chart
│   │   ├── BoxPlot.jsx              # Detention length distributions
│   │   ├── SankeyDiagram.jsx        # Flow diagrams (booking and conviction)
│   │   ├── InsightPanel.jsx         # Summary statistics panel
│   │   ├── Infographic.jsx          # Static infographic summary
│   │   ├── Vignettes.jsx            # Individual case narratives
│   │   └── Methodology.jsx          # Data methodology notes
│   ├── hooks/
│   │   ├── useData.js               # Data loading and filter computation
│   │   └── useFilters.js            # Global filter state via React context
│   └── data/                        # Data processing and assets
│       ├── scripts/                 # Python data processing scripts
│       │   ├── detention_data_cleaning.py
│       │   ├── preprocess_for_web.py
│       │   ├── preprocess_conviction_release_sankey.py
│       │   ├── export_stats_df_for_infographic.py
│       │   ├── helpers.py
│       │   └── ...
│       ├── data/                    # Processed data files and lookups
│       │   ├── processedData.json
│       │   ├── convictionReleaseSankey.json
│       │   ├── stats_df.json
│       │   ├── mockData.json
│       │   ├── *.csv                # Facility mappings, city/state lookups
│       │   ├── *.xlsx               # Detention records, facility enrichment
│       │   └── ...
│       └── assets/                  # Images and graphic assets
│           ├── america.png
│           ├── person.svg
│           └── ...
├── index.html
├── vite.config.js
└── package.json
```

---

## Data Folder Organization

The `src/data/` directory contains the data processing pipeline and assets, organized into three subdirectories:

- **`scripts/`** — Python scripts for data cleaning, preprocessing, and transformation
  - `detention_data_cleaning.py` — Clean and validate raw ICE FOIA data
  - `preprocess_for_web.py` — Transform cleaned data into JSON for web consumption
  - `preprocess_conviction_release_sankey.py` — Generate aggregated Sankey diagram data
  - `export_stats_df_for_infographic.py` — Export summary statistics for UI
  - `helpers.py` — Shared utility functions for data processing

- **`data/`** — Processed data files and reference lookups
  - Live data (used by the app):
    - `processedData.json` — Individual detention records
    - `convictionReleaseSankey.json` — Pre-aggregated Sankey node/link data
    - `stats_df.json` — Summary statistics for filtering and analytics
  - Development data: `mockData.json`, `processedData1.json`
  - Reference lookups: facility mappings, city/state coordinates, conviction type mappings, etc.
  - Raw data files: detention records in CSV and pickle formats

- **`assets/`** — Image and graphic files
  - Icons and symbols used in visualizations
  - Infographic components (person icons, currency symbols, etc.)

---

## How the Data Pipeline Works

All data processing happens client-side at runtime — there is no backend.

**Loading (`useData.js`):** On mount, the app fetches `processedData.json` and `convictionReleaseSankey.json` from the `public/data/` directory. Records are stored in React state.

**Filtering (`useFilters.js`):** Filter state is managed globally via React context. Two independent filter sets are maintained; Group A (primary) and Group B (comparison), each with five demographic dimensions plus a shared year range. Defaults are `"All"` for demographic fields and 2022–2025 for years.

**Computation (`useData.js`):** On every filter change, `useMemo` recomputes derived datasets from the full record set without re-fetching. This includes outcome share calculations, scaled time series, facility counts, detention length arrays, and Sankey link aggregations. The comparison group uses the same year bounds as the primary group.

---

## Local Development

**Prerequisites:** Node.js 18 or later.

```bash
# Clone the repo
git clone https://github.com/philchandy/ice_discrepancies.git
cd ice_discrepancies

# Install dependencies
npm install

# Start the development server
npm run dev
```

The app will be available at `http://localhost:5173`.

```bash
# Build for production
npm run build

# Preview the production build locally
npm run preview
```

---

## Vignettes

The Individual Cases section contains seven documented accounts of named individuals drawn entirely from published media reporting. Each vignette includes demographic metadata, detention length, outcome, narrative text, and links to primary sources. The four individuals with available portrait images are Kilmar Abrego Garcia, Godfrey Wade, Any Lucia Lopez Belloza, and Mohammed Hoque. Portrait images are stored in `public/` and served as static assets.

Sources include NPR, CNN, Reuters, CalMatters, the Oregon Capital Chronicle, the Atlanta News First, PayDay Report, the Sahan Journal, and Fox 9 KMSP, with reporting dates ranging from 2025 to 2026.

---

## Deployment

The app is deployed on Vercel via automatic integration with this GitHub repository. Every push to `main` triggers a new production deployment. No environment variables or build configuration beyond the defaults in `vite.config.js` are required.
