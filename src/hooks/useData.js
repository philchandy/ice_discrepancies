import { useMemo } from "react";
import * as d3 from "d3";
import processedData from "../data/processedData.json";

const dimensionKeys = [
  "sex",
  "age_group",
  "region_of_origin",
  "criminal_history",
  "first_booking_type",
];

function applyFilters(records, filters) {
  return records.filter((record) => {
    for (const key of dimensionKeys) {
      if (filters[key] !== "All" && record[key] !== filters[key]) {
        return false;
      }
    }

    return (
      record.booking_year >= filters.yearStart &&
      record.booking_year <= filters.yearEnd
    );
  });
}

function computeOptions(records) {
  const options = {};
  for (const key of dimensionKeys) {
    options[key] = ["All", ...new Set(records.map((d) => d[key]))];
  }

  const years = records.map((d) => d.booking_year);
  options.yearBounds = {
    min: d3.min(years) ?? 2018,
    max: d3.max(years) ?? 2025,
  };

  return options;
}

function countBy(records, key) {
  const result = {};
  records.forEach((row) => {
    result[row[key]] = (result[row[key]] || 0) + 1;
  });
  return result;
}

function toShare(counts, referenceKeys) {
  const total = d3.sum(Object.values(counts));
  const share = {};
  referenceKeys.forEach((key) => {
    share[key] = total > 0 ? (counts[key] || 0) / total : 0;
  });
  return share;
}

function buildSankey(records) {
  const linksMap = new Map();

  const bump = (source, target, value) => {
    const id = `${source}__${target}`;
    linksMap.set(id, {
      source,
      target,
      value: (linksMap.get(id)?.value || 0) + value,
    });
  };

  records.forEach((row) => {
    bump(`Booking: ${row.first_booking_type}`, `Transfer: ${row.transfer_type}`, 1);
    bump(`Transfer: ${row.transfer_type}`, `Outcome: ${row.outcome}`, 1);
  });

  const links = Array.from(linksMap.values()).filter((d) => d.value > 0);
  const nodes = Array.from(
    new Set(links.flatMap((link) => [link.source, link.target]))
  ).map((name) => ({ name }));

  return { nodes, links };
}

export function useData(filters) {
  return useMemo(() => {
    const records = processedData.records;
    const filtered = applyFilters(records, filters);
    const outcomes = ["Released", "Removed", "Transferred", "Still Detained"];

    const outcomeCountsAll = countBy(records, "outcome");
    const outcomeCountsFiltered = countBy(filtered, "outcome");

    const selectedOutcomeShare = toShare(outcomeCountsFiltered, outcomes);
    const overallOutcomeShare = toShare(outcomeCountsAll, outcomes);

    // Scale full-dataset time series by the current filter ratio so the line
    // chart reflects the selected subgroup while preserving real magnitudes.
    const filterRatio = records.length > 0 ? filtered.length / records.length : 1;
    const timeSeries = processedData.timeSeries.map((row) => ({
      ...row,
      population: Math.max(1, Math.round(row.population * filterRatio)),
    }));

    const facilityRollup = d3.rollup(
      filtered,
      (group) => group.length,
      (d) => d.facility_id
    );

    const facilities = processedData.facilities.map((facility) => ({
      ...facility,
      count: facilityRollup.get(facility.facility_id) || 0,
    }));

    const selectedLengths = filtered.map((d) => d.detention_length_days);
    const overallLengths = records.map((d) => d.detention_length_days);

    const sankeyData = buildSankey(filtered.length ? filtered : records);

    const summary = {
      filteredCount: filtered.length,
      totalCount: records.length,
      dominantOutcome:
        Object.entries(outcomeCountsFiltered).sort((a, b) => b[1] - a[1])[0]?.[0] ||
        "N/A",
    };

    return {
      filterOptions: computeOptions(records),
      records,
      filtered,
      timeSeries,
      facilities,
      selectedOutcomeShare,
      overallOutcomeShare,
      selectedLengths,
      overallLengths,
      sankeyData,
      summary,
    };
  }, [filters]);
}