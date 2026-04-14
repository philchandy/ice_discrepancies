import { useEffect, useRef, useState } from "react";
import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";
import Hero from "./components/Hero";
import Filters from "./components/Filters";
import LineChart from "./components/LineChart";
import MapPlaceholder from "./components/MapPlaceholder";
import StackedBar from "./components/StackedBar";
import BoxPlot from "./components/BoxPlot";
import SankeyDiagram from "./components/SankeyDiagram";
import InsightPanel from "./components/InsightPanel";
import Methodology from "./components/Methodology";
import Infographic from "./components/Infographic";
import { FilterProvider, useFilters } from "./hooks/useFilters";
import { useData } from "./hooks/useData";

function StoryContent() {
  const [isVizVisible, setIsVizVisible] = useState(false);
  const vizLayoutRef = useRef(null);

  const { primaryFilters, comparisonFilters } = useFilters();
  const {
    filterOptions,
    timeSeries,
    facilities,
    selectedOutcomeShare,
    comparisonOutcomeShare,
    overallOutcomeShare,
    selectedLengths,
    comparisonLengths,
    overallLengths,
    bookingSankeyData,
    convictionReleaseSankeyData,
    summary,
    isLoading,
    loadError,
  } = useData(primaryFilters, comparisonFilters);

  useEffect(() => {
    const target = vizLayoutRef.current;
    if (!target) return;

    const observer = new IntersectionObserver(
      (entries) => {
        const [entry] = entries;
        if (entry.isIntersecting) {
          setIsVizVisible(true);
          observer.disconnect();
        }
      },
      {
        threshold: 0.14,
      }
    );

    observer.observe(target);
    return () => observer.disconnect();
  }, []);

  return (
    <div className="app-shell">
      <Hero />

      <div
        ref={vizLayoutRef}
        className={`story-layout ${isVizVisible ? "story-layout-visible" : "story-layout-hidden"}`}
      >
        <aside className="sidebar">
          <Filters options={filterOptions} />
        </aside>

        <main className="story-content">
          {isLoading && <div className="data-status">Loading processed data...</div>}
          {loadError && <div className="data-status data-status-error">{loadError}</div>}

          <section className="story-section" id="system-scale">
            <h2>System Scale</h2>
            <p className="section-lead">
              A high-level look at detention volume trends and facility footprint.
            </p>
            <div className="viz-grid">
              <LineChart
                data={timeSeries}
                yearStart={primaryFilters.yearStart}
                yearEnd={primaryFilters.yearEnd}
              />
              <MapPlaceholder data={facilities} />
            </div>
          </section>

          <section className="story-section" id="outcomes-comparison">
            <h2>Outcomes Comparison</h2>
            <p className="section-lead">
              Compare outcome composition for Group A, Group B,
              and the overall population.
            </p>
            <StackedBar
              selectedOutcomeShare={selectedOutcomeShare}
              comparisonOutcomeShare={comparisonOutcomeShare}
              overallOutcomeShare={overallOutcomeShare}
            />
          </section>

          <section className="story-section" id="detention-length">
            <h2>Detention Length</h2>
            <p className="section-lead">
              Distribution snapshots show how long people remain in detention
              across both selected groups and overall.
            </p>
            <BoxPlot
              selectedLengths={selectedLengths}
              comparisonLengths={comparisonLengths}
              overallLengths={overallLengths}
            />
          </section>

          <section className="story-section" id="pathways">
            <h2>System Pathways</h2>
            <p className="section-lead">
              Compare booking flows with conviction-to-release flows.
            </p>
            <div className="viz-grid">
              <SankeyDiagram
                data={bookingSankeyData}
                title="Group A: Booking to Transfer to Outcome"
                emptyMessage="No Group A booking pathway data available for the current selection."
              />
              <SankeyDiagram
                data={convictionReleaseSankeyData}
                title="Conviction (General) to Release Reason (Most General)"
                emptyMessage="No conviction-to-release Sankey data available."
              />
            </div>
          </section>

          <section className="story-section" id="insights">
            <h2>Insight Panel</h2>
            <InsightPanel
              selectedOutcomeShare={selectedOutcomeShare}
              comparisonOutcomeShare={comparisonOutcomeShare}
              overallOutcomeShare={overallOutcomeShare}
              summary={summary}
            />
          </section>
          
          <Methodology />

          <footer className="story-footer">
            <section>
              <div>
                Trends in Immigration, created by Max Feit, Sarah Witzig, and Phillip Chandy.
                For CS7250 at Northeastern University.
              </div>
            </section>
          </footer>
        </main>
      </div>
    </div>
  );
}

const Navigation = () => {
  return (
    <nav className="app-navigation">
      <div className="nav-container">
        <Link to="/" className="nav-link">Main Analysis</Link>
        <Link to="/infographic" className="nav-link">Infographic</Link>
      </div>
    </nav>
  );
};

export default function App() {
  return (
    <Router>
      <Navigation />
      <Routes>
        <Route
          path="/"
          element={
            <FilterProvider>
              <StoryContent />
            </FilterProvider>
          }
        />
        <Route path="/infographic" element={<Infographic />} />
      </Routes>
    </Router>
  );
}