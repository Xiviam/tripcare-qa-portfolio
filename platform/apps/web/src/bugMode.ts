export const bugModeEnabled = import.meta.env.VITE_QA_BUG_MODE === "true";

export function isBugEnabled(id: string): boolean {
  return bugModeEnabled && /^BUG-0(1[0-5]|0[1-9])$/.test(id);
}
