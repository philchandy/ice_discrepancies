import { useMemo, useState } from "react";
import * as d3 from "d3";
import { sankey, sankeyLinkHorizontal } from "d3-sankey";
import { formatNumber } from "../utils/formatters";

const width = 1200;
const height = 560;

function formatNodeLabel(name) {
  return String(name)
    .replace(/^Conviction:\s*/, "")
    .replace(/^Release:\s*/, "");
}

export default function SankeyDiagram({
  data,
  title = "Pathways (Sankey)",
  emptyMessage = "No pathway data available for the current selection.",
}) {
  const [hoveredLink, setHoveredLink] = useState(null);

  const sanitizedData = useMemo(() => {
    const safeNodes = Array.isArray(data?.nodes) ? data.nodes : [];
    const safeLinks = Array.isArray(data?.links)
      ? data.links.filter(
          (link) =>
            typeof link?.source === "string" &&
            typeof link?.target === "string" &&
            Number.isFinite(link?.value) &&
            link.value > 0
        )
      : [];

    return { nodes: safeNodes, links: safeLinks };
  }, [data]);

  const hasRenderableGraph = sanitizedData.nodes.length > 0 && sanitizedData.links.length > 0;

  const graph = useMemo(() => {
    if (!hasRenderableGraph) {
      return { nodes: [], links: [] };
    }

    const generator = sankey()
      .nodeId((d) => d.name)
      .nodeWidth(22)
      .nodePadding(24)
      .extent([
        [28, 20],
        [width - 28, height - 20],
      ]);

    // Clone to keep d3-sankey mutations isolated from React props.
    const nodes = sanitizedData.nodes.map((d) => ({ ...d }));
    const links = sanitizedData.links.map((d) => ({ ...d }));
    return generator({ nodes, links });
  }, [hasRenderableGraph, sanitizedData.links, sanitizedData.nodes]);

  const color = useMemo(
    () => d3.scaleOrdinal().domain(graph.nodes.map((n) => n.name)).range(d3.schemeTableau10),
    [graph.nodes]
  );

  return (
    <div className="viz-card">
      <h4 className="viz-title">{title}</h4>
      {!hasRenderableGraph && (
        <p>{emptyMessage}</p>
      )}
      <svg viewBox={`0 0 ${width} ${height}`} width="100%" height="560">
        <g>
          {graph.links.map((link, index) => (
            <path
              key={`${link.source.name}-${link.target.name}-${index}`}
              d={sankeyLinkHorizontal()(link)}
              fill="none"
              stroke={color(link.source.name)}
              strokeWidth={Math.max(1, link.width)}
              strokeOpacity={
                hoveredLink === null
                  ? 0.45
                  : hoveredLink === index
                    ? 0.78
                    : 0.08
              }
              style={{ transition: "stroke-opacity 240ms ease" }}
              onMouseEnter={() => setHoveredLink(index)}
              onMouseLeave={() => setHoveredLink(null)}
            />
          ))}
        </g>

        <g>
          {graph.nodes.map((node) => (
            <g key={node.name}>
              <rect
                x={node.x0}
                y={node.y0}
                width={node.x1 - node.x0}
                height={Math.max(1, node.y1 - node.y0)}
                fill={color(node.name)}
                fillOpacity="0.88"
                stroke="#fff"
                strokeWidth="1"
              />
              <text
                x={node.x0 < width / 2 ? node.x1 + 6 : node.x0 - 6}
                y={(node.y0 + node.y1) / 2}
                dy="0.35em"
                textAnchor={node.x0 < width / 2 ? "start" : "end"}
                fontSize="13"
                fill="#2d3b48"
              >
                {formatNodeLabel(node.name)}
              </text>
            </g>
          ))}
        </g>
      </svg>

      <p>
        Hover links to isolate pathways. Current flow count: {formatNumber(d3.sum(graph.links, (d) => d.value))}
      </p>
    </div>
  );
}