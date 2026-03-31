import { useMemo, useState } from "react";
import * as d3 from "d3";
import { formatNumber } from "../utils/formatters";

const width = 520;
const height = 300;
const margin = { top: 12, right: 14, bottom: 18, left: 14 };

export default function MapPlaceholder({ data }) {
  const [hovered, setHovered] = useState(null);

  const xScale = useMemo(
    () =>
      d3
        .scaleLinear()
        .domain([-125, -66])
        .range([margin.left, width - margin.right]),
    []
  );
  const yScale = useMemo(
    () => d3.scaleLinear().domain([24, 50]).range([height - margin.bottom, margin.top]),
    []
  );

  const radiusScale = useMemo(() => {
    const max = d3.max(data, (d) => d.count) ?? 1;
    return d3.scaleSqrt().domain([0, max]).range([2, 14]);
  }, [data]);

  return (
    <div className="viz-card">
      <h4 className="viz-title">Facility Footprint (Map Placeholder)</h4>
      <svg viewBox={`0 0 ${width} ${height}`} width="100%" height="300">
        <rect x="0" y="0" width={width} height={height} fill="#f1efe8" />

        <path
          d="M40,60 L170,40 L250,55 L350,45 L470,85 L495,140 L462,205 L380,235 L280,250 L170,230 L90,210 L55,170 L45,110 Z"
          fill="#ddd8cc"
          stroke="#c2baa8"
        />

        {data.map((facility) => (
          <g key={facility.facility_id}>
            <circle
              cx={xScale(facility.lng)}
              cy={yScale(facility.lat)}
              r={radiusScale(facility.count)}
              fill="#0f5a6b"
              fillOpacity={0.65}
              stroke="#06343f"
              style={{ transition: "all 300ms ease" }}
              onMouseEnter={(event) =>
                setHovered({
                  x: event.nativeEvent.offsetX,
                  y: event.nativeEvent.offsetY,
                  ...facility,
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
          </g>
        ))}
      </svg>

      {hovered && (
        <div className="tooltip" style={{ left: hovered.x, top: hovered.y }}>
          {hovered.name}: {formatNumber(hovered.count)} records
        </div>
      )}
    </div>
  );
}