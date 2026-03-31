import * as d3 from "d3";

export function createLinearScale(domain, range) {
  return d3.scaleLinear().domain(domain).range(range).nice();
}

export function createBandScale(domain, range, padding = 0.2) {
  return d3.scaleBand().domain(domain).range(range).padding(padding);
}

export function createColorScale(keys) {
  const palette = ["#0f5a6b", "#31755a", "#c7802e", "#ad3f2f", "#7d4f85"];
  return d3.scaleOrdinal().domain(keys).range(palette);
}