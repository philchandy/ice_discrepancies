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

  const xScale = useMemo(() => {
    const years = data.map((d) => d.year);
    return createLinearScale(
      [d3.min(years) ?? 2018, d3.max(years) ?? 2025],
      [margin.left, width - margin.right]
    );
  }, [data]);

  const yScale = useMemo(() => {
    const max = d3.max(data, (d) => d.population) ?? 100;
    return createLinearScale([0, max], [height - margin.bottom, margin.top]);
  }, [data]);

  useEffect(() => {
    const xAxis = d3.axisBottom(xScale).ticks(6).tickFormat(d3.format("d"));
    const yAxis = d3.axisLeft(yScale).ticks(5);
    d3.select(xAxisRef.current).call(xAxis);
    d3.select(yAxisRef.current).call(yAxis);
  }, [xScale, yScale]);

  const linePath = useMemo(
    () =>
      d3
        .line()
        .x((d) => xScale(d.year))
        .y((d) => yScale(d.population))
        .curve(d3.curveMonotoneX)(data) || "",
    [data, xScale, yScale]
  );

  return (
    <div className="viz-card">
      <h4 className="viz-title">Detained Population Over Time</h4>
      <svg viewBox={`0 0 ${width} ${height}`} width="100%" height="300">
        <g className="axis" ref={xAxisRef} transform={`translate(0, ${height - margin.bottom})`} />
        <g className="axis" ref={yAxisRef} transform={`translate(${margin.left}, 0)`} />

        <path d={linePath} fill="none" stroke="#0f5a6b" strokeWidth="3" />

        {data.map((point) => (
          <circle
            key={point.year}
            cx={xScale(point.year)}
            cy={yScale(point.population)}
            r={hovered?.year === point.year ? 6 : 4}
            fill="#ad3f2f"
            style={{ transition: "all 250ms ease" }}
            onMouseEnter={(event) =>
              setHovered({
                x: event.nativeEvent.offsetX,
                y: event.nativeEvent.offsetY,
                ...point,
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
      </svg>

      {hovered && (
        <div className="tooltip" style={{ left: hovered.x, top: hovered.y }}>
          {hovered.year}: {formatNumber(hovered.population)}
        </div>
      )}
    </div>
  );
}