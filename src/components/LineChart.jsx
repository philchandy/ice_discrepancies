import { useEffect, useMemo, useRef, useState } from "react";
import * as d3 from "d3";
import { createLinearScale } from "../utils/scales";
import { formatNumber } from "../utils/formatters";

const width = 520;
const height = 300;
const margin = { top: 16, right: 20, bottom: 36, left: 48 };

export default function LineChart({ data }) {
  const [hovered, setHovered] = useState(null);
  const xAxisRef = useRef(null);
  const yAxisRef = useRef(null);

  const series = useMemo(
    () => [
      {
        key: "selected",
        label: "Selected Group (A)",
        color: "#0f5a6b",
        values: data?.selected || [],
      },
      {
        key: "comparison",
        label: "Comparison Group (B)",
        color: "#6c80b5",
        values: data?.comparison || [],
      },
      {
        key: "overall",
        label: "Overall Population",
        color: "#ad3f2f",
        values: data?.overall || [],
      },
    ],
    [data]
  );

  const allPoints = useMemo(
    () => series.flatMap((group) => group.values),
    [series]
  );

  const xScale = useMemo(() => {
    const years = allPoints.map((d) => d.year);
    return createLinearScale(
      [d3.min(years) ?? 2018, d3.max(years) ?? 2025],
      [margin.left, width - margin.right]
    );
  }, [allPoints]);

  const yScale = useMemo(() => {
    const max = d3.max(allPoints, (d) => d.population) ?? 100;
    return createLinearScale([0, max], [height - margin.bottom, margin.top]);
  }, [allPoints]);

  useEffect(() => {
    const xAxis = d3.axisBottom(xScale).ticks(6).tickFormat(d3.format("d"));
    const yAxis = d3.axisLeft(yScale).ticks(5);
    d3.select(xAxisRef.current).call(xAxis);
    d3.select(yAxisRef.current).call(yAxis);
  }, [xScale, yScale]);

  const lineGenerator = useMemo(
    () =>
      d3
        .line()
        .x((d) => xScale(d.year))
        .y((d) => yScale(d.population))
        .curve(d3.curveMonotoneX),
    [xScale, yScale]
  );

  return (
    <div className="viz-card">
      <h4 className="viz-title">Detained Population Over Time</h4>
      <svg viewBox={`0 0 ${width} ${height}`} width="100%" height="300">
        <g className="axis" ref={xAxisRef} transform={`translate(0, ${height - margin.bottom})`} />
        <g className="axis" ref={yAxisRef} transform={`translate(${margin.left}, 0)`} />

        {series.map((group) => (
          <g key={group.key}>
            <path
              d={lineGenerator(group.values) || ""}
              fill="none"
              stroke={group.color}
              strokeWidth="2.5"
              strokeOpacity={hovered && hovered.group !== group.label ? 0.35 : 0.95}
            />

            {group.values.map((point) => (
              <circle
                key={`${group.key}-${point.year}`}
                cx={xScale(point.year)}
                cy={yScale(point.population)}
                r={hovered?.group === group.label && hovered?.year === point.year ? 5 : 3.2}
                fill={group.color}
                style={{ transition: "all 250ms ease" }}
                onMouseEnter={(event) =>
                  setHovered({
                    x: event.nativeEvent.offsetX,
                    y: event.nativeEvent.offsetY,
                    group: group.label,
                    year: point.year,
                    population: point.population,
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
            ))}
          </g>
        ))}
      </svg>

      <div className="legend">
        {series.map((group) => (
          <span key={group.key} className="legend-item">
            <span className="legend-swatch" style={{ backgroundColor: group.color }} />
            {group.label}
          </span>
        ))}
      </div>

      {hovered && (
        <div className="tooltip" style={{ left: hovered.x, top: hovered.y }}>
          {hovered.group} • {hovered.year}: {formatNumber(hovered.population)}
        </div>
      )}
    </div>
  );
}