import { formatPercent, formatNumber } from "../utils/formatters";

export default function InsightPanel({ selectedOutcomeShare, overallOutcomeShare, summary }) {
  const removedDelta = selectedOutcomeShare.Removed - overallOutcomeShare.Removed;
  const detainedDelta =
    selectedOutcomeShare["Still Detained"] - overallOutcomeShare["Still Detained"];

  const removedSentence =
    removedDelta >= 0
      ? `People in this group were ${(removedDelta * 100).toFixed(1)}% more likely to be removed than average.`
      : `People in this group were ${Math.abs(removedDelta * 100).toFixed(1)}% less likely to be removed than average.`;

  const detentionSentence =
    detainedDelta >= 0
      ? `The group shows a ${(detainedDelta * 100).toFixed(1)}% higher share still detained.`
      : `The group shows a ${Math.abs(detainedDelta * 100).toFixed(1)}% lower share still detained.`;

  return (
    <div className="viz-card">
      <h4 className="viz-title">Dynamic Insights</h4>

      <div className="insight-grid">
        <article className="insight-block">
          <p>Filtered Records</p>
          <div className="insight-value">{formatNumber(summary.filteredCount)}</div>
          <p>out of {formatNumber(summary.totalCount)} synthetic records</p>
        </article>

        <article className="insight-block">
          <p>Dominant Outcome</p>
          <div className="insight-value">{summary.dominantOutcome}</div>
          <p>highest share in the selected group</p>
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
    </div>
  );
}