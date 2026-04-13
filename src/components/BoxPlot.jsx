import { useMemo, useState } from "react";
import * as d3 from "d3";
import { createBandScale, createLinearScale } from "../utils/scales";
import { formatDays } from "../utils/formatters";

const width = 800;
const height = 320;
const margin = { top: 16, right: 20, bottom: 36, left: 56 };

function computeStats(values) {
  if (!values.length) {
    return {
      min: 0,
      q1: 0,
      median: 0,
      q3: 0,
      max: 0,
      whiskerMin: 0,
      whiskerMax: 0,
      outliers: [],
    };
  }

  const sorted = [...values].sort(d3.ascending);
  const q1 = d3.quantileSorted(sorted, 0.25) ?? 0;
  const q3 = d3.quantileSorted(sorted, 0.75) ?? 0;
  const iqr = q3 - q1;
  const lowerFence = q1 - 1.5 * iqr;
  const upperFence = q3 + 1.5 * iqr;

  const inlierValues = sorted.filter((value) => value >= lowerFence && value <= upperFence);
  const outliers = sorted.filter((value) => value < lowerFence || value > upperFence);

  const whiskerMin = inlierValues.length ? d3.min(inlierValues) ?? 0 : d3.min(sorted) ?? 0;
  const whiskerMax = inlierValues.length ? d3.max(inlierValues) ?? 0 : d3.max(sorted) ?? 0;

  return {
    min: d3.min(sorted) ?? 0,
    q1,
    median: d3.quantileSorted(sorted, 0.5) ?? 0,
    q3,
    max: d3.max(sorted) ?? 0,
    whiskerMin,
    whiskerMax,
    outliers,
  };
}

export default function BoxPlot({ selectedLengths, comparisonLengths, overallLengths }) {
  const [hovered, setHovered] = useState(null);
  const groups = useMemo(
    () => [
      {
        key: "selected",
        label: "Group A",
        values: selectedLengths,
        fill: "#83b8c2",
      },
      {
        key: "comparison",
        label: "Group B",
        values: comparisonLengths,
        fill: "#c8d6f0",
      },
      {
        key: "overall",
        label: "Overall Population",
        values: overallLengths,
        fill: "#d5cfbd",
      },
    ],
    [comparisonLengths, overallLengths, selectedLengths]
  );

  const stats = useMemo(
    () => groups.map((group) => ({ ...group, stats: computeStats(group.values) })),
    [groups]
  );

  const yMax = d3.max(stats, (d) => d.stats.whiskerMax) ?? 1;
  const xScale = useMemo(
    () => createBandScale(stats.map((d) => d.label), [margin.left, width - margin.right], 0.4),
    [stats]
  );
  const yScale = useMemo(
    () => createLinearScale([0, yMax * 1.05], [height - margin.bottom, margin.top]),
    [yMax]
  );

  return (
    <div className="viz-card">
      <h4 className="viz-title">Detention Length Distribution (Box Plot)</h4>
      <svg viewBox={`0 0 ${width} ${height}`} width="100%" height="320">
        {stats.map((group) => {
          const x = xScale(group.label) || 0;
          const boxWidth = xScale.bandwidth();
          const center = x + boxWidth / 2;
          const s = group.stats;
          const q1Y = yScale(s.q1);
          const q3Y = yScale(s.q3);
          const boxHeight = Math.max(10, q1Y - q3Y);
          const boxY = q3Y - Math.max(0, 10 - (q1Y - q3Y)) / 2;

          return (
            <g key={group.key} style={{ transition: "all 450ms ease" }}>
              <line x1={center} x2={center} y1={yScale(s.whiskerMin)} y2={yScale(s.whiskerMax)} stroke="#415264" />
              <line x1={center - 20} x2={center + 20} y1={yScale(s.whiskerMin)} y2={yScale(s.whiskerMin)} stroke="#415264" />
              <line x1={center - 20} x2={center + 20} y1={yScale(s.whiskerMax)} y2={yScale(s.whiskerMax)} stroke="#415264" />

              <rect
                x={x}
                y={boxY}
                width={boxWidth}
                height={boxHeight}
                fill={group.fill}
                stroke="#0f5a6b"
                onMouseEnter={(event) =>
                  setHovered({
                    x: event.nativeEvent.offsetX,
                    y: event.nativeEvent.offsetY,
                    label: group.label,
                    ...s,
                  })
                }
                onMouseMove={(event) =>
                  setHovered((prev) =>
                    prev
                      ? {
                          ...prev,
                          x: event.nativeEvent.offsetX,
                          y: event.nativeEvent.offsetY,
                        }
                      : prev
                  )
                }
                onMouseLeave={() => setHovered(null)}
              />

              <line x1={x} x2={x + boxWidth} y1={yScale(s.median)} y2={yScale(s.median)} stroke="#ad3f2f" strokeWidth="2" />

              {s.outliers.map((value, index) => (
                <circle
                  key={`${group.key}-outlier-${index}`}
                  cx={center}
                  cy={yScale(value)}
                  r={2.2}
                  fill="#ad3f2f"
                  fillOpacity="0.75"
                />
              ))}

              <text x={center} y={height - 10} textAnchor="middle" fontSize="12" fill="#415264">
                {group.label}
              </text>
            </g>
          );
        })}
      </svg>

      {hovered && (
        <div className="tooltip" style={{ left: hovered.x, top: hovered.y }}>
          <div>{hovered.label}</div>
          <div>Median: {formatDays(hovered.median)}</div>
          <div>Q1-Q3: {formatDays(hovered.q1)} - {formatDays(hovered.q3)}</div>
          <div>Whiskers: {formatDays(hovered.whiskerMin)} - {formatDays(hovered.whiskerMax)}</div>
        </div>
      )}
    </div>
  );
}