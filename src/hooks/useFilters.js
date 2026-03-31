import React, { createContext, useContext, useMemo, useState } from "react";

const FilterContext = createContext(null);

const defaultFilters = {
  sex: "All",
  age_group: "All",
  region_of_origin: "All",
  criminal_history: "All",
  first_booking_type: "All",
  yearStart: 2018,
  yearEnd: 2025,
};

export function FilterProvider({ children }) {
  const [filters, setFilters] = useState(defaultFilters);

  const updateFilter = (key, value) => {
    setFilters((prev) => ({ ...prev, [key]: value }));
  };

  const resetFilters = () => {
    setFilters(defaultFilters);
  };

  const value = useMemo(
    () => ({ filters, updateFilter, resetFilters, defaultFilters }),
    [filters]
  );

  return React.createElement(FilterContext.Provider, { value }, children);
}

export function useFilters() {
  const context = useContext(FilterContext);
  if (!context) {
    throw new Error("useFilters must be used within FilterProvider");
  }
  return context;
}