export default function Methodology() {
    return (
        <section className="story-footer methodology" id="methodology">
            <h3>Methodology Notes</h3>
            <p>
                Data come from the Deportation Data Project processed ICE release
                (downloaded February 17, 2026). For this site, the detention-stays
                dataset is transformed into a web-optimized file via
                preprocess_for_web.py.
            </p>

            <ul className="methodology-list">
                <li>
                    The raw dataset contains hundreds of thousands of records, so the UI
                    uses a 40,000-row random sample for responsive filtering.
                </li>
                <li>
                    Yearly trend totals and facility totals are computed from the full
                    dataset, then scaled by active filters for comparison views.
                </li>
                <li>
                    Several fields are harmonized to match the dashboard schema:
                    gender-to-sex, birth-year-to-age-group, citizenship-country-to-region,
                    and release reasons grouped into Removed, Released, Transferred, and
                    Still Detained.
                </li>
                <li>
                    Facility coordinates are joined from the lookup table by facility code
                    and displayed only when valid latitude and longitude are available.
                </li>
            </ul>

            <p>
                This is an exploratory visualization and should not be interpreted as an
                official causal analysis. Sampling and category harmonization choices can
                affect subgroup estimates.
            </p>
            <p className="methodology-meta">
                Government data provided by ICE in response to a
                FOIA request, processed by the Deportation Data Project, and analyzed by
                this project team.
            </p>
        </section>
    );
}