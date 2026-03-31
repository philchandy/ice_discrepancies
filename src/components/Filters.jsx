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
  const { filters, updateFilter, resetFilters } = useFilters();

  const fields = useMemo(
    () => ["sex", "age_group", "region_of_origin", "criminal_history", "first_booking_type"],
    []
  );

  return (
    <div className="filters">
      <h3>Demographic Selector</h3>

      {fields.map((field) => (
        <div className="filter-group" key={field}>
          <label htmlFor={`filter-${field}`}>{labels[field]}</label>
          <select
            id={`filter-${field}`}
            value={filters[field]}
            onChange={(event) => updateFilter(field, event.target.value)}
          >
            {(options[field] || ["All"]).map((value) => (
              <option key={value} value={value}>
                {value}
              </option>
            ))}
          </select>
        </div>
      ))}

      <div className="filter-group">
        <label>Year Range</label>
        <div className="year-range">
          <input
            type="number"
            min={options.yearBounds?.min}
            max={filters.yearEnd}
            value={filters.yearStart}
            onChange={(event) => updateFilter("yearStart", Number(event.target.value))}
          />
          <input
            type="number"
            min={filters.yearStart}
            max={options.yearBounds?.max}
            value={filters.yearEnd}
            onChange={(event) => updateFilter("yearEnd", Number(event.target.value))}
          />
        </div>
      </div>

      <button className="clear-btn" type="button" onClick={resetFilters}>
        Reset Filters
      </button>
    </div>
  );
}