export const pointerToLongLat = (projection, transform, point) => {
  const longlat = projection.invert(transform.invert(point));

  return longlat;
};

export const distance = (px, py, mx, my) => {
  const a = px - mx;
  const b = py - my;

  return Math.sqrt(a * a + b * b);
};
