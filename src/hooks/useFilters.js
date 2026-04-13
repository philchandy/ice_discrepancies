import React, { createContext, useContext, useMemo, useState } from "react";

const FilterContext = createContext(null);

const defaultPrimaryFilters = {
  sex: "All",
  age_group: "All",
  region_of_origin: "All",
  criminal_history: "All",
  first_booking_type: "All",
  yearStart: 2022,
  yearEnd: 2025,
};

const defaultComparisonFilters = {
  sex: "All",
  age_group: "All",
  region_of_origin: "All",
  criminal_history: "All",
  first_booking_type: "All",
};

const MIN_YEAR_CAP = 2022;

export function FilterProvider({ children }) {
  const [primaryFilters, setPrimaryFilters] = useState(defaultPrimaryFilters);
  const [comparisonFilters, setComparisonFilters] = useState(defaultComparisonFilters);

  const updatePrimaryFilter = (key, value) => {
    setPrimaryFilters((prev) => {
      if (key === "yearStart") {
        const nextStart = Math.max(MIN_YEAR_CAP, Number(value));
        return {
          ...prev,
          yearStart: Math.min(nextStart, prev.yearEnd),
        };
      }

      if (key === "yearEnd") {
        const nextEnd = Math.max(MIN_YEAR_CAP, Number(value));
        return {
          ...prev,
          yearEnd: Math.max(nextEnd, prev.yearStart),
        };
      }

      return { ...prev, [key]: value };
    });
  };

  const updateComparisonFilter = (key, value) => {
    setComparisonFilters((prev) => ({ ...prev, [key]: value }));
  };

  const resetFilters = () => {
    setPrimaryFilters(defaultPrimaryFilters);
    setComparisonFilters(defaultComparisonFilters);
  };

  const value = useMemo(
    () => ({
      primaryFilters,
      comparisonFilters,
      updatePrimaryFilter,
      updateComparisonFilter,
      resetFilters,
      defaultPrimaryFilters,
      defaultComparisonFilters,
    }),
    [primaryFilters, comparisonFilters]
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