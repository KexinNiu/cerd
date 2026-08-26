import { useEffect, useMemo, useRef } from "react";
import Plotly from "plotly.js-basic-dist-min";
import type { CerdRecord, Condition } from "../types";
import { assaySymbol, organismColor } from "../lib/palette";
import { doseGradients, levelOf, sourceLabel } from "../lib/filters";
import type { Measure } from "../lib/measures";
import { useDarkMode } from "../lib/useDarkMode";

interface Props {
  records: CerdRecord[];
  condition: Condition;
  measure: Measure;
  yLog: boolean;
}

const ESC = (s: string) => s.replace(/</g, "&lt;").replace(/>/g, "&gt;");

function hoverText(r: CerdRecord): string {
  const level =
    r.condition === "UV"
      ? `${r.dose_value} ${r.dose_unit ?? ""} · ${Math.round(r.dose_j_m2 ?? 0)} J/m²`
      : `${r.temp_c} °C${r.temp_shift ? ` · ${r.temp_shift.replace(/_/g, " ")}` : ""}`;
  const quote = r.source_quote.length > 180
    ? `${r.source_quote.slice(0, 177)}…`
    : r.source_quote;
  return [
    `<b><i>${ESC(r.organism)}</i></b>`,
    `strain: ${ESC(r.strain ?? "not stated")}`,
    `${r.condition === "UV" ? "dose" : "temperature"}: ${ESC(level)}`,
    `response: ${r.response_value} ${ESC(r.response_unit ?? "")} (${ESC(r.response_type.replace(/_/g, " "))})`,
    `assay: ${ESC(r.assay)} · medium: ${ESC(r.medium ?? "not stated")}`,
    `evidence: ${ESC(r.evidence_level)}`,
    `source: ${ESC(sourceLabel(r))}`,
    `<i>“${ESC(quote)}”</i>`,
  ].join("<br>");
}

export function ScatterPlot({ records, condition, measure, yLog }: Props) {
  const host = useRef<HTMLDivElement>(null);
  const dark = useDarkMode();

  const organisms = useMemo(
    () => [...new Set(records.map((r) => r.organism))].sort(),
    [records],
  );

  const traces = useMemo(() => {
    const out: Partial<Plotly.PlotData>[] = [];

    // Thin dashed connectors first, so markers sit on top of them.
    for (const gradient of doseGradients(records)) {
      out.push({
        type: "scatter",
        mode: "lines",
        x: gradient.map((r) => levelOf(r) as number),
        y: gradient.map((r) => measure.valueOf(r) as number),
        line: {
          color: organismColor(gradient[0].organism, dark),
          width: 1,
          dash: "dot",
        },
        opacity: 0.55,
        hoverinfo: "skip",
        showlegend: false,
      });
    }

    for (const organism of organisms) {
      const points = records.filter((r) => r.organism === organism);
      out.push({
        type: "scatter",
        mode: "markers",
        name: organism,
        x: points.map((r) => levelOf(r) as number),
        y: points.map((r) => measure.valueOf(r) as number),
        text: points.map(hoverText),
        hovertemplate: "%{text}<extra></extra>",
        marker: {
          size: 10,
          color: organismColor(organism, dark),
          symbol: points.map((r) => assaySymbol(r.assay)),
          line: { width: 2, color: dark ? "#1a1a19" : "#fcfcfb" },
        },
      });
    }
    return out;
  }, [records, organisms, dark, measure]);

  useEffect(() => {
    const node = host.current;
    if (!node) return;

    const ink = dark ? "#c3c2b7" : "#52514e";
    const grid = dark ? "#262a24" : "#e4e8e2";
    const surface = dark ? "#1a1a19" : "#fcfcfb";

    const layout: Partial<Plotly.Layout> = {
      autosize: true,
      height: 460,
      margin: { l: 64, r: 18, t: 12, b: 56 },
      paper_bgcolor: surface,
      plot_bgcolor: surface,
      font: { family: "IBM Plex Sans, system-ui, sans-serif", size: 12, color: ink },
      hoverlabel: {
        bgcolor: surface,
        bordercolor: grid,
        font: { color: dark ? "#ffffff" : "#0b0b0b", size: 12 },
        align: "left",
      },
      xaxis: {
        title: {
          text: condition === "UV" ? "UV dose (J/m²)" : "temperature (°C)",
          font: { size: 12 },
        },
        type: condition === "UV" ? "log" : "linear",
        dtick: condition === "UV" ? 1 : undefined,
        gridcolor: grid,
        zeroline: false,
        linecolor: grid,
        ticks: "outside",
        tickcolor: grid,
      },
      yaxis: {
        title: { text: `${measure.label} (${measure.unit})`, font: { size: 12 } },
        type: yLog ? "log" : "linear",
        // SI prefixes read as nonsense on a percent axis ("100µ" for 1e-4).
        exponentformat: "power",
        gridcolor: grid,
        zeroline: false,
        linecolor: grid,
        ticks: "outside",
        tickcolor: grid,
      },
      legend: {
        orientation: "h",
        y: -0.19,
        x: 0,
        font: { size: 12 },
        itemsizing: "constant",
      },
      showlegend: organisms.length > 1,
    };

    Plotly.react(node, traces as Plotly.Data[], layout, {
      displayModeBar: true,
      modeBarButtonsToRemove: ["lasso2d", "select2d", "autoScale2d"],
      displaylogo: false,
      responsive: true,
    });
  }, [traces, condition, dark, organisms.length, measure, yLog]);

  useEffect(() => {
    const node = host.current;
    return () => {
      if (node) Plotly.purge(node);
    };
  }, []);

  if (records.length === 0) {
    return (
      <p className="empty">
        No records match these filters. Widen the range, add an organism, or
        allow more assay types.
      </p>
    );
  }

  return <div ref={host} className="plot" role="img" aria-label={
    `Dose–response scatter, ${records.length} records across ${organisms.length} organisms`
  } />;
}
