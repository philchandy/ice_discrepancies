import { useState } from "react";

const VIGNETTES = [
  {
    id: "abrego-garcia",
    name: "Kilmar Abrego Garcia",
    tag: "El Salvador · 29 · Sheet metal worker, Maryland",
    image: "/kilmar-abrego-garcia.webp",
    demographics: {
      origin: "El Salvador",
      age: "26–35",
      sex: "Male",
      criminalHistory: "None on record",
      language: "Spanish",
    },
    detentionDays: 7,
    detentionNote: "Days detained before deportation",
    outcome: "Wrongly deported",
    outcomeType: "error",
    story: [
      "Abrego Garcia came to the US from El Salvador at 16, fleeing gang threats that had already forced his older brother to flee before him. He settled in Maryland, married a US citizen, and had three children, one of whom has autism. In 2019 an immigration judge found he had a credible fear of persecution and granted him protected status that explicitly barred his deportation to El Salvador, and that order was upheld on appeal.",
      "In March 2025 he was arrested after a work shift and deported to El Salvador's CECOT mega-prison within days, in acknowledged violation of his court-protected status. ICE called it an \"administrative error.\" His wife learned he was in CECOT from photos and video published after the deportation flights landed. The Supreme Court unanimously ordered his return. He was eventually brought back to the US in June 2025 — to face federal criminal charges of alleged human trafficking the government had filed under seal during the weeks it claimed it lacked any means of retrieving him. His attorneys characterize the indictment as retaliatory. The criminal case remains pending.",
    ],
    sources: [
      { label: "NPR · April 2025", url: "https://www.npr.org/2025/04/01/nx-s1-5347427/maryland-el-salvador-error" },
      { label: "AP News · April 2026", url: "https://apnews.com/article/abrego-garcia-deportation-liberia-costa-rica-immigration-e7f637d07f2135740c4d9a5d250661b9" },
    ],
  },
  {
    id: "wade",
    name: "Godfrey Wade",
    tag: "Jamaica · 65 · US Army veteran, Georgia",
    image: "/godfrey-wade.avif",
    demographics: {
      origin: "Caribbean",
      age: "51–65",
      sex: "Male",
      criminalHistory: "Minor / non-violent",
      language: "English",
    },
    detentionDays: 180,
    detentionNote: "Approximately 6 months detained before deportation",
    outcome: "Deported",
    outcomeType: "removed",
    story: [
      "Wade immigrated legally from Jamaica as a teenager in the 1970s, enlisted in the US Army, and served honorably overseas during the Cold War in the 1980s. He lived in metro Atlanta for over 50 years as a lawful permanent resident, fathering six children and becoming a grandfather. An immigration removal order was entered in absentia in 2014, after a hearing he was never properly notified of. He remained unaware the notice to appear existed until 2019, when a green card renewal was denied citing the removal order.",
      "In September 2025, he was pulled over for an alleged failure to use a turn signal. The traffic stop triggered an immigration inquiry. He was taken to Atlanta's ICE field office, transferred to the privately operated Stewart Detention Center in Lumpkin, Georgia, then to a facility in Louisiana. He was deported to Jamaica in February 2026 while his appeal was still pending before the Board of Immigration Appeals. He never had an immigration hearing. A Biden-era policy directing ICE to treat military service as a significant mitigating factor was rescinded in 2025.",
    ],
    sources: [
      { label: "Atlanta News First · February 2026", url: "https://www.atlantanewsfirst.com/2026/02/17/georgia-army-veteran-deported-jamaica-after-ice-detention/" },
    ],
  },
  {
    id: "michel",
    name: "Daphy Michel",
    tag: "Haiti · 31 · Asylum seeker, Pennsylvania",
    image: null,
    demographics: {
      origin: "Caribbean",
      age: "26–35",
      sex: "Female",
      criminalHistory: "None on record",
      language: "Haitian Creole",
    },
    detentionDays: 183,
    detentionNote: "Days detained (county jail + ICE monitoring)",
    outcome: "Died under ICE supervision",
    outcomeType: "death",
    story: [
      "Michel was a Haitian immigrant who entered the US legally through a Texas port of entry in December 2022 and applied for a Temporary Protected Status program due to unrest in Haiti. In September 2025, Michel was detained following a mental health episode on misdemeanor charges and held in Washington, Pennsylvania County Jail for nearly six months on a $10,000 bond, awaiting a mental health evaluation that was repeatedly delayed. On February 26, 2026, a judge dismissed all charges entirely. Her brother Carlo attended the hearing and left the courthouse expecting to pick her up.",
      "Instead, ICE intercepted her release via a detainer, transported her to its Pittsburgh Enforcement and Removal Operations office, enrolled her in an ankle monitoring program, and released her alone, in an unfamiliar city, more than an hour from her home, without notifying her family or her legal representatives. Temperatures dropped to 5°F that week. On the morning of March 2, 2026, maintenance workers found her unresponsive at a Pittsburgh bus shelter. She was transported to UPMC Presbyterian Hospital, where she was pronounced dead. ICE's ankle monitor did not register a tamper alert until March 3 — the day the medical examiner removed it from her leg during intake. By that point, Michel had been dead for approximately 24 hours.",
    ],
    sources: [
      { label: "PayDay Report · March 2026", url: "https://paydayreport.com/haitian-immigrant-dies-in-pittsburgh-raising-questions-about-ice/" },
    ],
  },
  {
    id: "avirmed",
    name: "Avirmed",
    tag: "Mongolia · ~30s · Deaf asylum seeker, California",
    image: null,
    demographics: {
      origin: "Asia",
      age: "26–35",
      sex: "Male",
      criminalHistory: "None on record",
      language: "Other / indigenous",
    },
    detentionDays: 150,
    detentionNote: "Approximately 5 months detained",
    outcome: "Released by court order",
    outcomeType: "released",
    story: [
      "Avirmed — a pseudonym used at his family's request due to fear of harm from the Mongolian government should he be returned — sought asylum at the California-Mexico border in February 2025, citing persecution in Mongolia related to his disability. A 2020 assault there had left him with a traumatic brain injury causing seizures and memory loss; he had been attacked, according to court records, because of his disability. He is deaf and communicates in Mongolian Sign Language.",
      "He was transferred to ICE custody and placed at the for-profit Otay Mesa Detention Center in San Diego. For more than four months, no one at the facility spoke Mongolian Sign Language, and ICE made no arrangement for interpretation. His attorney described his situation as equivalent to solitary confinement: he could not communicate with staff, other detainees, or anyone involved in his case. During an initial interview, agents attempted to use Google Translate as a substitute for an interpreter. The resulting mistranscription was so severe that Avirmed's sister — who lives in Virginia and was listed as his sponsor — was recorded in his file as a daughter named \"Virginia Washington.\"",
      "He underwent a mental health evaluation with no interpretation whatsoever. A federal judge ordered ICE to provide him with a Mongolian Sign Language interpreter and to redo both the mental health evaluation and the credible fear assessment that would determine whether he could pursue asylum. \"He has a right to be involved where he understands and can respond and communicate, and be part of the process, not a bystander,\" the judge said in court. Avirmed was released from detention in late July 2025, approximately two weeks after the court order.",
    ],
    sources: [
      { label: "CalMatters · July 2025", url: "https://calmatters.org/justice/2025/07/deaf-immigrant-released-from-detention/" },
    ],
  },
  {
    id: "ojm",
    name: "O-J-M",
    tag: "Mexico · 24 · Transgender asylum seeker, Oregon",
    image: null,
    demographics: {
      origin: "Mexico",
      age: "18–25",
      sex: "Non-binary / other",
      criminalHistory: "None on record",
      language: "Spanish",
    },
    detentionDays: 40,
    detentionNote: "Days detained, including 40+ days in solitary",
    outcome: "Released by court order",
    outcomeType: "released",
    story: [
      "O-J-M — identified by initials in court documents at her attorney's request — is a 24-year-old transgender woman from Mexico who sought asylum in the United States. On June 2, 2025, she attended a hearing at the Portland Immigration Court at the Edith Green–Wendell Wyatt Federal Building. The government's own attorney had not moved to deport her. As she left the courtroom, ICE agents arrested her in the hallway. Her attorney told the court that the government had given assurances she would not be arrested that day. The government subsequently changed its stated legal basis for the arrest multiple times.",
      "She was transferred to the Northwest ICE Processing Center in Tacoma, Washington — a men's facility — where she requested solitary confinement for her own safety as a transgender woman in a men's detention unit. She remained in isolated detention for over 40 days. US District Court Judge Amy Baggio ordered her immediate release in July 2025, finding the detention unlawful. The judge noted the government had changed its justification for the arrest and detention multiple times without adequate explanation.",
    ],
    sources: [
      { label: "Oregon Capital Chronicle · July 2025", url: "https://oregoncapitalchronicle.com/2025/07/14/asylum-seeker-taken-by-ice-outside-portland-immigration-court-to-be-immediately-released/" },
    ],
  },
  {
    id: "lopez-belloza",
    name: "Any Lucia Lopez Belloza",
    tag: "Honduras · 19 · College student, Massachusetts",
    image: "/any-lucia-lopez-belloza.avif",
    demographics: {
      origin: "Central America",
      age: "18–25",
      sex: "Female",
      criminalHistory: "None on record",
      language: "Spanish",
    },
    detentionDays: 2,
    detentionNote: "Days detained before deportation",
    outcome: "Deported in defiance of court order",
    outcomeType: "removed",
    story: [
      "Lopez Belloza was a 19-year-old freshman at Babson College in Massachusetts. She had arrived in the US from Honduras at age 7, when her parents brought her to seek asylum. That asylum claim was denied in 2015 when she was a child; a removal order was entered, though her father told reporters they had been assured by the judge that the family did not have deportation orders. She had lived in the United States for 12 years.",
      "In November 2025, she was detained at Logan Airport while flying home for Thanksgiving break. Within 48 hours she had been transferred to ICE's regional office in Burlington, flown to Texas, held overnight in a detention facility, and deported to Honduras — in ankle chains and wrist restraints — a country she had not seen since she was 7 years old. A federal judge had issued an order barring her removal from Massachusetts before her deportation flight departed. She was deported in defiance of that order. The judge ordered her return to the US, but she refused to board a flight after ICE stated they would immediately deport her again based on the 11-year-old removal order.",
    ],
    sources: [
      { label: "Reuters · February 2026", url: "https://www.reuters.com/legal/government/deported-student-refuses-flight-back-us-following-threat-second-deportation-2026-02-27/" },
    ],
  },
  {
    id: "hoque",
    name: "Mohammed Hoque",
    tag: "Bangladesh · 20 · International student, Minnesota",
    image: "/mohammed-hoque.png",
    demographics: {
      origin: "Asia",
      age: "18–25",
      sex: "Male",
      criminalHistory: "Minor / non-violent",
      language: "Other",
    },
    detentionDays: 40,
    detentionNote: "Days detained before court-ordered release",
    outcome: "Released by court order; re-arrested",
    outcomeType: "released",
    story: [
      "Hoque was a 20-year-old management information systems student at Minnesota State University Mankato, enrolled on a valid F-1 student visa since 2021. On March 28, 2025, plainclothes ICE agents followed his car home from a coding class and arrested him outside his apartment in front of his parents, who were visiting from Bangladesh. His student visa was revoked the same day. The government cited a 2023 misdemeanor disorderly conduct conviction (stemming from pushing his brother's friend during an argument, which resulted in a year of probation) as justification for the arrest and visa revocation.",
      "Hoque and his attorneys argued the real basis was a series of social media posts in which he had expressed support for Palestinian human rights and used the hashtag #FreePalestine. He is a practicing Muslim. The ACLU of Minnesota, which took his case, noted that DHS had been targeting students from Muslim-majority countries with minor or no criminal records. An immigration judge granted him bond in April, finding he posed no danger or flight risk. DHS immediately appealed that decision, keeping him detained. During his 40 days in the Freeborn County jail, he missed a scheduled surgery to repair hernias; the facility provided only pain medication and declined to reschedule the procedure.",
      "A US District Judge ordered his release in May 2025, finding \"sufficiently clear evidence of viewpoint-based targeting.\" The judge found the disorderly conduct conviction \"does not appear to support removability\" under immigration law. Hoque was arrested a second time in January 2026 at his family home and was held by ICE for more than 6 hours before he was released. ICE subsequently acknowledged Hoque should not have been re-arrested.",
    ],
    sources: [
      { label: "Fox 9 KMSP · March 2026", url: "http://www.fox9.com/news/ice-unlawfully-arrested-mohammed-hoque" },
    ],
  },
];

