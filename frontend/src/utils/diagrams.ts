import type { DiagramImageDTO } from "@/types/api";

export function imageToDataUri(image: DiagramImageDTO) {
  if (image.data_base64.startsWith("data:")) return image.data_base64;
  return `data:${image.content_type};base64,${image.data_base64}`;
}
