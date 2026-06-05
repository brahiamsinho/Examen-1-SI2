/** Filtra filas por texto en uno o más campos (case-insensitive). */
export function filterRowsByQuery<T>(
  rows: readonly T[],
  query: string,
  pickTexts: (row: T) => readonly (string | null | undefined)[],
): T[] {
  const q = query.trim().toLowerCase();
  if (!q) return [...rows];
  return rows.filter((row) =>
    pickTexts(row).some((text) => text?.toLowerCase().includes(q)),
  );
}
