export type MethodType = "clustering" | "association_rule" | "pca" | "time_series";
export type ClusteringAlgorithm = "kmeans" | "dbscan" | "hierarchical";
export type PCAMethodType = "SVD" | "covariance_matrix";
export type TimeSeriesMethodType = "linear_regression" | "arima";

export interface UploadResponseDTO {
  upload_id: string;
  filename: string;
  content_type: string;
  bytes: number;
  path: string;
  method_types?: string[] | null;
  metadata?: Record<string, unknown>;
  allowed_method_types?: MethodType[];
}

export interface MethodTypeResponseDTO {
  method_type: MethodType[];
}

export interface PreprocessingRunRequestDTO {
  upload_id: string;
  method_type: MethodType;
}

export interface PreprocessingRunResponseDTO {
  output_file_path: string;
}

export interface ClusteringRunRequestDTO {
  upload_id: string;
  algorithm: ClusteringAlgorithm;
}

export interface ClusteringRunResponseDTO {
  output_file_path: string;
  algorithm: ClusteringAlgorithm;
  n_clusters: number;
  noise_points?: number | null;
}

export interface BestClusteringRunRequestDTO {
  upload_id: string;
}

export interface ClusteringScoreDTO {
  algorithm: ClusteringAlgorithm;
  silhouette: number;
  n_clusters: number;
  noise_points?: number | null;
}

export interface BestClusteringRunResponseDTO {
  output_file_path: string;
  best_algorithm: ClusteringAlgorithm;
  results: ClusteringScoreDTO[];
}

export interface AssociationRunRequestDTO {
  upload_id: string;
  min_support: number;
  min_confidence: number;
  min_lift: number;
}

export interface AssociationRunResponseDTO {
  frequent_itemsets_file_path: string;
  association_rules_file_path: string;
}

export interface PCARunRequestDTO {
  upload_id: string;
  n_components?: number;
  threshold?: number;
}

export interface PCARunResponseDTO {
  transformed_data_file_path: string;
  explained_variance_ratio: number[];
  cumulative_variance: number[];
  pca_method_type: PCAMethodType;
}

export interface TimeSeriesRunRequestDTO {
  upload_id: string;
  method_type?: TimeSeriesMethodType;
}

export interface TimeSeriesRunResponseDTO {
  transformed_data_file_path: string;
  forecast_file_path: string;
  historical_plot_path: string;
  forecast_plot_path: string;
  target_column: string;
  datetime_column: string;
  metrics: Record<string, unknown>;
  time_series_method_type: TimeSeriesMethodType;
}

export interface DiagramImageDTO {
  filename: string;
  content_type: string;
  data_base64: string;
}

export interface DiagramsResponseDTO {
  upload_id: string;
  diagram_type: string;
  images: DiagramImageDTO[];
}

export interface AlgorithmReportInputDTO {
  name: string;
  measures?: Record<string, unknown> | null;
  params?: Record<string, unknown> | null;
  outputs?: Record<string, unknown> | null;
  notes?: string | null;
}

export interface ReportRequestDTO {
  upload_id: string;
  algorithms: AlgorithmReportInputDTO[];
}

export interface ReportResponseDTO {
  upload_id: string;
  report_text: string;
  schema: Record<string, unknown>;
}

export interface DatasetSession {
  uploadId: string;
  filename: string;
  bytes: number;
  contentType: string;
  uploadedAt: string;
  methodTypes: MethodType[];
  metadata?: Record<string, unknown>;
}

export interface AlgorithmResultRecord<T = unknown> {
  name: string;
  methodType: MethodType;
  params: Record<string, unknown>;
  output: T;
  diagrams?: DiagramsResponseDTO | null;
  createdAt: string;
}
