export const previewRows = [
  { segment: "Enterprise", records: 1240, quality: 98, drift: 2.1 },
  { segment: "Mid-market", records: 980, quality: 94, drift: 3.8 },
  { segment: "SMB", records: 2140, quality: 91, drift: 5.6 },
  { segment: "Research", records: 740, quality: 96, drift: 1.9 }
];

export const trendData = [
  { name: "Jan", clustering: 31, association: 12, forecast: 7 },
  { name: "Feb", clustering: 42, association: 18, forecast: 12 },
  { name: "Mar", clustering: 58, association: 22, forecast: 18 },
  { name: "Apr", clustering: 77, association: 29, forecast: 26 },
  { name: "May", clustering: 92, association: 34, forecast: 39 },
  { name: "Jun", clustering: 116, association: 45, forecast: 54 }
];

export const forecastData = [
  { date: "Week 1", actual: 120, predicted: 118 },
  { date: "Week 2", actual: 132, predicted: 129 },
  { date: "Week 3", actual: 141, predicted: 142 },
  { date: "Week 4", actual: 152, predicted: 155 },
  { date: "Week 5", actual: 164, predicted: 167 },
  { date: "Week 6", actual: null, predicted: 179 },
  { date: "Week 7", actual: null, predicted: 188 }
];

export const associationRules = [
  { antecedent: "High Recency", consequent: "Premium Segment", confidence: 0.82, lift: 1.7 },
  { antecedent: "Large Basket", consequent: "Repeat Purchase", confidence: 0.76, lift: 1.44 },
  { antecedent: "Discount Used", consequent: "Churn Risk", confidence: 0.61, lift: 1.22 }
];
