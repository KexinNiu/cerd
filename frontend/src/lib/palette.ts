/**
 * Organism colors are fixed by entity, never by rank — a filter that removes
 * an organism must not repaint the survivors.
 *
 * This four-hue set was chosen by exhaustively validating every 4-combination
 * of the reference categorical ramp against the all-pairs colorblind and
 * normal-vision floors in BOTH light and dark surfaces; it is one of only two
 * that pass. The dark-mode green/ochre pair sits at CVD dE 6.9 (the 6-8 floor
 * band), which is legal only alongside secondary encoding — the legend, the
 * hover card and the evidence table all name the organism in text.
 */
export const ORGANISM_COLORS_LIGHT: Record<string, string> = {
  "Escherichia coli": "#2a78d6",
  "Bacillus subtilis": "#eda100",
  "Saccharomyces cerevisiae": "#e87ba4",
  "Caenorhabditis elegans": "#008300",
};

export const ORGANISM_COLORS_DARK: Record<string, string> = {
  "Escherichia coli": "#3987e5",
  "Bacillus subtilis": "#c98500",
  "Saccharomyces cerevisiae": "#d55181",
  "Caenorhabditis elegans": "#008300",
};

const FALLBACK_LIGHT = "#52514e";
const FALLBACK_DARK = "#c3c2b7";

export function organismColor(organism: string, dark: boolean): string {
  const map = dark ? ORGANISM_COLORS_DARK : ORGANISM_COLORS_LIGHT;
  return map[organism] ?? (dark ? FALLBACK_DARK : FALLBACK_LIGHT);
}

/** Marker shape carries assay, so identity never rests on color alone. */
export const ASSAY_SYMBOLS: Record<string, string> = {
  CFU: "circle",
  survival_curve: "square",
  OD: "diamond",
  spot_assay: "triangle-up",
  microscopy: "cross",
  other: "x",
};

export function assaySymbol(assay: string): string {
  return ASSAY_SYMBOLS[assay] ?? "x";
}

/** Grouped for the organism panel — taxonomy the curators actually use. */
export const ORGANISM_GROUPS: { label: string; organisms: string[] }[] = [
  { label: "Bacteria", organisms: ["Escherichia coli", "Bacillus subtilis"] },
  { label: "Yeast", organisms: ["Saccharomyces cerevisiae"] },
  { label: "Multicellular", organisms: ["Caenorhabditis elegans"] },
];
