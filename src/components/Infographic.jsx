import React, { useState, useEffect, useRef } from 'react';
import * as d3 from 'd3';

const PERSON_ICON_PATH = 'M291.299,116.517h-3.501c10.635-12.36,17.102-28.378,17.102-45.915C304.899,31.666,273.219,0,234.305,0c-38.93,0-70.584,31.666-70.584,70.602c0,17.537,6.477,33.555,17.093,45.915h-3.51c-19.645,0-35.626,15.997-35.626,35.645v117.105c0,19.648,15.982,35.633,35.626,35.633h1.372v128.07c0,20.332,10.697,35.645,24.884,35.645h61.468c14.208,0,24.908-15.312,24.908-35.645v-128.07h1.363c19.642,0,35.639-15.984,35.639-35.633V152.161C326.932,132.514,310.94,116.517,291.299,116.517z';
const PERSON_ICON_VIEWBOX = 468.614;

// Infographic-specific styles
const infographicStyles = {
  wrapper: {
    width: '100%',
    margin: '0 auto',
    padding: '2rem 0 4rem',
    backgroundColor: '#f5f3ee',
  },
  filterSection: {
    backgroundColor: '#fbfaf7',
    border: '1px solid #d6d2c5',
    borderRadius: '12px',
    padding: '1.2rem',
    marginBottom: '1.5rem',
    boxShadow: '0 2px 8px rgba(10, 17, 26, 0.04)',
  },
  filterGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))',
    gap: '1rem',
  },
  heading: {
    fontSize: '1.3rem',
    marginBottom: '0.8rem',
    color: '#182028',
    fontFamily: '"Libre Baskerville", serif',
    fontWeight: '500',
  },
  heading2: {
    fontSize: '0.95rem',
    marginBottom: '1.2rem',
    color: '#182028',
    fontFamily: '"Libre Baskerville", serif',
  },
  contentColumn: {
    display: 'flex',
    flexDirection: 'column',
    gap: '1.2rem',
  },
  statsContainer: {
    display: 'grid',
    gridTemplateColumns: '22% 39% 39%',
    gap: '0.75rem',
    marginBottom: '1.2rem',
  },
  statsBox: {
    backgroundColor: '#fbfaf7',
    border: '1px solid #d6d2c5',
    borderRadius: '10px',
    padding: '0.9rem',
    minHeight: '220px',
    display: 'flex',
    flexDirection: 'column',
    color: '#182028',
    boxShadow: '0 2px 4px rgba(10, 17, 26, 0.02)',
  },
  outcomeSection: {
    backgroundColor: '#fbfaf7',
    border: '1px solid #d6d2c5',
    borderRadius: '12px',
    padding: '1.2rem',
    marginBottom: '1.2rem',
    boxShadow: '0 2px 4px rgba(10, 17, 26, 0.02)',
  },
  bondDetentionGrid: {
    display: 'grid',
    gridTemplateColumns: '45% 55%',
    gap: '1rem',
    marginTop: '0',
  },
  cardBox: {
    backgroundColor: '#fbfaf7',
    border: '1px solid #d6d2c5',
    borderRadius: '10px',
    padding: '1rem',
    minHeight: '280px',
    display: 'flex',
    flexDirection: 'column',
    color: '#182028',
    boxShadow: '0 2px 4px rgba(10, 17, 26, 0.02)',
  },
  smallText: {
    fontSize: '0.8rem',
    color: '#5d6773',
    marginTop: '0.3rem',
    lineHeight: '1.4',
  },
  statTitle: {
    fontSize: '0.95rem',
    fontWeight: '600',
    fontFamily: '"Libre Baskerville", serif',
    color: '#182028',
    marginBottom: '0.4rem',
    marginTop: '0.4rem',
  },
};

