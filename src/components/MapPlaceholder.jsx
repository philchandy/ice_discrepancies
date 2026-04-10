import { useMemo, useState } from "react";
import * as d3 from "d3";
import { feature, mesh } from "topojson-client";
import usAtlas from "us-atlas/states-10m.json";
import { formatNumber } from "../utils/formatters";

const width = 520;
const height = 300;
const margin = { top: 12, right: 14, bottom: 18, left: 14 };

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
    const max = d3.max(projectedFacilities, (d) => d.count) ?? 1;
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

        {projectedFacilities
          .filter((facility) => facility.count > 0)
          .map((facility) => (
          <g key={facility.facility_id}>
            <circle
              cx={facility.x}
              cy={facility.y}
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