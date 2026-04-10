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

function applyFilters(records, filters, yearBounds) {
  return records.filter((record) => {
    for (const key of dimensionKeys) {
      if (filters[key] !== "All" && record[key] !== filters[key]) {
        return false;
      }
    }

    if (!yearBounds) {
      return true;
    }

    return record.booking_year >= yearBounds.yearStart && record.booking_year <= yearBounds.yearEnd;
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

export function useData(primaryFilters, comparisonFilters) {
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
    const yearBounds = {
      yearStart: primaryFilters.yearStart,
      yearEnd: primaryFilters.yearEnd,
    };

    const filteredPrimary = applyFilters(records, primaryFilters, yearBounds);
    const filteredComparison = applyFilters(records, comparisonFilters, yearBounds);
    const outcomes = ["Released", "Removed", "Transferred", "Still Detained"];

    const outcomeCountsAll = countBy(records, "outcome");
    const outcomeCountsPrimary = countBy(filteredPrimary, "outcome");
    const outcomeCountsComparison = countBy(filteredComparison, "outcome");

    const selectedOutcomeShare = toShare(outcomeCountsPrimary, outcomes);
    const comparisonOutcomeShare = toShare(outcomeCountsComparison, outcomes);
    const overallOutcomeShare = toShare(outcomeCountsAll, outcomes);

    const primaryRatio = records.length > 0 ? filteredPrimary.length / records.length : 1;
    const comparisonRatio = records.length > 0 ? filteredComparison.length / records.length : 1;
    const timeSeries = {
      selected: processedData.timeSeries.map((row) => ({
        ...row,
        population: Math.max(1, Math.round(row.population * primaryRatio)),
      })),
      comparison: processedData.timeSeries.map((row) => ({
        ...row,
        population: Math.max(1, Math.round(row.population * comparisonRatio)),
      })),
      overall: processedData.timeSeries,
    };

    const facilityRollupSelected = d3.rollup(
      filteredPrimary,
      (group) => group.length,
      (d) => d.facility_id
    );
    const facilityRollupComparison = d3.rollup(
      filteredComparison,
      (group) => group.length,
      (d) => d.facility_id
    );
    const facilityRollupOverall = d3.rollup(
      records,
      (group) => group.length,
      (d) => d.facility_id
    );

    const facilities = processedData.facilities.map((facility) => ({
      ...facility,
      selectedCount: facilityRollupSelected.get(facility.facility_id) || 0,
      comparisonCount: facilityRollupComparison.get(facility.facility_id) || 0,
      overallCount: facilityRollupOverall.get(facility.facility_id) || 0,
    }));

    const selectedLengths = filteredPrimary
      .map((d) => d.detention_length_days)
      .filter((value) => Number.isFinite(value));
    const comparisonLengths = filteredComparison
      .map((d) => d.detention_length_days)
      .filter((value) => Number.isFinite(value));
    const overallLengths = records
      .map((d) => d.detention_length_days)
      .filter((value) => Number.isFinite(value));

    const bookingSankeyData = buildBookingSankey(filteredPrimary.length ? filteredPrimary : records);
    const convictionReleaseSankeyData = processedData.convictionReleaseSankey;

    const summary = {
      filteredCount: filteredPrimary.length,
      comparisonCount: filteredComparison.length,
      totalCount: records.length,
      dominantOutcome:
        Object.entries(outcomeCountsPrimary).sort((a, b) => b[1] - a[1])[0]?.[0] ||
        "N/A",
      comparisonDominantOutcome:
        Object.entries(outcomeCountsComparison).sort((a, b) => b[1] - a[1])[0]?.[0] ||
        "N/A",
    };

    return {
      filterOptions: computeOptions(records),
      records,
      filtered: filteredPrimary,
      comparisonFiltered: filteredComparison,
      timeSeries,
      facilities,
      selectedOutcomeShare,
      comparisonOutcomeShare,
      overallOutcomeShare,
      selectedLengths,
      comparisonLengths,
      overallLengths,
      bookingSankeyData,
      convictionReleaseSankeyData,
      summary,
      isLoading,
      loadError,
    };
  }, [comparisonFilters, isLoading, loadError, primaryFilters, processedData]);
}