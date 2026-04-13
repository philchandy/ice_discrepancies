import { useEffect, useMemo, useRef, useState } from "react";
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
    label: "Group A",
    countKey: "selectedCount",
    color: "#0f5a6b",
    stroke: "#06343f",
    dx: -6,
    dy: -4,
  },
  {
    key: "comparison",
    label: "Group B",
    countKey: "comparisonCount",
    color: "#6c80b5",
    stroke: "#41526f",
    dx: 0,
    dy: 0,
  },
  {
    key: "overall",
    label: "Overall Population",
    countKey: "overallCount",
    color: "#ad3f2f",
    stroke: "#7a271b",
    dx: 6,
    dy: 4,
  },
];

export default function MapPlaceholder({ data }) {
  const [hovered, setHovered] = useState(null);
  const [zoomTransform, setZoomTransform] = useState(d3.zoomIdentity);
  const svgRef = useRef(null);
  const zoomBehaviorRef = useRef(null);

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

  const activeGroups = useMemo(() => {
    const selectedDiffersFromOverall = projectedFacilities.some(
      (facility) => (facility.selectedCount || 0) !== (facility.overallCount || 0)
    );
    const comparisonDiffersFromOverall = projectedFacilities.some(
      (facility) => (facility.comparisonCount || 0) !== (facility.overallCount || 0)
    );

    if (!selectedDiffersFromOverall && !comparisonDiffersFromOverall) {
      return mapGroups.filter((group) => group.key === "overall");
    }

    if (!selectedDiffersFromOverall) {
      return mapGroups.filter((group) => group.key !== "selected");
    }

    if (!comparisonDiffersFromOverall) {
      return mapGroups.filter((group) => group.key !== "comparison");
    }

    return mapGroups;
  }, [projectedFacilities]);

  const radiusScale = useMemo(() => {
    const max =
      d3.max(projectedFacilities, (d) =>
        d3.max(activeGroups, (group) => d[group.countKey] || 0)
      ) ?? 1;
    return d3.scaleSqrt().domain([0, max]).range([2, 14]);
  }, [activeGroups, projectedFacilities]);

  const maxBubbleCount = radiusScale.domain()[1] ?? 1;
  const sizeLegendValues = useMemo(
    () =>
      Array.from(
        new Set([
          Math.max(1, Math.round(maxBubbleCount * 0.25)),
          Math.max(1, Math.round(maxBubbleCount * 0.6)),
          Math.max(1, Math.round(maxBubbleCount)),
        ])
      ),
    [maxBubbleCount]
  );

  useEffect(() => {
    if (!svgRef.current) return;

    const selection = d3.select(svgRef.current);
    const zoomBehavior = d3
      .zoom()
      .scaleExtent([1, 8])
      .extent([
        [0, 0],
        [width, height],
      ])
      .translateExtent([
        [0, 0],
        [width, height],
      ])
      .on("zoom", (event) => {
        setZoomTransform(event.transform);
      });

    zoomBehaviorRef.current = zoomBehavior;
    selection.call(zoomBehavior);

    return () => {
      selection.on(".zoom", null);
    };
  }, []);

  const zoomIn = () => {
    if (!svgRef.current || !zoomBehaviorRef.current) return;
    d3.select(svgRef.current).transition().duration(200).call(zoomBehaviorRef.current.scaleBy, 1.25);
  };

  const zoomOut = () => {
    if (!svgRef.current || !zoomBehaviorRef.current) return;
    d3.select(svgRef.current).transition().duration(200).call(zoomBehaviorRef.current.scaleBy, 0.8);
  };

  const resetZoom = () => {
    if (!svgRef.current || !zoomBehaviorRef.current) return;
    d3.select(svgRef.current)
      .transition()
      .duration(220)
      .call(zoomBehaviorRef.current.transform, d3.zoomIdentity);
  };

  return (
    <div className="viz-card">
      <div className="map-header">
        <h4 className="viz-title">Facility Footprint (US Map)</h4>
        <div className="map-controls" aria-label="Map zoom controls">
          <button type="button" className="map-control-btn" onClick={zoomOut} aria-label="Zoom out">
            -
          </button>
          <button type="button" className="map-control-btn" onClick={zoomIn} aria-label="Zoom in">
            +
          </button>
          <button type="button" className="map-control-btn map-control-reset" onClick={resetZoom}>
            Reset
          </button>
        </div>
      </div>

      <svg ref={svgRef} viewBox={`0 0 ${width} ${height}`} width="100%" height="300" className="zoomable-map">
        <g transform={zoomTransform.toString()}>
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
              {activeGroups.map((group) => {
                const count = facility[group.countKey] || 0;
                if (count <= 0) return null;

                return (
                  <circle
                    key={`${facility.facility_id}-${group.key}`}
                    cx={facility.x + group.dx}
                    cy={facility.y + group.dy}
                    r={radiusScale(count)}
                    fill={group.color}
                    fillOpacity={0.62}
                    stroke={group.stroke}
                    strokeWidth="1.2"
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
        </g>
      </svg>

      <div className="legend">
        {activeGroups.map((group) => (
          <span key={group.key} className="legend-item">
            <span className="legend-swatch" style={{ backgroundColor: group.color }} />
            {group.label}
          </span>
        ))}
      </div>

      <div className="map-readability-note">Color indicates cohort. Bubble size indicates record count at a facility.</div>

      <div className="size-legend" aria-label="Bubble size legend">
        {sizeLegendValues.map((value) => (
          <span key={value} className="size-legend-item">
            <span className="size-legend-dot" style={{ width: radiusScale(value) * 2, height: radiusScale(value) * 2 }} />
            {formatNumber(value)}
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