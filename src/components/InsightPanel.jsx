import { formatPercent, formatNumber } from "../utils/formatters";

export default function InsightPanel({
  selectedOutcomeShare,
  comparisonOutcomeShare,
  overallOutcomeShare,
  summary,
}) {
  const removedDelta = selectedOutcomeShare.Removed - overallOutcomeShare.Removed;
  const comparisonRemovedDelta = comparisonOutcomeShare.Removed - overallOutcomeShare.Removed;
  const detainedDelta =
    selectedOutcomeShare["Still Detained"] - overallOutcomeShare["Still Detained"];
  const comparisonDetainedDelta =
    comparisonOutcomeShare["Still Detained"] - overallOutcomeShare["Still Detained"];

  const removedSentence =
    removedDelta >= 0
      ? `People in Group A were ${(removedDelta * 100).toFixed(1)}% more likely to be removed than average.`
      : `People in Group A were ${Math.abs(removedDelta * 100).toFixed(1)}% less likely to be removed than average.`;

  const detentionSentence =
    detainedDelta >= 0
      ? `Group A shows a ${(detainedDelta * 100).toFixed(1)}% higher share still detained.`
      : `Group A shows a ${Math.abs(detainedDelta * 100).toFixed(1)}% lower share still detained.`;

  const comparisonRemovedSentence =
    comparisonRemovedDelta >= 0
      ? `People in Group B were ${(comparisonRemovedDelta * 100).toFixed(1)}% more likely to be removed than average.`
      : `People in Group B were ${Math.abs(comparisonRemovedDelta * 100).toFixed(1)}% less likely to be removed than average.`;

  const comparisonDetentionSentence =
    comparisonDetainedDelta >= 0
      ? `Group B shows a ${(comparisonDetainedDelta * 100).toFixed(1)}% higher share still detained.`
      : `Group B shows a ${Math.abs(comparisonDetainedDelta * 100).toFixed(1)}% lower share still detained.`;

  return (
    <div className="viz-card">
      <h4 className="viz-title">Dynamic Insights</h4>

      <div className="insight-grid">
        <article className="insight-block">
          <p>Group A Records</p>
          <div className="insight-value">{formatNumber(summary.filteredCount)}</div>
          <p>out of {formatNumber(summary.totalCount)} synthetic records</p>
        </article>

        <article className="insight-block">
          <p>Group B Records</p>
          <div className="insight-value">{formatNumber(summary.comparisonCount)}</div>
          <p>out of {formatNumber(summary.totalCount)} synthetic records</p>
        </article>
      </div>

      <div className="insight-grid" style={{ marginTop: "1rem" }}>
        <article className="insight-block">
          <p>Dominant Outcome (A)</p>
          <div className="insight-value">{summary.dominantOutcome}</div>
          <p>highest share in Group A</p>
        </article>

        <article className="insight-block">
          <p>Dominant Outcome (B)</p>
          <div className="insight-value">{summary.comparisonDominantOutcome}</div>
          <p>highest share in Group B</p>
        </article>
      </div>

      <div className="insight-grid" style={{ marginTop: "1rem" }}>
        <article className="insight-block">
          <p>{removedSentence}</p>
          <div className="insight-value">Removed: {formatPercent(selectedOutcomeShare.Removed)}</div>
        </article>

        <article className="insight-block">
          <p>{detentionSentence}</p>
          <div className="insight-value">
            Still Detained: {formatPercent(selectedOutcomeShare["Still Detained"])}
          </div>
        </article>
      </div>

      <div className="insight-grid" style={{ marginTop: "1rem" }}>
        <article className="insight-block">
          <p>{comparisonRemovedSentence}</p>
          <div className="insight-value">Removed: {formatPercent(comparisonOutcomeShare.Removed)}</div>
        </article>

        <article className="insight-block">
          <p>{comparisonDetentionSentence}</p>
          <div className="insight-value">
            Still Detained: {formatPercent(comparisonOutcomeShare["Still Detained"])}
          </div>
        </article>
      </div>
    </div>
  );
}