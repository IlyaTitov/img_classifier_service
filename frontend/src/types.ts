export type Detection = {
  id: number;
  label: string;
  confidence: number;
  x_min: number;
  y_min: number;
  x_max: number;
  y_max: number;
};

export type ImageDetail = {
  id: number;
  name: string;
  created_at: string | null;
  processing_complete: boolean;
  processed_filename: string | null;
  original_filename: string;
  detections: Detection[];
};

export type ArchiveItem = {
  id: number;
  name: string;
  created_at: string | null;
  processing_complete: boolean;
  processed_filename: string | null;
  original_filename: string;
  detection_count: number;
  file_size: number;
};

export type TokenResponse = {
  access_token: string;
  token_type: string;
};

export type SortBy = "created_at" | "detection_count";
export type SortOrder = "asc" | "desc";