// Sub-components
const FilterControls = ({ rows, filters, onFilterChange }) => {
  const dims = {
    age_group: 'Age group',
    gender: 'Gender',
    citizenship_country_sub_region: 'Sub-region',
    conviction_charge_badness: 'Criminal status'
  };

  const getUniqueOptions = (column) => {
    const values = [...new Set(rows.map((r) => r[column]).filter(Boolean))];
    const withoutAll = values.filter((value) => value !== 'All').sort((a, b) => a.localeCompare(b));
    return values.includes('All') ? ['All', ...withoutAll] : withoutAll;
  };

  return (
    <div style={infographicStyles.filterSection}>
      <h3 style={{ ...infographicStyles.heading, marginBottom: '1rem' }}>Filters</h3>
      <div style={infographicStyles.filterGrid}>
        {Object.entries(dims).map(([key, label]) => (
          <div key={key}>
            <label htmlFor={key} style={{ fontSize: '0.7rem', fontWeight: '700', textTransform: 'uppercase', color: '#5d6773', display: 'block', marginBottom: '0.4rem' }}>{label}</label>
            <select
              id={key}
              value={filters[key] || 'All'}
              onChange={(e) => onFilterChange(key, e.target.value)}
              aria-label={`Select ${label.toLowerCase()}`}
              style={{ width: '100%', padding: '0.35rem 0.5rem', fontSize: '0.85rem', border: '1px solid #d6d2c5', borderRadius: '6px', backgroundColor: '#fff', fontFamily: 'inherit' }}
            >
              {getUniqueOptions(key).map((option) => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </select>
          </div>
        ))}
      </div>
    </div>
  );
};

const GenderBox = ({ row }) => {
  const containerRef = useRef(null);

  useEffect(() => {
    if (!containerRef.current || !row) return;

    const malePercent = row.male_percent ?? 0;
    const femalePercent = row.female_percent ?? Math.max(0, 100 - malePercent);
    const prominentGender = malePercent >= femalePercent
      ? { label: 'male', percent: malePercent }
      : { label: 'female', percent: femalePercent };

    d3.select(containerRef.current).selectAll('*').remove();

    d3.select(containerRef.current)
      .append('div')
      .style('font-size', '17px')
      .style('font-weight', '600')
      .style('font-family', '"Libre Baskerville", serif')
      .style('color', '#182028')
      .style('margin-bottom', '0.5rem')
      .text(`${Math.round(prominentGender.percent)}% are ${prominentGender.label}`);

    const svg = d3.select(containerRef.current)
      .append('svg')
      .attr('viewBox', '0 0 180 150')
      .attr('aria-label', 'Gender pie chart')
      .style('margin-top', 'auto')
      .style('width', '100%');

    const pieData = [
      { label: 'Male', value: malePercent, color: '#0f5a6b' },
      { label: 'Female', value: femalePercent, color: '#83b8c2' }
    ];

    const pieGenerator = d3.pie().value((d) => d.value).sort(null);
    const arcGenerator = d3.arc().innerRadius(0).outerRadius(55);

    svg
      .append('g')
      .attr('transform', 'translate(90,75)')
      .selectAll('path')
      .data(pieGenerator(pieData))
      .join('path')
      .attr('d', arcGenerator)
      .attr('fill', (d) => d.data.color)
      .attr('stroke', 'transparent')
      .attr('stroke-width', 4);
  }, [row]);

  return <div style={infographicStyles.statsBox} ref={containerRef}></div>;
};

const AgeDistributionChart = ({ row }) => {
  const containerRef = useRef(null);

  useEffect(() => {
    if (!containerRef.current || !row) return;

    d3.select(containerRef.current).selectAll('*').remove();

    d3.select(containerRef.current)
      .append('div')
      .style('font-size', '17px')
      .style('font-weight', '600')
      .style('font-family', '"Libre Baskerville", serif')
      .style('color', '#182028')
      .style('margin-bottom', '0.5rem')
      .text('Age Distribution');

    const distribution = row.age_distribution || {};
    const ageDistribution = Object.entries(distribution)
      .map(([age, pct]) => ({ age: Number(age), value: Number(pct) / 100 }))
      .filter((d) => !Number.isNaN(d.age) && !Number.isNaN(d.value))
      .sort((a, b) => a.age - b.age);

    const ageSvg = d3.select(containerRef.current)
      .append('svg')
      .attr('viewBox', '0 0 420 160')
      .attr('aria-label', 'Age distribution histogram')
      .style('flex', '1');

    if (ageDistribution.length === 0) {
      ageSvg.append('text')
        .attr('x', 210)
        .attr('y', 80)
        .attr('text-anchor', 'middle')
        .style('font-size', '12px')
        .text('No age distribution data available');
      return;
    }

    const ageMargin = { top: 4, right: 8, bottom: 40, left: 32 };
    const ageWidth = 420 - ageMargin.left - ageMargin.right;
    const ageHeight = 160 - ageMargin.top - ageMargin.bottom;
    const agePlot = ageSvg.append('g').attr('transform', `translate(${ageMargin.left},${ageMargin.top})`);

    const uniqueAges = [...new Set(ageDistribution.map((d) => d.age))].sort((a, b) => a - b);
    const xAge = d3.scaleBand()
      .domain(uniqueAges)
      .range([0, ageWidth])
      .paddingInner(0.1)
      .paddingOuter(0.02);

    const maxY = Math.max(0.05, d3.max(ageDistribution, (d) => d.value));
    const yAge = d3.scaleLinear()
      .domain([0, maxY])
      .range([ageHeight, 0]);

    agePlot
      .selectAll('rect')
      .data(ageDistribution)
      .join('rect')
      .attr('x', (d) => xAge(d.age))
      .attr('y', (d) => yAge(d.value))
      .attr('width', xAge.bandwidth())
      .attr('height', (d) => ageHeight - yAge(d.value))
      .attr('fill', '#0f5a6b');

    const ageTickStep = uniqueAges.length <= 8 ? 1 : (uniqueAges.length <= 16 ? 2 : 5);
    const ageTickValues = uniqueAges.filter((_, idx) => idx % ageTickStep === 0);

    agePlot
      .append('g')
      .attr('transform', `translate(0,${ageHeight})`)
      .call(d3.axisBottom(xAge).tickValues(ageTickValues))
      .call((g) => g.selectAll('text').style('font-size', '9px'));

    agePlot
      .append('g')
      .call(d3.axisLeft(yAge).ticks(4).tickFormat(d3.format('.0%')))
      .call((g) => g.selectAll('text').style('font-size', '9px'));
  }, [row]);

  return <div style={infographicStyles.statsBox} ref={containerRef}></div>;
};

const CriminalStatusChart = ({ row }) => {
  const containerRef = useRef(null);

  useEffect(() => {
    if (!containerRef.current || !row) return;

    d3.select(containerRef.current).selectAll('*').remove();

    d3.select(containerRef.current)
      .append('div')
      .style('font-size', '17px')
      .style('font-weight', '600')
      .style('font-family', '"Libre Baskerville", serif')
      .style('color', '#182028')
      .style('margin-bottom', '0.5rem')
      .text('Criminal Status');

    const crimeColorForCategory = (crimeCategory) => {
      if (crimeCategory.includes('None')) return '#e5e7eb';
      if (crimeCategory.includes('Minimal')) return '#fee2e2';
      if (crimeCategory.includes('Low')) return '#fca5a5';
      if (crimeCategory.includes('Moderate')) return '#f87171';
      if (crimeCategory.includes('High')) return '#dc2626';
      if (crimeCategory.includes('Extreme')) return '#7f1d1d';
      return '#6b1f2b';
    };

    const crimeDistribution = Object.entries(row.crime_distribution || {})
      .map(([crimeCategory, pct]) => ({ crimeCategory, value: Number(pct) / 100 }))
      .filter((d) => !Number.isNaN(d.value))
      .sort((a, b) => a.crimeCategory.localeCompare(b.crimeCategory));

    const crimeSvg = d3.select(containerRef.current)
      .append('svg')
      .attr('viewBox', '0 0 420 160')
      .attr('aria-label', 'Criminal status distribution')
      .style('flex', '1');

    if (crimeDistribution.length === 0) {
      crimeSvg.append('text')
        .attr('x', 210)
        .attr('y', 80)
        .attr('text-anchor', 'middle')
        .style('font-size', '12px')
        .text('No criminal status data available');
      return;
    }

    const crimeMargin = { top: 4, right: 8, bottom: 50, left: 32 };
    const crimeWidth = 420 - crimeMargin.left - crimeMargin.right;
    const crimeHeight = 160 - crimeMargin.top - crimeMargin.bottom;
    const crimePlot = crimeSvg.append('g').attr('transform', `translate(${crimeMargin.left},${crimeMargin.top})`);

    const xCrime = d3.scaleBand()
      .domain(crimeDistribution.map((d) => d.crimeCategory))
      .range([0, crimeWidth])
      .paddingInner(0.1);

    const yCrime = d3.scaleLinear()
      .domain([0, Math.max(0.05, d3.max(crimeDistribution, (d) => d.value))])
      .range([crimeHeight, 0]);

    const tooltip = d3.select('body').selectAll('#crimeStatusTooltip').data([null])
      .join('div')
      .attr('id', 'crimeStatusTooltip')
      .attr('class', 'tooltip');

    const crimeBars = crimePlot
      .selectAll('rect')
      .data(crimeDistribution)
      .join('rect')
      .attr('x', (d) => xCrime(d.crimeCategory))
      .attr('y', (d) => yCrime(d.value))
      .attr('width', xCrime.bandwidth())
      .attr('height', (d) => crimeHeight - yCrime(d.value))
      .attr('fill', (d) => crimeColorForCategory(d.crimeCategory));

    crimeBars
      .on('mouseenter', (event, d) => {
        tooltip.style('opacity', 1);
      })
      .on('mouseleave', () => {
        tooltip.style('opacity', 0);
      });

    crimePlot
      .append('g')
      .attr('transform', `translate(0,${crimeHeight})`)
      .call(d3.axisBottom(xCrime))
      .call((g) => g.selectAll('text').style('font-size', '8px').attr('transform', 'rotate(-15)').style('text-anchor', 'end'));

    crimePlot
      .append('g')
      .call(d3.axisLeft(yCrime).ticks(4).tickFormat(d3.format('.0%')))
      .call((g) => g.selectAll('text').style('font-size', '9px'));
  }, [row]);

  return <div style={infographicStyles.statsBox} ref={containerRef}></div>;
};

const OutcomePanel = ({ row }) => {
  const svgRef = useRef(null);
  const legendRef = useRef(null);
  const titleRef = useRef(null);

  const outcomeColors = {
    'Released to USA - long term residence likely': '#0f5a6b',
    'Released to USA - long term residence possible': '#83b8c2',
    'Released to USA - will be detained again': '#c7802e',
    'Awaiting Deportation': '#ad3f2f',
    'Deported': '#182028'
  };

  const outcomeLabels = {
    'Released to USA - long term residence likely': 'Stay in USA likely',
    'Released to USA - long term residence possible': 'Stay in USA possible',
    'Released to USA - will be detained again': 'Will be detained again',
    'Awaiting Deportation': 'Awaiting Deportation',
    'Deported': 'Deported'
  };

  const outcomeOrder = [
    'Released to USA - long term residence likely',
    'Released to USA - long term residence possible',
    'Released to USA - will be detained again',
    'Awaiting Deportation',
    'Deported'
  ];

  const outcomeKeyAliases = {
    'Released to USA - long term residence likely': ['Released to USA - long term residence likely'],
    'Released to USA - long term residence possible': ['Released to USA - long term residence possible'],
    'Released to USA - will be detained again': [
      'Released to USA - will be detained again',
      'Released to USA - will be detained at a later date'
    ],
    'Awaiting Deportation': ['Awaiting Deportation'],
    'Deported': ['Deported']
  };

  const toNum = (value) => {
    if (value === null || value === undefined || value === '' || value === '<NA>') return null;
    const parsed = Number(value);
    return Number.isNaN(parsed) ? null : parsed;
  };

  useEffect(() => {
    if (!svgRef.current || !row) return;

    d3.select(svgRef.current).selectAll('*').remove();
    d3.select(legendRef.current).selectAll('*').remove();

    const getOutcomeValue = (key) => {
      const aliases = outcomeKeyAliases[key] || [key];
      for (const alias of aliases) {
        const value = toNum(row[alias]);
        if (value !== null) return value;
      }
      return 0;
    };

    const outcomes = outcomeOrder.map((key) => ({ key, value: getOutcomeValue(key) }));
    const floorCounts = outcomes.map((d) => ({ ...d, count: Math.floor(d.value), remainder: d.value - Math.floor(d.value) }));
    const floorTotal = d3.sum(floorCounts, (d) => d.count);
    const slotsRemaining = Math.max(0, 100 - floorTotal);

    floorCounts
      .sort((a, b) => b.remainder - a.remainder)
      .slice(0, slotsRemaining)
      .forEach((d) => { d.count += 1; });

    const countsByKey = {};
    floorCounts.forEach((d) => { countsByKey[d.key] = d.count; });
    const longTermStayCount = (countsByKey['Released to USA - long term residence likely'] || 0)
      + (countsByKey['Released to USA - long term residence possible'] || 0);
    const deportedCount = (countsByKey['Awaiting Deportation'] || 0) + (countsByKey.Deported || 0);

    if (titleRef.current) {
      titleRef.current.textContent =
        `For every 100 detainees, ${longTermStayCount} will get to stay long-term, and ${deportedCount} will be deported.`;
    }

    const leftKeys = [
      'Released to USA - long term residence likely',
      'Released to USA - long term residence possible',
      'Released to USA - will be detained again'
    ];
    const rightKeys = ['Awaiting Deportation', 'Deported'];

    const makeIcons = (keys) => {
      const iconList = [];
      keys.forEach((key) => {
        for (let i = 0; i < (countsByKey[key] || 0); i += 1) {
          iconList.push({ category: key, color: outcomeColors[key] });
        }
      });
      return iconList;
    };

    const leftIcons = makeIcons(leftKeys);
    const rightIcons = makeIcons(rightKeys);
    const midSvg = d3.select(svgRef.current);

    const buildIconGroup = (icons, centerX, centerY, gapX, gapY) => {
      const iconSize = 28;
      const columns = Math.max(1, Math.min(10, icons.length));
      const rows = Math.ceil(icons.length / columns);
      const width = columns * iconSize + (columns - 1) * gapX;
      const height = rows * iconSize + (rows - 1) * gapY;

      return {
        group: midSvg.append('g').attr('transform', `translate(${centerX - width / 2},${centerY - height / 2})`),
        columns,
        rows,
        iconSize,
        gapX,
        gapY
      };
    };

    const drawPeople = (group, icons, columns, iconSize, gapX, gapY) => {
      const scale = iconSize / PERSON_ICON_VIEWBOX;

      const people = group.selectAll('g.person').data(icons).join('g')
        .attr('class', 'person')
        .attr('transform', (_, i) => {
          const x = (i % columns) * (iconSize + gapX);
          const y = Math.floor(i / columns) * (iconSize + gapY);
          return `translate(${x},${y})`;
        });

      people.selectAll('*').remove();

      people.append('path')
        .attr('d', PERSON_ICON_PATH)
        .attr('transform', `scale(${scale})`)
        .attr('fill', (d) => d.color)
        .attr('stroke', 'none');
    };

    const left = buildIconGroup(leftIcons, 222, 206, 7, 8);
    const right = buildIconGroup(rightIcons, 596, 206, 6, 8);

    drawPeople(left.group, leftIcons, left.columns, left.iconSize, left.gapX, left.gapY);
    drawPeople(right.group, rightIcons, right.columns, right.iconSize, right.gapX, right.gapY);

    d3.select(legendRef.current)
      .selectAll('div.legend-item')
      .data(outcomeOrder)
      .join('div')
      .attr('class', 'legend-item')
      .style('display', 'inline-flex')
      .style('align-items', 'center')
      .style('gap', '0.4rem')
      .style('margin-right', '1rem')
      .style('margin-bottom', '0.4rem')
      .html((key) => `<span style='width: 10px; height: 10px; background: ${outcomeColors[key]}; border-radius: 2px;'></span><span style='font-size: 0.75rem;'>${outcomeLabels[key]}</span>`);
  }, [row]);

  return (
    <div style={infographicStyles.outcomeSection}>
      <h3 style={{ ...infographicStyles.heading, marginBottom: '0.8rem', fontSize: '1rem' }} ref={titleRef}>For every 100 people detained in this group...</h3>
      <svg ref={svgRef} viewBox="0 0 800 430" aria-label="Population outcomes pictograph" style={{ width: '100%', height: 'auto', minHeight: '340px' }}></svg>
      <div style={{ marginTop: '0.8rem', fontSize: '0.08rem' }} ref={legendRef}></div>
    </div>
  );
};

const BondAndDetentionCard = ({ row }) => {
  const bondTextRef = useRef(null);
  const bondValueRef = useRef(null);
  const bondSvgRef = useRef(null);
  const bondStackAreaRef = useRef(null);
  const transferTextRef = useRef(null);
  const milesTextRef = useRef(null);
  const detentionDaysDeportRef = useRef(null);
  const detentionDaysReleaseRef = useRef(null);
  const deportMonthGlyphRef = useRef(null);
  const releaseMonthGlyphRef = useRef(null);

  const DAYS_PER_MONTH = 30;
  const CALENDAR_GLYPH_PATH = '/data/calendar_glyph.png';
  const CASH_STACK_PATH = '/data/cash_stack.png';
  const ZERO_BOND_PATH = '/data/zero_bond.png';
  const cash_offset = 5;
  const max_cash_stacks = 10;

  const money = d3.format('$,d');

  const toNum = (value) => {
    if (value === null || value === undefined || value === '' || value === '<NA>') return null;
    const parsed = Number(value);
    return Number.isNaN(parsed) ? null : parsed;
  };

  useEffect(() => {
    if (!row) return;

    const bondPct = row['Bond Percentage'] ?? 0;
    const bondShare = Math.max(0, Math.min(1, bondPct / 100));

    if (bondTextRef.current) {
      bondTextRef.current.textContent = `${Math.round(bondPct)}% of those released within the USA pay a bond.`;
    }

    const overallAvg = 6969.51;
    const avgBond = row['Average Bond Paid'];

    if (bondValueRef.current) {
      if (bondPct < 0.5) {
        bondValueRef.current.textContent = '';
      } else {
        let text;
        if (!avgBond) {
          text = 'The average bond paid is N/A';
        } else {
          const pctDiff = ((avgBond - overallAvg) / overallAvg) * 100;
          const pctFormatted = Math.abs(pctDiff).toFixed(0);
          let comparisonText = '';
          if (pctDiff > 0) {
            comparisonText = `, ${pctFormatted}% higher than the overall average.`;
          } else if (pctDiff < 0) {
            comparisonText = `, ${pctFormatted}% lower than the overall average.`;
          } else {
            comparisonText = `, equal to the overall average.`;
          }
          text = `The average bond paid is ${money(avgBond)}${comparisonText}`;
        }
        bondValueRef.current.textContent = text;
      }
    }

    if (transferTextRef.current) {
      transferTextRef.current.innerHTML = `<strong>${row['Number Transfers'] ?? 'N/A'} transfers</strong>`;
    }

    if (milesTextRef.current) {
      milesTextRef.current.innerHTML = `<strong>${row['Miles Traveled'] ?? 'N/A'} miles</strong> traveled`;
    }

    if (detentionDaysDeportRef.current) {
      detentionDaysDeportRef.current.innerHTML = `<strong>${row['Days spent prior to deportation'] ?? 'N/A'} days</strong> in detention prior to deportation`;
    }

    if (detentionDaysReleaseRef.current) {
      detentionDaysReleaseRef.current.innerHTML = `<strong>${row['Days spent prior to release'] ?? 'N/A'} days</strong> in detention prior to release`;
    }

    const renderMonthGlyphs = (ref, daysValue) => {
      const days = toNum(daysValue);
      if (ref.current) {
        ref.current.innerHTML = '';
        if (days === null || days <= 0) return;

        const uncappedGlyphs = Math.ceil(days / DAYS_PER_MONTH);
        const totalGlyphs = Math.min(8, uncappedGlyphs);
        const finalGlyphFraction = (days % DAYS_PER_MONTH) / DAYS_PER_MONTH || 1;
        const wasCapped = uncappedGlyphs > 8;

        const glyphData = Array.from({ length: totalGlyphs }, (_, i) =>
          i === totalGlyphs - 1 && !wasCapped ? finalGlyphFraction : 1
        );

        d3.select(ref.current)
          .selectAll('img.month-glyph')
          .data(glyphData)
          .join('img')
          .attr('class', 'month-glyph')
          .attr('src', CALENDAR_GLYPH_PATH)
          .attr('alt', '')
          .style('width', (fraction) => `${40 * fraction}px`)
          .style('height', '40px')
          .style('object-fit', 'cover')
          .style('border-radius', '3px');
      }
    };

    renderMonthGlyphs(deportMonthGlyphRef, row['Days spent prior to deportation']);
    renderMonthGlyphs(releaseMonthGlyphRef, row['Days spent prior to release']);

    if (bondSvgRef.current) {
      d3.select(bondSvgRef.current).selectAll('*').remove();

      const bondSvg = d3.select(bondSvgRef.current);
      const bondPie = d3.pie().value((d) => d.value).sort(null)([
        { label: 'Paid bond', value: bondShare, color: '#7f1d1d' },
        { label: 'No bond', value: 1 - bondShare, color: '#cad5eb' }
      ]);

      const pieCenterX = 100;
      const pieCenterY = 75;
      const pieRadius = 65;

      bondSvg
        .append('g')
        .attr('transform', `translate(${pieCenterX},${pieCenterY})`)
        .selectAll('path')
        .data(bondPie)
        .join('path')
        .attr('d', d3.arc().innerRadius(0).outerRadius(pieRadius))
        .attr('fill', (d) => d.data.color)
        .attr('stroke', '#ffffff')
        .attr('stroke-width', 1);

      const bondLegend = bondSvg.append('g')
        .attr('transform', 'translate(100,160)');

      const legendItems = [
        { label: 'No bond', color: '#cad5eb', x: -50 },
        { label: 'Paid bond', color: '#7f1d1d', x: 15 }
      ];

      const legendGroup = bondLegend.selectAll('g')
        .data(legendItems)
        .join('g')
        .attr('transform', (d) => `translate(${d.x},0)`);

      legendGroup.append('circle')
        .attr('r', 4)
        .attr('cx', 0)
        .attr('cy', -3)
        .attr('fill', (d) => d.color);

      legendGroup.append('text')
        .attr('x', 10)
        .attr('y', 0)
        .attr('dominant-baseline', 'middle')
        .style('font-size', '11px')
        .style('fill', '#182028')
        .text((d) => d.label);
    }

    if (bondStackAreaRef.current) {
      bondStackAreaRef.current.innerHTML = '';
      const showZeroBondImage = bondPct < 0.5 || !avgBond || avgBond < 10;
      const rawStackCount = showZeroBondImage ? 0 : Math.max(1, Math.floor(avgBond / 1000));
      const stackCount = Math.min(max_cash_stacks, rawStackCount);

      if (showZeroBondImage && avgBond) {
        const img = document.createElement('img');
        img.className = 'bond-stack-image';
        img.src = ZERO_BOND_PATH;
        img.style.position = 'absolute';
        img.style.left = '30px';
        img.style.bottom = '20px';
        img.style.width = '120px';
        img.style.height = '120px';
        img.style.objectFit = 'contain';
        bondStackAreaRef.current.appendChild(img);
      } else {
        const yOffset = Math.max(0, cash_offset);
        for (let i = 0; i < stackCount; i += 1) {
          const img = document.createElement('img');
          img.className = 'bond-stack-image';
          img.src = CASH_STACK_PATH;
          img.style.position = 'absolute';
          img.style.left = '30px';
          img.style.bottom = `${20 + (i * yOffset)}px`;
          img.style.width = '120px';
          img.style.height = 'auto';
          img.style.objectFit = 'contain';
          bondStackAreaRef.current.appendChild(img);
        }
      }
    }
  }, [row]);

  return (
    <div style={infographicStyles.bondDetentionGrid}>
      <div style={infographicStyles.cardBox}>
        <h4 style={infographicStyles.statTitle} ref={bondTextRef}></h4>
        <p style={infographicStyles.smallText} ref={bondValueRef}></p>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem', marginTop: '0.8rem', flex: 1 }}>
          <div style={{ position: 'relative', height: '140px' }} ref={bondStackAreaRef} aria-hidden="true"></div>
          <svg ref={bondSvgRef} viewBox="0 0 200 180" aria-label="Bond share chart" style={{ width: '100%' }}></svg>
        </div>
      </div>

      <div style={infographicStyles.cardBox}>
        <h4 style={infographicStyles.statTitle}>During the average detention:</h4>
        <p style={{ ...infographicStyles.smallText, marginTop: '0.6rem' }} ref={transferTextRef}></p>
        <p style={{ ...infographicStyles.smallText, marginTop: '0.4rem' }} ref={milesTextRef}></p>
        <p style={{ ...infographicStyles.smallText, marginTop: '0.8rem' }} ref={detentionDaysDeportRef}></p>
        <div style={{ display: 'flex', gap: '0.3rem', marginTop: '0.3rem', flexWrap: 'wrap' }} ref={deportMonthGlyphRef} aria-hidden="true"></div>
        <p style={{ ...infographicStyles.smallText, marginTop: '0.6rem' }} ref={detentionDaysReleaseRef}></p>
        <div style={{ display: 'flex', gap: '0.3rem', marginTop: '0.3rem', flexWrap: 'wrap' }} ref={releaseMonthGlyphRef} aria-hidden="true"></div>
      </div>
    </div>
  );
};

// Main Infographic Component
const Infographic = () => {
  const [rows, setRows] = useState([]);
  const [filters, setFilters] = useState({
    age_group: 'All',
    gender: 'All',
    citizenship_country_sub_region: 'All',
    conviction_charge_badness: 'All'
  });
  const [selectedRow, setSelectedRow] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const toNum = (value) => {
    if (value === null || value === undefined || value === '' || value === '<NA>') return null;
    const parsed = Number(value);
    return Number.isNaN(parsed) ? null : parsed;
  };

  const parseDistribution = (value) => {
    if (!value) return {};
    if (typeof value === 'object') return value;
    try {
      return JSON.parse(value);
    } catch {
      return {};
    }
  };

  const normalizeRow = (row) => ({
    ...row,
    n_records: toNum(row.n_records),
    male_percent: toNum(row.male_percent),
    female_percent: toNum(row.female_percent),
    age_distribution: parseDistribution(row.age_distribution),
    crime_distribution: parseDistribution(row.crime_distribution),
    'Released to USA - long term residence likely': toNum(row['Released to USA - long term residence likely']),
    'Released to USA - long term residence possible': toNum(row['Released to USA - long term residence possible']),
    'Released to USA - will be detained at a later date': toNum(row['Released to USA - will be detained at a later date']),
    'Released to USA - will likely be detained again': toNum(row['Released to USA - will likely be detained again']),
    'Awaiting Deportation': toNum(row['Awaiting Deportation']),
    'Deported': toNum(row['Deported']),
    'Bond Percentage': toNum(row['Bond Percentage']),
    'Average Bond Paid': toNum(row['Average Bond Paid']),
    'Number Transfers': toNum(row['Number Transfers']),
    'Miles Traveled': toNum(row['Miles Traveled']),
    'Days spent prior to deportation': toNum(row['Days spent prior to deportation']),
    'Days spent prior to release': toNum(row['Days spent prior to release'])
  });

  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        const response = await fetch('/data/stats_df.json');
        if (!response.ok) throw new Error('Failed to load data');
        const data = await response.json();
        const normalizedRows = data.map(normalizeRow);
        setRows(normalizedRows);
        setSelectedRow(normalizedRows[0] || null);
      } catch (err) {
        console.error('Error loading data:', err);
        setError('Failed to load infographic data');
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, []);

  const getMatchingRow = (filters) => {
    if (!rows.length) return null;

    const exact = rows.find(
      (row) => row.age_group === filters.age_group
        && row.gender === filters.gender
        && row.citizenship_country_sub_region === filters.citizenship_country_sub_region
        && row.conviction_charge_badness === filters.conviction_charge_badness
    );

    if (exact) return exact;

    const filterKeys = Object.keys(filters);
    const permissiveRows = rows.filter((row) =>
      filterKeys.every((key) => row[key] === filters[key] || row[key] === 'All')
    );
    const scored = permissiveRows
      .map((row) => ({
        row,
        specificity: filterKeys.reduce((acc, key) => acc + (row[key] === 'All' ? 0 : 1), 0)
      }))
      .sort((a, b) => b.specificity - a.specificity);

    return scored[0]?.row || null;
  };

  useEffect(() => {
    const newRow = getMatchingRow(filters);
    setSelectedRow(newRow);
  }, [filters, rows]);

  const handleFilterChange = (key, value) => {
    setFilters((prev) => ({ ...prev, [key]: value }));
  };

  if (loading) {
    return (
      <div style={infographicStyles.wrapper}>
        <p style={{ color: '#5d6773' }}>Loading infographic...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div style={infographicStyles.wrapper}>
        <p style={{ color: '#ad3f2f' }}>{error}</p>
      </div>
    );
  }

  const fullDatasetRow = getMatchingRow({
    age_group: 'All',
    gender: 'All',
    citizenship_country_sub_region: 'All',
    conviction_charge_badness: 'All'
  });

  const selectedCount = selectedRow?.n_records ?? 0;
  const totalCount = fullDatasetRow?.n_records ?? 0;
  const selectedShare = totalCount > 0 ? (selectedCount / totalCount) * 100 : 0;
  const selectedShareText = selectedShare.toFixed(1);
  const numberWithCommas = d3.format(',d');

  return (
    <div style={infographicStyles.wrapper}>
      <div className="app-shell infographic-shell">
        <div className="story-layout infographic-layout">
          <aside className="sidebar infographic-sidebar">
            <FilterControls rows={rows} filters={filters} onFilterChange={handleFilterChange} />
          </aside>

          <main style={infographicStyles.contentColumn}>
            <h2 style={{ ...infographicStyles.heading2, marginBottom: '0' }}>
              For these {numberWithCommas(selectedCount)} detainees ({selectedShareText}% of dataset):
            </h2>

            <div style={infographicStyles.statsContainer} className="infographic-stats-grid">
              {selectedRow && (
                <>
                  <GenderBox row={selectedRow} />
                  <AgeDistributionChart row={selectedRow} />
                  <CriminalStatusChart row={selectedRow} />
                </>
              )}
            </div>

            {selectedRow && <OutcomePanel row={selectedRow} />}
            {selectedRow && <BondAndDetentionCard row={selectedRow} allRows={rows} />}
          </main>
        </div>
      </div>
    </div>
  );
};

export default Infographic;
