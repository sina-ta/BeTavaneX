export function extractNumericSeries(
  points: Array<Record<string, unknown> | object>,
  key: string
): number[] {
  return points
    .map((point) =>
      Number((point as Record<string, unknown>)[key])
    )
    .filter((value) => !Number.isNaN(value));
}

export function buildSparklinePath(
  values: number[],
  width = 240,
  height = 64
): string {
  if (values.length === 0) {
    return "";
  }

  if (values.length === 1) {
    const y = height / 2;
    return `M 0 ${y} L ${width} ${y}`;
  }

  const min = Math.min(...values);
  const max = Math.max(...values);
  const range = max - min || 1;

  return values
    .map((value, index) => {
      const x =
        (index / (values.length - 1)) * width;
      const y =
        height -
        ((value - min) / range) * (height - 8) -
        4;

      return `${index === 0 ? "M" : "L"} ${x} ${y}`;
    })
    .join(" ");
}
