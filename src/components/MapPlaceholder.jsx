import { useMemo, useState } from "react";
import * as d3 from "d3";
import { feature, mesh } from "topojson-client";
import usAtlas from "us-atlas/states-10m.json";
import { formatNumber } from "../utils/formatters";

const width = 520;
const height = 300;
const margin = { top: 12, right: 14, bottom: 18, left: 14 };
const mapGroups = [
  {
    key: "selected",
    label: "Selected Group (A)",
    countKey: "selectedCount",
    color: "#0f5a6b",
    stroke: "#06343f",
    dx: -4,
  },
  {
    key: "comparison",
    label: "Comparison Group (B)",
    countKey: "comparisonCount",
    color: "#6c80b5",
    stroke: "#41526f",
    dx: 0,
  },
  {
    key: "overall",
    label: "Overall Population",
    countKey: "overallCount",
    color: "#ad3f2f",
    stroke: "#7a271b",
    dx: 4,
  },
];

export default function MapPlaceholder({ data }) {
  const [hovered, setHovered] = useState(null);

  const nation = useMemo(
    () => feature(usAtlas, usAtlas.objects.nation),
    []
  );
  const states = useMemo(
    () => feature(usAtlas, usAtlas.objects.states).features,
    []
  );
  const stateBorders = useMemo(
    () => mesh(usAtlas, usAtlas.objects.states, (a, b) => a !== b),
    []
  );
  const projection = useMemo(
    () =>
      d3
        .geoAlbersUsa()
        .fitExtent(
          [
            [margin.left, margin.top],
            [width - margin.right, height - margin.bottom],
          ],
          nation
        ),
    [nation]
  );
  const path = useMemo(() => d3.geoPath(projection), [projection]);

  const projectedFacilities = useMemo(
    () =>
      data
        .map((facility) => {
          const point = projection([facility.lng, facility.lat]);
          if (!point) return null;
          return {
            ...facility,
            x: point[0],
            y: point[1],
          };
        })
        .filter(Boolean),
    [data, projection]
  );

  const radiusScale = useMemo(() => {
    const max =
      d3.max(projectedFacilities, (d) =>
        d3.max(mapGroups, (group) => d[group.countKey] || 0)
      ) ?? 1;
    return d3.scaleSqrt().domain([0, max]).range([2, 14]);
  }, [projectedFacilities]);

  return (
    <div className="viz-card">
      <h4 className="viz-title">Facility Footprint (US Map)</h4>
      <svg viewBox={`0 0 ${width} ${height}`} width="100%" height="300">
        <rect x="0" y="0" width={width} height={height} fill="#f1efe8" />

        <path d={path(nation) || undefined} fill="#ddd8cc" stroke="#c2baa8" />
        {states.map((state) => (
          <path
            key={state.id}
            d={path(state) || undefined}
            fill="#ddd8cc"
            stroke="none"
          />
        ))}
        <path
          d={path(stateBorders) || undefined}
          fill="none"
          stroke="#c2baa8"
          strokeWidth="0.6"
          vectorEffect="non-scaling-stroke"
        />

        {projectedFacilities.map((facility) => (
          <g key={facility.facility_id}>
            {mapGroups.map((group) => {
              const count = facility[group.countKey] || 0;
              if (count <= 0) return null;

              return (
                <circle
                  key={`${facility.facility_id}-${group.key}`}
                  cx={facility.x + group.dx}
                  cy={facility.y}
                  r={radiusScale(count)}
                  fill={group.color}
                  fillOpacity={0.62}
                  stroke={group.stroke}
                  style={{ transition: "all 300ms ease" }}
                  onMouseEnter={(event) =>
                    setHovered({
                      x: event.nativeEvent.offsetX,
                      y: event.nativeEvent.offsetY,
                      name: facility.name,
                      count,
                      group: group.label,
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
            })}
          </g>
        ))}
      </svg>

      <div className="legend">
        {mapGroups.map((group) => (
          <span key={group.key} className="legend-item">
            <span className="legend-swatch" style={{ backgroundColor: group.color }} />
            {group.label}
          </span>
        ))}
      </div>

      {hovered && (
        <div className="tooltip" style={{ left: hovered.x, top: hovered.y }}>
          {hovered.name} • {hovered.group}: {formatNumber(hovered.count)} records
        </div>
      )}
    </div>
  );
}