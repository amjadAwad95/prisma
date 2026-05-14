import type {
  AssociationRunRequestDTO,
  AssociationRunResponseDTO,
  BestClusteringRunRequestDTO,
  BestClusteringRunResponseDTO,
  ClusteringRunRequestDTO,
  ClusteringRunResponseDTO,
  DiagramsResponseDTO,
  MethodTypeResponseDTO,
  PCARunRequestDTO,
  PCARunResponseDTO,
  PreprocessingRunRequestDTO,
  PreprocessingRunResponseDTO,
  ReportRequestDTO,
  ReportResponseDTO,
  TimeSeriesRunRequestDTO,
  TimeSeriesRunResponseDTO,
  UploadResponseDTO
} from "@/types/api";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  status?: number;
  details?: unknown;

  constructor(message: string, status?: number, details?: unknown) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.details = details;
  }
}

async function parseResponse<T>(response: Response): Promise<T> {
  const contentType = response.headers.get("content-type") ?? "";
  const payload = contentType.includes("application/json") ? await response.json() : await response.text();

  if (!response.ok) {
    const message = typeof payload === "object" && payload && "detail" in payload
      ? JSON.stringify((payload as { detail: unknown }).detail)
      : `Request failed with status ${response.status}`;
    throw new ApiError(message, response.status, payload);
  }

  return payload as T;
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {})
    }
  });
  return parseResponse<T>(response);
}

export const api = {
  baseUrl: API_BASE_URL,

  uploadFile(file: File, onProgress?: (progress: number) => void) {
    return new Promise<UploadResponseDTO>((resolve, reject) => {
      const xhr = new XMLHttpRequest();
      const formData = new FormData();
      formData.append("file", file);

      xhr.open("POST", `${API_BASE_URL}/files/upload`);
      xhr.upload.onprogress = (event) => {
        if (event.lengthComputable && onProgress) {
          onProgress(Math.round((event.loaded / event.total) * 100));
        }
      };
      xhr.onload = () => {
        try {
          const body = JSON.parse(xhr.responseText || "{}");
          if (xhr.status >= 200 && xhr.status < 300) {
            resolve(body as UploadResponseDTO);
          } else {
            reject(new ApiError(body.detail ?? "Upload failed", xhr.status, body));
          }
        } catch (error) {
          reject(error);
        }
      };
      xhr.onerror = () => reject(new ApiError("Network error while uploading file"));
      xhr.send(formData);
    });
  },

  getMetadata(uploadId: string) {
    return request<UploadResponseDTO>(`/files/metadata/${uploadId}`);
  },

  listMetadata() {
    return request<UploadResponseDTO[]>("/files/metadata");
  },

  getAllowedMethods(uploadId: string) {
    return request<MethodTypeResponseDTO>(`/preprocessing/type/${uploadId}`);
  },

  runPreprocessing(input: PreprocessingRunRequestDTO) {
    return request<PreprocessingRunResponseDTO>("/preprocessing/run", {
      method: "POST",
      body: JSON.stringify(input)
    });
  },

  runClustering(input: ClusteringRunRequestDTO) {
    return request<ClusteringRunResponseDTO>("/clustering/run", {
      method: "POST",
      body: JSON.stringify(input)
    });
  },

  runBestClustering(input: BestClusteringRunRequestDTO) {
    return request<BestClusteringRunResponseDTO>("/clustering/best", {
      method: "POST",
      body: JSON.stringify(input)
    });
  },

  runPCA(input: PCARunRequestDTO) {
    return request<PCARunResponseDTO>("/pca/run", {
      method: "POST",
      body: JSON.stringify(input)
    });
  },

  runAssociation(input: AssociationRunRequestDTO) {
    return request<AssociationRunResponseDTO>("/association/run", {
      method: "POST",
      body: JSON.stringify(input)
    });
  },

  runTimeSeries(input: TimeSeriesRunRequestDTO) {
    return request<TimeSeriesRunResponseDTO>("/time-series/run", {
      method: "POST",
      body: JSON.stringify(input)
    });
  },

  getDiagrams(uploadId: string, diagramType: string) {
    return request<DiagramsResponseDTO>(`/files/diagrams/${uploadId}/${diagramType}`);
  },

  generateReport(input: ReportRequestDTO) {
    return request<ReportResponseDTO>("/reports/generate", {
      method: "POST",
      body: JSON.stringify(input)
    });
  }
};