const OUTCOME_COLORS = {
  removed: "var(--color-outcome-removed, #c0392b)",
  released: "var(--color-outcome-released, #27ae60)",
  death: "var(--color-outcome-death, #2c3e50)",
  error: "var(--color-outcome-error, #e67e22)",
};

export default function Vignettes() {
  const [activeId, setActiveId] = useState(null);
  const active = VIGNETTES.find((v) => v.id === activeId) ?? null;

  function handleSelect(id) {
    setActiveId((prev) => (prev === id ? null : id));
  }

  return (
    <div className="vignettes">
      <div className="vignette-cards">
        {VIGNETTES.map((v) => (
          <button
            key={v.id}
            type="button"
            className={`vignette-card ${activeId === v.id ? "vignette-card--active" : ""}`}
            onClick={() => handleSelect(v.id)}
            aria-pressed={activeId === v.id}
          >
            <span className="vignette-card__name">{v.name}</span>
            <span className="vignette-card__tag">{v.tag}</span>
            <span
              className="vignette-card__outcome"
              style={{ color: OUTCOME_COLORS[v.outcomeType] }}
            >
              {v.outcome}
            </span>
          </button>
        ))}
      </div>

      {active && (
        <div className="vignette-detail">
          <div className="vignette-detail__body">
            {active.image && (
              <div className="vignette-detail__image-col">
                <img
                  src={active.image}
                  alt={`Portrait of ${active.name}`}
                  className="vignette-detail__image"
                />
              </div>
            )}

            <div className={`vignette-detail__text-col ${!active.image ? "vignette-detail__text-col--full" : ""}`}>
              <div className="vignette-detail__header">
                <div>
                  <h3 className="vignette-detail__name">{active.name}</h3>
                  <p className="vignette-detail__tag">{active.tag}</p>
                </div>
                <div className="vignette-detail__meta">
                  <span
                    className="vignette-detail__outcome-badge"
                    style={{ background: OUTCOME_COLORS[active.outcomeType] }}
                  >
                    {active.outcome}
                  </span>
                  <span className="vignette-detail__days">
                    {active.detentionDays} days
                    <span className="vignette-detail__days-note"> · {active.detentionNote}</span>
                  </span>
                </div>
              </div>

              <div className="vignette-detail__demographics">
                {Object.entries(active.demographics).map(([key, val]) => (
                  <span key={key} className="vignette-detail__demo-pill">{val}</span>
                ))}
              </div>

              <div className="vignette-detail__story">
                {active.story.map((para, i) => (
                  <p key={i}>{para}</p>
                ))}
              </div>

              <div className="vignette-detail__sources">
                {active.sources.map((s) => (
                  <a
                    key={s.url}
                    className="vignette-detail__source"
                    href={s.url}
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    {s.label} ↗
                  </a>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
