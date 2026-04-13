import { useMemo, useState } from "react";
import { createBandScale, createColorScale, createLinearScale } from "../utils/scales";
import { formatPercent } from "../utils/formatters";

const width = 800;
const height = 260;
const margin = { top: 20, right: 20, bottom: 42, left: 120 };
const outcomes = ["Released", "Removed", "Transferred", "Still Detained"];

export default function StackedBar({
  selectedOutcomeShare,
  comparisonOutcomeShare,
  overallOutcomeShare,
}) {
  const [hovered, setHovered] = useState(null);
  const colorScale = useMemo(() => createColorScale(outcomes), []);

  const rows = useMemo(
    () => [
      { group: "Group A", shares: selectedOutcomeShare },
      { group: "Group B", shares: comparisonOutcomeShare },
      { group: "Overall Population", shares: overallOutcomeShare },
    ],
    [comparisonOutcomeShare, overallOutcomeShare, selectedOutcomeShare]
  );

  const xScale = useMemo(() => createLinearScale([0, 1], [margin.left, width - margin.right]), []);
  const yScale = useMemo(
    () => createBandScale(rows.map((d) => d.group), [margin.top, height - margin.bottom], 0.35),
    [rows]
  );

  return (
    <div className="viz-card">
      <h4 className="viz-title">Outcome Composition</h4>
      <svg viewBox={`0 0 ${width} ${height}`} width="100%" height="280">
        {rows.map((row) => {
          let cumulative = 0;
          return outcomes.map((outcome) => {
            const value = row.shares[outcome] || 0;
            const x0 = xScale(cumulative);
            const x1 = xScale(cumulative + value);
            cumulative += value;

            return (
              <rect
                key={`${row.group}-${outcome}`}
                x={x0}
                y={yScale(row.group)}
                width={Math.max(0, x1 - x0)}
                height={yScale.bandwidth()}
                fill={colorScale(outcome)}
                opacity={hovered && hovered.outcome !== outcome ? 0.35 : 0.9}
                style={{ transition: "all 500ms ease" }}
                onMouseEnter={(event) =>
                  setHovered({
                    x: event.nativeEvent.offsetX,
                    y: event.nativeEvent.offsetY,
                    group: row.group,
                    outcome,
                    value,
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
            );
          });
        })}

        {rows.map((row) => (
          <text
            key={row.group}
            x={margin.left - 10}
            y={(yScale(row.group) || 0) + yScale.bandwidth() / 2 + 5}
            textAnchor="end"
            fontSize="12"
            fill="#40505d"
          >
            {row.group}
          </text>
        ))}
      </svg>

      <div className="legend">
        {outcomes.map((outcome) => (
          <span key={outcome} className="legend-item">
            <span className="legend-swatch" style={{ backgroundColor: colorScale(outcome) }} />
            {outcome}
          </span>
        ))}
      </div>

      {hovered && (
        <div className="tooltip" style={{ left: hovered.x, top: hovered.y }}>
          {hovered.group} - {hovered.outcome}: {formatPercent(hovered.value)}
        </div>
      )}
    </div>
  );
}