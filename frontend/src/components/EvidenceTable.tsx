import { useMemo, useState } from "react";
import type { CerdRecord } from "../types";
import { levelOf, sourceLabel, sourceUrl } from "../lib/filters";

type SortKey = "organism" | "strain" | "level" | "assay" | "response" | "evidence";

interface Props {
  records: CerdRecord[];
}

const COLUMNS: { key: SortKey; label: string; numeric?: boolean }[] = [
  { key: "organism", label: "Organism" },
  { key: "strain", label: "Strain" },
  { key: "level", label: "Level", numeric: true },
  { key: "assay", label: "Assay" },
  { key: "response", label: "Response", numeric: true },
  { key: "evidence", label: "Evidence" },
];

function valueFor(record: CerdRecord, key: SortKey): string | number {
  switch (key) {
    case "organism": return record.organism;
    case "strain": return record.strain ?? "";
    case "level": return levelOf(record) ?? Number.NEGATIVE_INFINITY;
    case "assay": return record.assay;
    case "response": return record.response_value ?? Number.NEGATIVE_INFINITY;
    case "evidence": return record.evidence_level;
  }
}

export function EvidenceTable({ records }: Props) {
  const [sortKey, setSortKey] = useState<SortKey>("level");
  const [ascending, setAscending] = useState(true);

  const sorted = useMemo(() => {
    const copy = [...records];
    copy.sort((a, b) => {
      const va = valueFor(a, sortKey);
      const vb = valueFor(b, sortKey);
      const cmp =
        typeof va === "number" && typeof vb === "number"
          ? va - vb
          : String(va).localeCompare(String(vb));
      return ascending ? cmp : -cmp;
    });
    return copy;
  }, [records, sortKey, ascending]);

  const onSort = (key: SortKey) => {
    if (key === sortKey) setAscending(!ascending);
    else {
      setSortKey(key);
      setAscending(true);
    }
  };

  return (
    <div className="table-scroll">
      <table>
        <thead>
          <tr>
            {COLUMNS.map((col) => (
              <th
                key={col.key}
                scope="col"
                className={col.numeric ? "num" : undefined}
                aria-sort={
                  sortKey === col.key
                    ? ascending ? "ascending" : "descending"
                    : "none"
                }
              >
                <button type="button" onClick={() => onSort(col.key)}>
                  {col.label}
                  {sortKey === col.key && <span aria-hidden="true">{ascending ? " ▲" : " ▼"}</span>}
                </button>
              </th>
            ))}
            <th scope="col">Source</th>
          </tr>
        </thead>
        <tbody>
          {sorted.map((r) => {
            const url = sourceUrl(r);
            const level = levelOf(r);
            return (
              <tr key={r.record_id}>
                <td className="sci">{r.organism}</td>
                <td>{r.strain ?? "—"}</td>
                <td className="num">
                  {level === null
                    ? "—"
                    : r.condition === "UV"
                      ? `${Math.round(level)} J/m²`
                      : `${level} °C`}
                </td>
                <td>{r.assay.replace(/_/g, " ")}</td>
                <td className="num">
                  {r.response_value ?? "—"} {r.response_unit ?? ""}
                </td>
                <td>{r.evidence_level}</td>
                <td>
                  {url
                    ? <a href={url} target="_blank" rel="noreferrer">{sourceLabel(r)}</a>
                    : sourceLabel(r)}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
