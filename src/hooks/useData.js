import { useEffect, useMemo, useState } from "react";
import * as d3 from "d3";

const emptyProcessedData = {
  records: [],
  timeSeries: [],
  facilities: [],
  convictionReleaseSankey: {
    nodes: [],
    links: [],
    metadata: {},
  },
};

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
    min: d3.min(years) ?? 2004,
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

function buildBookingSankey(records) {
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
  const [processedData, setProcessedData] = useState(emptyProcessedData);
  const [isLoading, setIsLoading] = useState(true);
  const [loadError, setLoadError] = useState(null);

  useEffect(() => {
    let isCancelled = false;

    async function loadData() {
      try {
        setIsLoading(true);
        setLoadError(null);

        const response = await fetch("/data/processedData.json", { cache: "no-store" });
        if (!response.ok) {
          throw new Error(`Failed to load processed data (${response.status})`);
        }

        const [json, sankeyJson] = await Promise.all([
          response.json(),
          fetch("/data/convictionReleaseSankey.json", { cache: "no-store" })
            .then((sankeyResponse) => {
              if (!sankeyResponse.ok) {
                throw new Error(`Failed to load conviction-release Sankey data (${sankeyResponse.status})`);
              }
              return sankeyResponse.json();
            })
            .catch(() => emptyProcessedData.convictionReleaseSankey),
        ]);

        if (!isCancelled) {
          setProcessedData({
            records: Array.isArray(json.records) ? json.records : [],
            timeSeries: Array.isArray(json.timeSeries) ? json.timeSeries : [],
            facilities: Array.isArray(json.facilities) ? json.facilities : [],
            convictionReleaseSankey: {
              nodes: Array.isArray(sankeyJson?.nodes) ? sankeyJson.nodes : [],
              links: Array.isArray(sankeyJson?.links) ? sankeyJson.links : [],
              metadata:
                sankeyJson && typeof sankeyJson.metadata === "object" && sankeyJson.metadata !== null
                  ? sankeyJson.metadata
                  : {},
            },
          });
        }
      } catch (error) {
        if (!isCancelled) {
          setLoadError(error.message || "Failed to load processed data");
        }
      } finally {
        if (!isCancelled) {
          setIsLoading(false);
        }
      }
    }

    loadData();
    return () => {
      isCancelled = true;
    };
  }, []);

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

    const selectedLengths = filtered
      .map((d) => d.detention_length_days)
      .filter((value) => Number.isFinite(value));
    const overallLengths = records
      .map((d) => d.detention_length_days)
      .filter((value) => Number.isFinite(value));

    const bookingSankeyData = buildBookingSankey(filtered.length ? filtered : records);
    const convictionReleaseSankeyData = processedData.convictionReleaseSankey;

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
      bookingSankeyData,
      convictionReleaseSankeyData,
      summary,
      isLoading,
      loadError,
    };
  }, [filters, isLoading, loadError, processedData]);
}