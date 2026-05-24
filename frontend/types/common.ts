export interface Recommendation {
  title: string;
  action: string;
  severity?: string;
  factors?: string[];
  explanation?: string;
  rule_id?: string;
}

export type AsyncPageStatus =
  | "loading"
  | "success"
  | "empty"
  | "error";
