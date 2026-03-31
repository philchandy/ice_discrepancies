import { useMemo, useState } from "react";
import * as d3 from "d3";
import { sankey, sankeyLinkHorizontal } from "d3-sankey";
import { formatNumber } from "../utils/formatters";

const width = 920;
const height = 420;

export default function SankeyDiagram({ data }) {
  const [hoveredLink, setHoveredLink] = useState(null);

  const graph = useMemo(() => {
    const generator = sankey()
      .nodeId((d) => d.name)
      .nodeWidth(16)
      .nodePadding(18)
      .extent([
        [20, 16],
        [width - 20, height - 18],
      ]);

    // Clone to keep d3-sankey mutations isolated from React props.
    const nodes = data.nodes.map((d) => ({ ...d }));
    const links = data.links.map((d) => ({ ...d }));
    return generator({ nodes, links });
  }, [data]);

  const color = useMemo(
    () => d3.scaleOrdinal().domain(graph.nodes.map((n) => n.name)).range(d3.schemeTableau10),
    [graph.nodes]
  );

  return (
    <div className="viz-card">
      <h4 className="viz-title">Pathways: Booking to Outcome (Sankey)</h4>
      <svg viewBox={`0 0 ${width} ${height}`} width="100%" height="420">
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
                fontSize="11"
                fill="#2d3b48"
              >
                {node.name}
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