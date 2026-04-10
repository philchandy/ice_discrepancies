import { useMemo } from "react";
import { useFilters } from "../hooks/useFilters";

const labels = {
  sex: "Sex",
  age_group: "Age Group",
  region_of_origin: "Region of Origin",
  criminal_history: "Criminal History",
  first_booking_type: "First Booking Type",
};

export default function Filters({ options }) {
  const {
    primaryFilters,
    comparisonFilters,
    updatePrimaryFilter,
    updateComparisonFilter,
    resetFilters,
  } = useFilters();

  const fields = useMemo(
    () => ["sex", "age_group", "region_of_origin", "criminal_history", "first_booking_type"],
    []
  );

  return (
    <div className="filters">
      <h3>Demographic Selectors</h3>

      <div className="filter-columns">
        <div className="filter-column">
          <div className="filter-section-title">Group A</div>
          {fields.map((field) => (
            <div className="filter-group" key={`primary-${field}`}>
              <label htmlFor={`primary-filter-${field}`}>{labels[field]}</label>
              <select
                id={`primary-filter-${field}`}
                value={primaryFilters[field]}
                onChange={(event) => updatePrimaryFilter(field, event.target.value)}
              >
                {(options[field] || ["All"]).map((value) => (
                  <option key={value} value={value}>
                    {value}
                  </option>
                ))}
              </select>
            </div>
          ))}
        </div>

        <div className="filter-column">
          <div className="filter-section-title">Group B</div>
          {fields.map((field) => (
            <div className="filter-group" key={`comparison-${field}`}>
              <label htmlFor={`comparison-filter-${field}`}>{labels[field]}</label>
              <select
                id={`comparison-filter-${field}`}
                value={comparisonFilters[field]}
                onChange={(event) => updateComparisonFilter(field, event.target.value)}
              >
                {(options[field] || ["All"]).map((value) => (
                  <option key={value} value={value}>
                    {value}
                  </option>
                ))}
              </select>
            </div>
          ))}
        </div>
      </div>

      <div className="filter-group">
        <label>Year Range</label>
        <div className="year-range">
          <input
            type="number"
            min={options.yearBounds?.min}
            max={primaryFilters.yearEnd}
            value={primaryFilters.yearStart}
            onChange={(event) => updatePrimaryFilter("yearStart", Number(event.target.value))}
          />
          <input
            type="number"
            min={primaryFilters.yearStart}
            max={options.yearBounds?.max}
            value={primaryFilters.yearEnd}
            onChange={(event) => updatePrimaryFilter("yearEnd", Number(event.target.value))}
          />
        </div>
      </div>

      <button className="clear-btn" type="button" onClick={resetFilters}>
        Reset Filters
      </button>
    </div>
  );
}