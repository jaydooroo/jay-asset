export const parseCommaTickers = (rawValue) =>
  String(rawValue ?? '')
    .split(',')
    .map((value) => value.trim().toUpperCase())
    .filter(Boolean);

export const parseNumber = (rawValue) => {
  const num = Number.parseFloat(rawValue);
  return Number.isNaN(num) ? null : num;
};

