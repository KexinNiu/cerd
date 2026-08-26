import type { CerdRecord } from "../types";
import { ORGANISM_GROUPS, organismColor } from "../lib/palette";
import { useDarkMode } from "../lib/useDarkMode";

interface Props {
  available: string[];
  selected: string[];
  onChange: (organisms: string[]) => void;
  records: CerdRecord[];
}

export function OrganismPanel({ available, selected, onChange, records }: Props) {
  const dark = useDarkMode();

  const toggle = (organism: string) => {
    onChange(
      selected.includes(organism)
        ? selected.filter((o) => o !== organism)
        : [...selected, organism],
    );
  };

  const countFor = (organism: string) =>
    records.filter((r) => r.organism === organism).length;

  return (
    <section className="panel" aria-labelledby="organism-heading">
      <h2 id="organism-heading" className="panel-title">Organisms</h2>
      <div className="panel-body">
        {ORGANISM_GROUPS.map((group) => {
          const present = group.organisms.filter((o) => available.includes(o));
          if (present.length === 0) return null;
          return (
            <fieldset key={group.label} className="group">
              <legend>{group.label}</legend>
              {present.map((organism) => (
                <label key={organism} className="check">
                  <input
                    type="checkbox"
                    checked={selected.includes(organism)}
                    onChange={() => toggle(organism)}
                  />
                  <span
                    className="dot"
                    style={{ background: organismColor(organism, dark) }}
                    aria-hidden="true"
                  />
                  <i className="sci">{organism}</i>
                  <span className="count">{countFor(organism)}</span>
                </label>
              ))}
            </fieldset>
          );
        })}
      </div>
      <div className="panel-foot">
        <button type="button" onClick={() => onChange(available)}>All</button>
        <button type="button" onClick={() => onChange([])}>None</button>
      </div>
    </section>
  );
}
