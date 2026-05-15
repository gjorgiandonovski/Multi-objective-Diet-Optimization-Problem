# CANVA PRESENTATION PROMPT: Multi-Objective Diet Optimization

**Project:** Multi-Objective Diet Optimization (BAO 2026)  
**Duration:** 10-minute academic presentation  
**Total Slides:** 10  
**Target Audience:** Academic (Bioinspired Algorithms course)

---

## 🎨 OVERALL DESIGN BRIEF

### Color Palette:
- **Primary:** Deep blue (#1F4788) and emerald green (#2D8659)
- **Accent:** Gold/amber (#D4A574) for highlights and key data
- **Neutral:** Light gray (#F5F5F5) and white (#FFFFFF) for backgrounds
- **Text:** Dark charcoal (#2C2C2C) for readability

### Typography:
- **Headings:** Modern sans-serif (Montserrat or Inter Bold, 48-56pt)
- **Body text:** Clean sans-serif (Open Sans or Lato, 18-24pt)
- **Data/Numbers:** Monospace for metrics (16-20pt)
- **Spacing:** Generous margins (minimum 40px), breathing room

### Visual Style:
- Minimalist + Modern Data-Driven
- Clean geometric shapes and dividers
- Subtle gradients (not overwhelming)
- Icons: Flaticons, Heroicons (modern thin-line style)
- Data visualizations: Professional charts with rounded corners

---

## 📊 SLIDE-BY-SLIDE BREAKDOWN

---

## **SLIDE 1: TITLE SLIDE**

### Design Style:
**Hero layout with strong visual hierarchy**
- Full-width background: Gradient from deep blue (top-left) to emerald green (bottom-right)
- Centered white text with gold accent underline
- Modern, clean, immediately establishes tone

### Content:
```
┌─────────────────────────────────────────┐
│                                         │
│   Multi-Objective Diet Optimization    │
│   ████████████ (Gold underline)        │
│                                         │
│   Balancing Nutrition Through          │
│   Bioinspired Algorithms              │
│                                         │
│   Group 11                             │
│   Ismael De Los Santos & Gjorgi Andonovski │
│   BAO 2026                             │
│                                         │
└─────────────────────────────────────────┘
```

### Visual Elements:
- **Left side:** Abstract illustration of a plate with different food groups (colorful, geometric style)
- **Right side:** Small icons of algorithms (DNA helix for GA, ant for ACO, swarm particles for swarm)
- **Background elements:** Subtle food-related icons (fork, spoon, scales) very faded in corners

### Design Notes:
- No clutter; let the gradient do the work
- Icons should be 20-30% opacity, subtle background layer
- Use white text with thin shadow for depth
- Gold underline should be 4-6px thick

---

## **SLIDE 2: PROBLEM DEFINITION**

### Design Style:
**Split-screen with problem breakdown**
- Left 60%: Text content with icons
- Right 40%: Visual representation of the problem space

### Content Layout:
```
┌─────────────────────────────┬──────────────────┐
│  PROBLEM DEFINITION         │                  │
│                             │  [VISUAL SIDE]   │
│  ✓ 7-day meal plans        │                  │
│  ✓ 5 user profiles         │  Plate graphic   │
│  ✓ Dual objectives         │  showing all     │
│  ✓ 77 decision variables   │  nutrients       │
│                             │                  │
│  📊 Competing Goals:        │                  │
│  • Caloric targets         │                  │
│  • Macronutrient ratios    │                  │
│  (50% carbs, 27.5% fat,   │                  │
│   22.5% protein)           │                  │
│                             │                  │
│  🔒 Constraints:           │                  │
│  • Food categories         │                  │
│  • Meal slots              │                  │
└─────────────────────────────┴──────────────────┘
```

### Visual Elements:
- **Left:** Icons (checkmark, chart, lock) in gold/green
- **Right:** 
  - **INSERT IMAGE:** From report - can use a colorful diagram of a weekly meal plan structure, OR create a graphic showing a plate divided into macronutrient sections (pie chart style)
  - Show the 77-variable structure visually (7 days × 11 slots grid)
- Background: Light gray
- Divider line: Gold accent line between sections

### Design Notes:
- Use bullet points with colored icons
- Numbers in gold for emphasis
- Keep right side visual, not text-heavy
- Modern minimalist approach: lots of white space

---

## **SLIDE 3: DATASETS & ENCODINGS**

### Design Style:
**Three-column comparison layout**
- Clean, structured, data-forward

### Content Layout:
```
┌─────────────────────────────────────────────────────┐
│  DATASETS & ENCODINGS                              │
├──────────────────┬──────────────────┬──────────────┤
│  USERS           │  FOOD CATALOG    │  ENCODINGS   │
│                  │                  │              │
│  👤 5 Profiles   │  🍖 2,616 Items  │  🔢 Type 1:  │
│  📊 Ages:        │  ⚡ Complete     │  Direct-Index│
│  17, 30, 40,     │    Nutrition     │  Integer ID  │
│  55, 72          │    Data          │  Vector      │
│                  │                  │              │
│  🎯 Targets:     │  🥗 Categories:  │  🔢 Type 2:  │
│  1,401-3,103     │  Fruits, Veggies,│  Random-Key  │
│  kcal/day        │  Proteins,       │  Real [0,1]⁷⁷│
│                  │  Grains, etc.    │  Vector      │
│                  │                  │              │
│  ✅ Both feasibility-preserving: constraints built-in!
└─────────────────────────────────────────────────────┘
```

### Visual Elements:
- **Left column:** User profile icons (diverse ages) with color coding
- **Middle column:** Food items grid (colorful food illustrations, 4-6 items visible)
- **Right column:** Encoding visualization 
  - **INSERT IMAGE:** From report - show the encoding example (the boolean array [0,1,0,0,1,1,0,1,1,0] and permutation [0,2,1,4,3,5,7,8,6,9])
  - Use color differentiation: blue for direct-index, green for random-key

### Design Notes:
- Use 3 distinct background colors (very light variants of primary palette)
- Each column should have a subtle border/shadow
- Icons large and colorful (80-100px)
- Final line about feasibility should be gold and bold

---

## **SLIDE 4: FITNESS FUNCTIONS & CONSTRAINTS**

### Design Style:
**Equation-focused with visual constraint representation**
- Top half: Fitness functions (highlighted)
- Bottom half: Constraint handling explanation

### Content Layout:
```
┌──────────────────────────────────────────────────────┐
│  FITNESS FUNCTIONS                                   │
│                                                      │
│  f₁ = Σ |daily_calories - target|                   │
│       [Caloric Balance]                              │
│                                                      │
│  f₂ = Σ (|%carbs - 50| + |%fat - 27.5| +           │
│       |%protein - 22.5|) [Macronutrient Balance]   │
├──────────────────────────────────────────────────────┤
│  CONSTRAINT HANDLING: ENFORCED BY ENCODING            │
│                                                      │
│  ✅ Generator only draws from valid domains          │
│  ✅ All variators respect admissible foods           │
│  ✅ Zero infeasible solutions generated              │
│  ✅ No repair/penalty strategies needed              │
│                                                      │
│  KEY INSIGHT: Feasibility is guaranteed by design    │
└──────────────────────────────────────────────────────┘
```

### Visual Elements:
- **Top section (equations):**
  - Each formula in a rounded-corner box with different background colors
  - f₁ box: Light blue background
  - f₂ box: Light green background
  - Use large, bold text for math (36pt minimum)
  - Labels in italics below each equation (18pt)

- **Bottom section (constraints):**
  - Checkmarks in gold
  - Four checkpoints flowing left-to-right or in a stack
  - Key insight in a gold-outlined box with white background

- **Optional visual:**
  - **INSERT IMAGE:** From report - the constraint diagram showing how tasks must be ordered (if you have a flowchart showing feasibility preservation)

### Design Notes:
- Separate top and bottom with a gold divider line
- Equations should be readable from far away (large fonts)
- Checkmarks large (40-50px), gold color
- Make the "KEY INSIGHT" line stand out: larger font, gold text on light background

---

## **SLIDE 5: METAHEURISTICS OVERVIEW**

### Design Style:
**Algorithm comparison grid with icons**
- 4-quadrant layout showing all algorithms at once
- Color-coded by type (Evolutionary vs. Swarm)

### Content Layout:
```
┌─────────────────────────────┬─────────────────────────────┐
│  EVOLUTIONARY ALGORITHMS    │  SWARM ALGORITHMS           │
├────────┬────────────────────┼────────┬────────────────────┤
│  NSGA- │ • Non-dominated    │ MOPSO  │ • Particle swarm   │
│   II   │   sorting          │        │ • Fast: 0.37s      │
│        │ • Crowding distance│        │ • Moderate quality │
│        │ • Population: 80   │        │ • Continuous space │
│        │ • Generations: 80  │        │                    │
│        │ • Both encodings   │        │                    │
├────────┼────────────────────┼────────┼────────────────────┤
│  PAES  │ • (1+1) strategy   │ P-ACO  │ • Ant colony       │
│        │ • Archive-based    │        │ • Competitive HV   │
│        │ • Single solution  │        │ • Slow: 33.5s      │
│        │ • Generations: 800 │        │ • Pheromone-based  │
│        │ • Deep exploration │        │                    │
└────────┴────────────────────┴────────┴────────────────────┘
```

### Visual Elements:
- **Top-left section (NSGA-II & PAES):**
  - Background: Very light blue
  - Icons: DNA helix (NSGA-II), Evolution arrows (PAES)
  - Each box has a 4px blue left border

- **Top-right section (MOPSO & P-ACO):**
  - Background: Very light green
  - Icons: Particle swarm (MOPSO), Ant trail (P-ACO)
  - Each box has a 4px green left border

- **Center divider:** Gold line separating Evolutionary | Swarm

- **Overall:** 4 equal boxes arranged in 2×2 grid

### Design Notes:
- Large algorithm names (40pt, bold)
- Icons 100-120px, placed top-right of each box
- Bullet points: 18pt, with small icon bullets
- Color differentiation crucial: Blue section vs. Green section
- Use subtle gradient within each box (very light, only 10% opacity)

---

## **SLIDE 6: EVOLUTIONARY ALGORITHMS DEEP DIVE**

### Design Style:
**Split comparison: NSGA-II (left) vs PAES (right) with visual representation**
- Left 45%: NSGA-II with visualization
- Right 45%: PAES with visualization

### Content Layout:
```
┌──────────────────────────────┬──────────────────────────────┐
│  NSGA-II                     │  PAES                        │
│                              │                              │
│  Maintains Population        │  Single-Solution Trajectory  │
│  ┌─────────────────────┐    │  ┌─────────────────────┐    │
│  │ ✓ Non-dominated     │    │  │ ✓ Archive-based     │    │
│  │   sorting           │    │  │   acceptance        │    │
│  │ ✓ Crowding distance │    │  │ ✓ Adaptive grid     │    │
│  │ ✓ Diverse Fronts    │    │  │ ✓ Deep exploration  │    │
│  └─────────────────────┘    │  └─────────────────────┘    │
│                              │                              │
│  📊 Parameters:              │  📊 Parameters:              │
│  • Pop: 80                   │  • Pop: 1 (by design)       │
│  • Gen: 80                   │  • Gen: 800                 │
│  • Best for: Coverage        │  • Best for: Specialization │
│                              │                              │
│  [VISUALIZATION]             │  [VISUALIZATION]            │
│  Diverse point cloud         │  Single trajectory path     │
└──────────────────────────────┴──────────────────────────────┘
```

### Visual Elements:
- **Left section:**
  - Background: Very light blue with subtle gradient
  - NSGA-II heading in dark blue (40pt)
  - **INSERT IMAGE:** From report - Pareto front visualization showing a diverse, well-distributed set of points (scatter plot from experiments/demo_overview.png or similar)
  - Use blue accent color for boxes

- **Right section:**
  - Background: Slightly different light blue (more muted)
  - PAES heading in dark blue (40pt)
  - **INSERT IMAGE:** From report - Archive visualization showing a more concentrated exploration (or create a visual showing single-solution trajectory)
  - Use dark blue accent color for boxes

- **Center divider:** Gold vertical line

### Design Notes:
- Both sides should mirror each other in layout
- Images should be circular or rounded-corner (not rectangular)
- Parameter boxes: light background with border, NOT filled
- Visualizations should take up 40% of each side (height)
- Icons: Population icon for NSGA-II, Archive/folder icon for PAES

---

## **SLIDE 7: SWARM ALGORITHMS DEEP DIVE**

### Design Style:
**Speed vs. Quality trade-off showcase**
- Left: MOPSO (Speed champion)
- Right: P-ACO (Quality focus)
- Visual emphasizing the trade-off

### Content Layout:
```
┌──────────────────────────────┬──────────────────────────────┐
│  MOPSO: SPEED CHAMPION       │  P-ACO: QUALITY FOCUS        │
│                              │                              │
│  ⚡ 0.37 seconds per run     │  🧠 Competitive HV: 435k    │
│  (90× faster than P-ACO)     │  (3rd place overall)        │
│                              │                              │
│  Particle Swarm Optimizer    │  Pareto Ant Colony          │
│  ┌─────────────────────┐    │  ┌─────────────────────┐    │
│  │ ✓ Leader selection  │    │  │ ✓ Pheromone trails  │    │
│  │ ✓ Sigma rule        │    │  │ ✓ Archive learning  │    │
│  │ ✓ Continuous space  │    │  │ ✓ Diversity favored │    │
│  │ ✓ Fast convergence  │    │  │ ✓ Deep exploitation │    │
│  └─────────────────────┘    │  └─────────────────────┘    │
│                              │                              │
│  📊 Parameters:              │  📊 Parameters:              │
│  • Pop: 30                   │  • Pop: 60                  │
│  • Gen: 80                   │  • Gen: 40                  │
│  • Encoding: Random-Key      │  • Encoding: Direct-Index   │
│  (continuous velocity update)│  (discrete task assignment) │
│                              │                              │
│  [SPEED METER: 🟢 FAST]      │  [SPEED METER: 🔴 SLOW]    │
│  [HQ METER:    🟡 MEDIUM]    │  [HQ METER:    🟢 GOOD]    │
└──────────────────────────────┴──────────────────────────────┘
```

### Visual Elements:
- **Left section (MOPSO):**
  - Background: Very light green with subtle speedline pattern
  - MOPSO heading in emerald green (40pt)
  - Lightning bolt icon (80px) for speed
  - **INSERT IMAGE:** Particle swarm visualization (scatter plot showing particle movement pattern, or from report)
  - Speed/Quality meters at bottom as horizontal bars (green full for speed, yellow/medium for quality)

- **Right section (P-ACO):**
  - Background: Slightly different light green
  - P-ACO heading in dark green (40pt)
  - Brain/ant icon (80px) for intelligence
  - **INSERT IMAGE:** Pheromone trail visualization or ant colony behavior diagram
  - Speed/Quality meters at bottom (red/slow for speed, green full for quality)

- **Emphasis:** Large speed metric (0.37s) in top-left, large HV (435k) in top-right

### Design Notes:
- Use speedometer/gauge visual for the trade-off concept
- Color contrast: Green on left, green on right but different shades
- Speed bars should be prominent and easy to compare
- Use emoji or simple icons for meters (⚡ for speed, 🎯 for quality)
- Add a small note about encoding difference at bottom

---

## **SLIDE 8: EXPERIMENTAL DESIGN**

### Design Style:
**Process flow with emphasis on scale and rigor**
- Top: Tuning phase
- Bottom: Benchmark phase
- Large numbers showcased

### Content Layout:
```
┌─────────────────────────────────────────────────────┐
│  HYPERPARAMETER TUNING PHASE                        │
│                                                     │
│  2 Subjects → 56 Cells/Algorithm → 5 Replicates   │
│              └─→ 560 Tuning Runs                   │
│                  Selected by: Highest Hypervolume  │
├─────────────────────────────────────────────────────┤
│  FULL BENCHMARK PHASE                              │
│                                                     │
│  5 Configs × 5 Subjects × 30 Replicates            │
│       ↓           ↓              ↓                  │
│     NSGA-II      Users    Statistical Power ✓     │
│     PAES         (17,30,                           │
│     MOPSO        40,55,72)  n=30 validated         │
│     P-ACO×2                                        │
│                                                     │
│  ⚡ TOTAL: 750 RUNS with Statistical Rigor       │
├─────────────────────────────────────────────────────┤
│  METRICS:                                           │
│  Hypervolume | IGD | Spacing | Δ-Spread | Runtime │
│                                                     │
│  STATISTICAL TESTS:                                 │
│  Wilcoxon Signed-Ranks | Friedman Aligned Ranks   │
└─────────────────────────────────────────────────────┘
```

### Visual Elements:
- **Top section (Tuning):**
  - Flow diagram with arrows showing: 2 Subjects → Grid Search → 560 runs
  - Icons: People icon (subjects), Grid icon (hyperparameter space), Checkmark (selected)
  - Background: Very light gray

- **Middle section (Benchmark):**
  - Large "750 RUNS" text in gold (60-80pt, centered)
  - 3×3 grid showing breakdown (5 configs, 5 subjects, 30 replicates)
  - **Optional image:** INSERT small chart showing distribution of runs across configs
  - Background: Very light blue

- **Bottom section (Metrics):**
  - Metric boxes in a row with icons
  - Small colored boxes for each metric type
  - Background: Light gray

### Design Notes:
- Use large numbers (750) as visual anchor
- Flow diagrams with arrows and icons
- Each phase in distinct background color
- Bottom metrics as horizontal pill-shaped boxes
- Gold color for the "750 RUNS" number for emphasis
- Keep very organized and clear hierarchy

---

## **SLIDE 9: RESULTS – KEY FINDINGS**

### Design Style:
**Data-heavy but visually organized**
- Top: Hypervolume bar chart (PRIMARY)
- Bottom: Objective specialization table and speed comparison

### Content Layout:
```
┌────────────────────────────────────────────────────┐
│  HYPERVOLUME RESULTS (Higher = Better)            │
│                                                    │
│  1.2M │                                            │
│       │      ███                                   │
│  1.0M │      ███  ██                              │
│       │      ███  ██  ███                         │
│  800k │      ███  ██  ███ ███                     │
│       │      ███  ██  ███ ███ ███                 │
│       │     [1]  [2] [3] [4] [5]                 │
│       └───────────────────────────────────        │
│     NSGA-II NSGA-II P-ACO MOPSO PAES             │
│     (RK)    (DI)                                  │
│     1.06M   1.01M   435k   404k   401k            │
│     🥇      🥈      🥉     —      —               │
│                                                    │
├────────────────────────────────────────────────────┤
│  OBJECTIVE SPECIALIZATION                         │
│                                                    │
│  Algorithm      | Best f₁     | Best f₂         │
│  ─────────────────────────────────────────       │
│  NSGA-II (RK)   | 1,105 kcal  | 167.11% ✓       │
│  NSGA-II (DI)   | 1,343 kcal  | 167.77%         │
│  PAES           | 1,988 kcal  | 123.92% 🎯      │
│  MOPSO          | 2,363 kcal  | 175.30%         │
│  P-ACO          | 2,700 kcal  | 179.80%         │
│                                                    │
│  SPEED COMPARISON:                               │
│  MOPSO: ⚡⚡⚡⚡⚡ (0.37s)                         │
│  Others: ⚡⚡ (1.4-2.0s)                          │
│  P-ACO: ⚡ (33.5s)                               │
└────────────────────────────────────────────────────┘
```

### Visual Elements:

**Top section (Bar Chart):**
- **INSERT IMAGE:** From report - experiments/boxplots.png or create a bar chart
- Bars should be color-coded:
  - NSGA-II variants: Bright gold/amber
  - Other algorithms: Emerald green and gray
- Y-axis labeled clearly (Hypervolume)
- Add medal emojis: 🥇 (NSGA-II RK), 🥈 (NSGA-II DI), 🥉 (P-ACO)
- Background: Very light blue gradient
- Bars should have rounded tops (modern look)
- Data labels on top of each bar

**Middle section (Comparison Table):**
- Clean table with alternating light row backgrounds
- NSGA-II rows: light gold tint
- PAES row: light green highlight (best macronutrient)
- Numbers in monospace font
- Checkmark (✓) in gold next to NSGA-II f₁ best
- Target emoji (🎯) next to PAES f₂ best
- Border: 1px gold

**Bottom section (Speed):**
- Horizontal bar chart or emoji-based visualization
- MOPSO: 5 lightning bolts (bright gold)
- Others: 2 lightning bolts (gray)
- P-ACO: 1 lightning bolt (faded)
- Time labels next to each bar

### Design Notes:
- Top section takes 50% of slide
- Table and speed occupy bottom 50%
- High contrast between sections
- Use emojis sparingly but effectively (medals, checkmarks, targets)
- Data should be immediately readable
- Gold color for highlighting winners/best performers

---

## **SLIDE 10: STATISTICAL SIGNIFICANCE & CONCLUSIONS**

### Design Style:
**Two-part slide: Stats (top) + Recommendations (bottom)**
- Top: Statistical rigor confirmation
- Bottom: Actionable conclusions and recommendations

### Content Layout:
```
┌────────────────────────────────────────────────────┐
│  STATISTICAL SIGNIFICANCE                         │
│                                                    │
│  Friedman Omnibus Test (All Metrics)              │
│  p < 10⁻⁷⁰  ✓✓✓ Highly Significant               │
│                                                    │
│  Pairwise Comparisons (Wilcoxon + Shaffer):       │
│  NSGA-II >> PAES, MOPSO, P-ACO ✓✓✓               │
│  All p-values << 0.05 (statistically proven)     │
│                                                    │
│  Within NSGA-II: Encoding choice NOT significant  │
│  (Random-Key vs. Direct-Index: p = 0.359)        │
├────────────────────────────────────────────────────┤
│  RECOMMENDATIONS & CONCLUSIONS                    │
│                                                    │
│  🏆 BEST OVERALL: NSGA-II with Direct-Index      │
│     • Strong Pareto coverage                      │
│     • Slightly better runtime                     │
│     • Fully interpretable decision vectors        │
│                                                    │
│  🎯 ALTERNATIVE CHOICES:                          │
│     Use PAES if: Only need best macronutrient    │
│     Use MOPSO if: Runtime is critical            │
│                                                    │
│  💡 KEY INSIGHT:                                  │
│     Feasibility-preserving encoding eliminated    │
│     constraint overhead & streamlined search     │
│                                                    │
│  Code: github.com/gjorgiandonovski/Diet-Optim    │
└────────────────────────────────────────────────────┘
```

### Visual Elements:

**Top section (Statistics):**
- Large "p < 10⁻⁷⁰" in gold with checkmarks (40pt minimum)
- Three checkmarks in green (✓✓✓) for emphasis
- Friedman and Wilcoxon boxes with different background tints
- Statistical confidence visual: thermometer or gauge showing very high confidence
- Background: Very light gray

**Bottom section (Conclusions):**
- Trophy icon (🏆) for best choice
- Target icon (🎯) for alternatives
- Lightbulb icon (💡) for key insight
- Each recommendation in its own pill-shaped box with subtle border
- Boxes color-coded: Gold for "BEST", Green for "ALTERNATIVES", Amber for "INSIGHT"
- GitHub link as a hyperlink (blue, underlined)

### Design Notes:
- Split clearly with gold divider line
- Top section emphasizes statistical rigor (use multiple checkmarks, large p-value)
- Bottom section gives clear, actionable guidance
- Use icons consistently (from top slides)
- GitHub link should be visible and clickable
- Final line (Key Insight) should stand out in gold box with white background
- Keep bottom section well-spaced (breathing room around boxes)

---

## **SUMMARY OF IMAGE PLACEMENTS**

Here's where to INSERT images from the report:

| Slide | Image to Insert | Source |
|-------|-----------------|--------|
| 2 | Encoding example (boolean array + permutation) | Figure or create from example in report |
| 2 | Weekly meal plan structure (7×11 grid visual) | Create visualization or from methods |
| 4 | Feasibility constraint diagram (optional) | From report methods section |
| 6 | Pareto front scatter plot (NSGA-II results) | `experiments/demo_overview.png` or `boxplots.png` |
| 6 | Archive visualization (PAES trajectory) | `experiments/demo_overview.png` center plot |
| 7 | Particle swarm visualization | Create or from MOPSO algorithm section |
| 7 | Pheromone trail visualization | Create or from P-ACO algorithm section |
| 9 | Hypervolume bar chart | `experiments/boxplots.png` (top-left plot) or create bar chart |
| 9 | Objective space scatter plot | `experiments/best_pts_subject_1.png` |

---

## **DESIGN CONSISTENCY CHECKLIST**

- [ ] All headings: Montserrat Bold or Inter Bold, 40-48pt
- [ ] All body text: Open Sans or Lato, 18-22pt
- [ ] Color palette: Blue + Green + Gold + Neutrals (no other colors)
- [ ] Spacing: Minimum 40px margins, generous padding
- [ ] Icons: Consistent style (Flaticons thin-line style)
- [ ] Visualizations: Rounded corners, no sharp edges
- [ ] Gold accent used for: Key numbers, highlights, dividers, best performers
- [ ] Gradients: Subtle, only in backgrounds (max 10-15% opacity shift)
- [ ] Modern look: Clean lines, whitespace, no clutter
- [ ] Readable from distance: Test legibility at presentation distance

---

## **CANVA GENERATION INSTRUCTIONS**

1. **Create a 10-slide presentation** in Canva
2. **Use this document as a reference** for each slide's design
3. **Color palette:** Follow the colors specified (Blue: #1F4788, Green: #2D8659, Gold: #D4A574)
4. **Typography:** Use sans-serif fonts (Montserrat for headings, Open Sans for body)
5. **Visual style:** Modern, minimalist, data-driven
6. **For charts/data:** Use professional-looking visualizations with rounded corners
7. **Image insertion:** Follow the "IMAGE PLACEMENTS" table above when available
8. **Spacing:** Ensure generous margins and breathing room (40px minimum)
9. **Icons:** Download from Flaticons or Heroicons (thin-line, modern style)
10. **Final check:** View in presentation mode to ensure readability from distance

---

## **TIMING GUIDE FOR 10-MINUTE PRESENTATION**

- **Slide 1 (Title):** 30 seconds
- **Slide 2 (Problem):** 1 minute
- **Slide 3 (Datasets):** 45 seconds
- **Slide 4 (Fitness/Constraints):** 1 minute
- **Slide 5 (Algorithms Overview):** 1 minute
- **Slide 6 (Evolutionary Deep Dive):** 1 minute
- **Slide 7 (Swarm Deep Dive):** 1 minute
- **Slide 8 (Experimental Design):** 45 seconds
- **Slide 9 (Results & Stats):** 2 minutes
- **Slide 10 (Conclusions):** 1.5 minutes
- **Buffer for Q&A:** 30 seconds

**Total: 10 minutes exactly**

