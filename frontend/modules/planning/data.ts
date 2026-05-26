import type {
  PlanningLocationType,
  PlanningProjectType,
  PlanningResourceType,
  PlanningWbsTemplate,
} from "./types";

type TemplateGroup = {
  phase: string;
  category: string;
  templates: Array<{
    title: string;
    duration: number;
    description: string;
    repeatable?: boolean;
    hints?: Partial<Record<PlanningResourceType, number>>;
  }>;
};

export const planningProjectTypes: Array<{
  value: PlanningProjectType;
  label: string;
}> = [
  {
    value: "residential_tower",
    label: "Residential Tower",
  },
  {
    value: "commercial_building",
    label: "Commercial Building",
  },
  {
    value: "mixed_use",
    label: "Mixed Use",
  },
  {
    value: "industrial",
    label: "Industrial",
  },
];

export const planningLocationTypes: Array<{
  value: PlanningLocationType;
  label: string;
}> = [
  { value: "tower", label: "Tower" },
  { value: "floor", label: "Floor" },
  { value: "zone", label: "Zone" },
  { value: "room", label: "Room" },
  { value: "sector", label: "Sector" },
];

export const planningResourceTypes: Array<{
  value: PlanningResourceType;
  label: string;
  unit: string;
}> = [
  { value: "manpower", label: "Manpower", unit: "people" },
  { value: "material", label: "Material", unit: "units" },
  { value: "equipment", label: "Equipment", unit: "hours" },
];

