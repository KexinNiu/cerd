import { useEffect, useState } from "react";

/** Tracks the OS color scheme so Plotly can be restyled to match the page. */
export function useDarkMode(): boolean {
  const [dark, setDark] = useState(
    () =>
      typeof matchMedia === "function" &&
      matchMedia("(prefers-color-scheme: dark)").matches,
  );

  useEffect(() => {
    const media = matchMedia("(prefers-color-scheme: dark)");
    const onChange = (e: MediaQueryListEvent) => setDark(e.matches);
    media.addEventListener("change", onChange);
    return () => media.removeEventListener("change", onChange);
  }, []);

  return dark;
}