const templateGroups: TemplateGroup[] = [
  {
    phase: "Phase 0 — Pre-Construction",
    category: "pre-construction",
    templates: [
      {
        title: "Feasibility Study",
        duration: 5,
        description: "Early project viability and scope review.",
        repeatable: false,
      },
      {
        title: "Geotechnical Study",
        duration: 4,
        description: "Site soil and ground condition evaluation.",
        repeatable: false,
      },
      {
        title: "Architectural Design",
        duration: 6,
        description: "Primary architectural package preparation.",
        repeatable: false,
      },
      {
        title: "Structural Design",
        duration: 6,
        description: "Structural system definition and detailing.",
        repeatable: false,
      },
      {
        title: "BIM Coordination",
        duration: 4,
        description: "Cross-discipline model coordination.",
        repeatable: false,
      },
      {
        title: "Clash Detection",
        duration: 3,
        description: "Constructability clash review.",
        repeatable: false,
      },
      {
        title: "Quantity Surveying",
        duration: 4,
        description: "Bill of quantities and takeoff preparation.",
        repeatable: false,
      },
      {
        title: "Permits",
        duration: 5,
        description: "Authority approvals and permit readiness.",
        repeatable: false,
      },
    ],
  },
  {
    phase: "Phase 1 — Site Setup",
    category: "site-setup",
    templates: [
      {
        title: "Site Fencing",
        duration: 2,
        description: "Secure site perimeter setup.",
        hints: { manpower: 4, material: 20 },
      },
      {
        title: "Temporary Power",
        duration: 2,
        description: "Temporary power distribution setup.",
        hints: { manpower: 3, equipment: 6 },
      },
      {
        title: "Temporary Water",
        duration: 2,
        description: "Temporary water line setup.",
        hints: { manpower: 3, material: 8 },
      },
      {
        title: "Site Office",
        duration: 3,
        description: "Operational command office setup.",
        hints: { manpower: 4, material: 10 },
      },
      {
        title: "Internet",
        duration: 1,
        description: "Site communication and connectivity setup.",
        hints: { manpower: 2, equipment: 4 },
      },
      {
        title: "Site Access",
        duration: 2,
        description: "Access and movement path preparation.",
        hints: { manpower: 4, equipment: 4 },
      },
    ],
  },
  {
    phase: "Phase 2 — Excavation & Shoring",
    category: "earthworks",
    templates: [
      {
        title: "Excavation",
        duration: 4,
        description: "Primary excavation works.",
        hints: { manpower: 6, equipment: 24 },
      },
      {
        title: "Soil Removal",
        duration: 3,
        description: "Spoil transport and removal.",
        hints: { manpower: 5, equipment: 18 },
      },
      {
        title: "Level Control",
        duration: 2,
        description: "Excavation level checking and control.",
        hints: { manpower: 2 },
      },
      {
        title: "Nailing",
        duration: 3,
        description: "Slope stabilization nailing works.",
        hints: { manpower: 5, equipment: 10 },
      },
      {
        title: "Shotcrete",
        duration: 2,
        description: "Shoring face shotcrete application.",
        hints: { manpower: 4, material: 12, equipment: 8 },
      },
      {
        title: "Drainage",
        duration: 2,
        description: "Temporary or permanent drainage works.",
        hints: { manpower: 3, material: 8 },
      },
    ],
  },
  {
    phase: "Phase 3 — Foundation",
    category: "foundation",
    templates: [
      {
        title: "Subgrade Preparation",
        duration: 2,
        description: "Subgrade cleaning and readiness.",
        hints: { manpower: 4, equipment: 6 },
      },
      {
        title: "Lean Concrete",
        duration: 2,
        description: "Blinding concrete placement.",
        hints: { manpower: 4, material: 10, equipment: 6 },
      },
      {
        title: "Reinforcement",
        duration: 3,
        description: "Foundation reinforcement works.",
        hints: { manpower: 6, material: 14 },
      },
      {
        title: "Formwork",
        duration: 3,
        description: "Foundation formwork preparation.",
        hints: { manpower: 5, material: 10 },
      },
      {
        title: "Concrete Pour",
        duration: 1,
        description: "Foundation concrete placement.",
        hints: { manpower: 6, material: 16, equipment: 10 },
      },
      {
        title: "Concrete Testing",
        duration: 1,
        description: "Quality testing during concrete placement.",
        hints: { manpower: 2, equipment: 2 },
      },
    ],
  },
  {
    phase: "Phase 4 — Structural Frame",
    category: "structure",
    templates: [
      {
        title: "Columns",
        duration: 3,
        description: "Column cycle execution.",
        hints: { manpower: 6, material: 12, equipment: 8 },
      },
      {
        title: "Beams",
        duration: 3,
        description: "Beam reinforcement and casting cycle.",
        hints: { manpower: 6, material: 12, equipment: 8 },
      },
      {
        title: "Slabs",
        duration: 4,
        description: "Slab reinforcement and pouring cycle.",
        hints: { manpower: 8, material: 16, equipment: 10 },
      },
      {
        title: "Curing",
        duration: 2,
        description: "Concrete curing follow-up.",
        hints: { manpower: 2, material: 4 },
      },
      {
        title: "Form Removal",
        duration: 2,
        description: "Formwork stripping and clearance.",
        hints: { manpower: 4, equipment: 4 },
      },
    ],
  },
  {
    phase: "Phase 5 — Masonry & Partition",
    category: "masonry",
    templates: [
      {
        title: "Block Work",
        duration: 3,
        description: "Partition and block wall execution.",
        hints: { manpower: 5, material: 20 },
      },
      {
        title: "Wall Posts",
        duration: 2,
        description: "Wall post installation.",
        hints: { manpower: 3, material: 8 },
      },
      {
        title: "Openings",
        duration: 2,
        description: "Door and window opening preparation.",
        hints: { manpower: 3, material: 6 },
      },
      {
        title: "Lintels",
        duration: 2,
        description: "Lintel placement and support works.",
        hints: { manpower: 3, material: 6 },
      },
    ],
  },
  {
    phase: "Phase 6 — MEP Rough-In",
    category: "mep-rough-in",
    templates: [
      {
        title: "Water Piping",
        duration: 3,
        description: "Water line rough-in installation.",
        hints: { manpower: 4, material: 12 },
      },
      {
        title: "Drainage",
        duration: 3,
        description: "Drainage network rough-in.",
        hints: { manpower: 4, material: 10 },
      },
      {
        title: "Electrical Conduits",
        duration: 3,
        description: "Electrical conduit rough-in.",
        hints: { manpower: 4, material: 12 },
      },
      {
        title: "Cable Trays",
        duration: 2,
        description: "Cable tray support and installation.",
        hints: { manpower: 3, material: 8 },
      },
      {
        title: "Fire Alarm",
        duration: 2,
        description: "Fire alarm containment rough-in.",
        hints: { manpower: 2, material: 6 },
      },
      {
        title: "CCTV",
        duration: 2,
        description: "CCTV pathway rough-in.",
        hints: { manpower: 2, material: 5 },
      },
    ],
  },
  {
    phase: "Phase 7 — Finishes",
    category: "finishes",
    templates: [
      {
        title: "Plaster",
        duration: 3,
        description: "Wall and ceiling plaster works.",
        hints: { manpower: 5, material: 14 },
      },
      {
        title: "Flooring",
        duration: 3,
        description: "Floor finish installation.",
        hints: { manpower: 4, material: 12 },
      },
      {
        title: "Painting",
        duration: 2,
        description: "Surface painting works.",
        hints: { manpower: 4, material: 10 },
      },
      {
        title: "Ceiling Systems",
        duration: 2,
        description: "Ceiling framing and finishing.",
        hints: { manpower: 4, material: 8 },
      },
    ],
  },
  {
    phase: "Phase 8 — Facade",
    category: "facade",
    templates: [
      {
        title: "Substructure",
        duration: 3,
        description: "Facade substructure installation.",
        hints: { manpower: 5, material: 10, equipment: 6 },
      },
      {
        title: "Stone",
        duration: 3,
        description: "Stone facade execution.",
        hints: { manpower: 5, material: 14, equipment: 6 },
      },
      {
        title: "Curtain Wall",
        duration: 4,
        description: "Curtain wall installation cycle.",
        hints: { manpower: 6, material: 12, equipment: 8 },
      },
      {
        title: "Waterproofing",
        duration: 2,
        description: "Facade or roof waterproofing works.",
        hints: { manpower: 3, material: 10 },
      },
    ],
  },
  {
    phase: "Phase 9 — MEP Final Fix",
    category: "mep-final-fix",
    templates: [
      {
        title: "Equipment Installation",
        duration: 3,
        description: "Final MEP equipment placement.",
        hints: { manpower: 4, equipment: 8 },
      },
      {
        title: "Panels",
        duration: 2,
        description: "Panel installation and fixing.",
        hints: { manpower: 3, material: 6 },
      },
      {
        title: "Lighting",
        duration: 2,
        description: "Lighting fixture final fix.",
        hints: { manpower: 3, material: 6 },
      },
      {
        title: "BMS",
        duration: 2,
        description: "Building management system final integration.",
        hints: { manpower: 2, equipment: 4 },
      },
    ],
  },
  {
    phase: "Phase 10 — Vertical Transportation",
    category: "vertical-transportation",
    templates: [
      {
        title: "Elevator Rails",
        duration: 3,
        description: "Rail installation in shafts.",
        hints: { manpower: 4, equipment: 8 },
      },
      {
        title: "Motors",
        duration: 2,
        description: "Motor installation.",
        hints: { manpower: 3, equipment: 6 },
      },
      {
        title: "Cabins",
        duration: 2,
        description: "Cabin assembly and placement.",
        hints: { manpower: 3, equipment: 6 },
      },
      {
        title: "Testing",
        duration: 2,
        description: "Lift testing and readiness checks.",
        hints: { manpower: 2, equipment: 2 },
      },
    ],
  },
  {
    phase: "Phase 11 — External Works",
    category: "external-works",
    templates: [
      {
        title: "Pavement",
        duration: 3,
        description: "Pavement and hardscape preparation.",
        hints: { manpower: 4, material: 16, equipment: 8 },
      },
      {
        title: "Landscaping",
        duration: 3,
        description: "Landscape installation and shaping.",
        hints: { manpower: 4, material: 12 },
      },
      {
        title: "Asphalt",
        duration: 2,
        description: "Asphalt laying works.",
        hints: { manpower: 4, material: 12, equipment: 6 },
      },
      {
        title: "Lighting",
        duration: 2,
        description: "External lighting installation.",
        hints: { manpower: 3, material: 6 },
      },
    ],
  },
  {
    phase: "Phase 12 — Testing & Commissioning",
    category: "commissioning",
    templates: [
      {
        title: "Electrical Testing",
        duration: 2,
        description: "Electrical systems testing.",
        hints: { manpower: 2, equipment: 3 },
      },
      {
        title: "HVAC Testing",
        duration: 2,
        description: "HVAC testing and balancing checks.",
        hints: { manpower: 2, equipment: 3 },
      },
      {
        title: "Startup",
        duration: 2,
        description: "System startup activities.",
        hints: { manpower: 2, equipment: 2 },
      },
      {
        title: "Integration Tests",
        duration: 2,
        description: "Cross-system integration verification.",
        hints: { manpower: 2, equipment: 2 },
      },
    ],
  },
  {
    phase: "Phase 13 — Handover",
    category: "handover",
    templates: [
      {
        title: "Punch List",
        duration: 2,
        description: "Final defect and close-out list.",
        repeatable: false,
      },
      {
        title: "As-Built Documents",
        duration: 2,
        description: "As-built record package preparation.",
        repeatable: false,
      },
      {
        title: "O&M Manuals",
        duration: 2,
        description: "Operations and maintenance handover package.",
        repeatable: false,
      },
      {
        title: "Final Delivery",
        duration: 1,
        description: "Client handover milestone.",
        repeatable: false,
      },
    ],
  },
  {
    phase: "Phase 14 — HSE",
    category: "hse",
    templates: [
      {
        title: "PPE",
        duration: 1,
        description: "Personal protective equipment readiness.",
      },
      {
        title: "Work Permits",
        duration: 1,
        description: "Permit-to-work operational checks.",
      },
      {
        title: "Height Safety",
        duration: 1,
        description: "Work-at-height readiness controls.",
      },
      {
        title: "Waste Management",
        duration: 1,
        description: "Waste segregation and control.",
      },
    ],
  },
  {
    phase: "Phase 15 — Quality Control",
    category: "quality-control",
    templates: [
      {
        title: "Material Testing",
        duration: 1,
        description: "Material quality testing checks.",
      },
      {
        title: "Execution Inspection",
        duration: 1,
        description: "Execution inspection and hold point review.",
      },
      {
        title: "NCR",
        duration: 1,
        description: "Non-conformance handling.",
      },
      {
        title: "Laboratory Reports",
        duration: 1,
        description: "Laboratory testing record package.",
      },
    ],
  },
  {
    phase: "Phase 16 — Digital Construction & Data",
    category: "digital-construction",
    templates: [
      {
        title: "Data Governance",
        duration: 2,
        description: "Operational data standards and ownership.",
        repeatable: false,
      },
      {
        title: "KPI Dashboards",
        duration: 2,
        description: "Operational dashboard setup.",
        repeatable: false,
      },
      {
        title: "Workflow Automation",
        duration: 2,
        description: "Lightweight digital workflow setup.",
        repeatable: false,
      },
      {
        title: "Operational Analytics",
        duration: 2,
        description: "Operational visibility configuration.",
        repeatable: false,
      },
      {
        title: "Forecasting",
        duration: 2,
        description: "Future-ready forecasting placeholder template.",
        repeatable: false,
      },
    ],
  },
];

function createTemplateId(title: string): string {
  return title
    .toLowerCase()
    .replace(/&/g, "and")
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-|-$/g, "");
}

export const planningWbsTemplates: PlanningWbsTemplate[] =
  templateGroups.flatMap((group) =>
    group.templates.map((template) => ({
      id: createTemplateId(template.title),
      code: `${group.category.toUpperCase().slice(0, 4)}-${createTemplateId(template.title)
        .toUpperCase()
        .slice(0, 8)}`,
      title: template.title,
      category: group.category,
      phase: group.phase,
      description: template.description,
      repeatable: template.repeatable ?? true,
      defaultDurationDays: template.duration,
      defaultResourceHints: template.hints ?? {},
    }))
  );

export const planningWbsTemplatesByPhase = templateGroups.map(
  (group) => ({
    phase: group.phase,
    templates: planningWbsTemplates.filter(
      (template) => template.phase === group.phase
    ),
  })
);

export const workflowSuggestionMap: Record<
  string,
  { nextTitles: string[]; note: string }
> = {
  excavation: {
    nextTitles: [
      "Lean Concrete",
      "Drainage",
      "Subgrade Preparation",
    ],
    note: "Earthworks can branch depending on stability and site readiness.",
  },
  "lean-concrete": {
    nextTitles: ["Reinforcement", "Formwork"],
    note: "Foundation preparation can continue in parallel.",
  },
  reinforcement: {
    nextTitles: ["Formwork", "Concrete Pour"],
    note: "Steel readiness usually unlocks forming and pour preparation.",
  },
  "concrete-pour": {
    nextTitles: ["Concrete Testing", "Columns", "Slabs"],
    note: "Post-pour follow-up and next structural cycles may start next.",
  },
  columns: {
    nextTitles: [
      "Beams",
      "Slabs",
      "Retaining Wall",
      "Underground Utilities",
    ],
    note: "Structural work can branch by location and strategy.",
  },
  slabs: {
    nextTitles: [
      "Block Work",
      "Electrical Conduits",
      "Waterproofing",
    ],
    note: "Interior and envelope packages can start in parallel after slab readiness.",
  },
  "block-work": {
    nextTitles: ["Wall Posts", "Openings", "Plaster"],
    note: "Partition work typically unlocks finishes and follow-up detailing.",
  },
  plaster: {
    nextTitles: ["Flooring", "Painting", "Ceiling Systems"],
    note: "Finish packages can be sequenced tactically by zone.",
  },
  "electrical-conduits": {
    nextTitles: ["Cable Trays", "Fire Alarm", "CCTV"],
    note: "MEP rough-in branches should remain optional.",
  },
  "equipment-installation": {
    nextTitles: ["Panels", "Lighting", "BMS"],
    note: "Final fix can progress through several optional next packages.",
  },
};

export function getWorkflowSuggestionsForTemplate(
  templateTitle: string
): string[] {
  const key = createTemplateId(templateTitle);
  return workflowSuggestionMap[key]?.nextTitles ?? [];
}

export function getWorkflowSuggestionNote(
  templateTitle: string
): string {
  const key = createTemplateId(templateTitle);
  return (
    workflowSuggestionMap[key]?.note ??
    "No predefined next-path suggestions yet for this template."
  );
}
