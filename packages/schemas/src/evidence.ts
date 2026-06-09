import type { EvidenceKind, EvidenceSensitivity } from "./enums";
import type { ConfidenceScore, EvidenceId, ISODateTimeString } from "./primitives";

export type EvidenceReference = {
  id: EvidenceId;
  kind: EvidenceKind;
  source: string;
  title: string;
  summary: string;
  location?: string;
  excerpt?: string;
  confidence: ConfidenceScore;
  sensitivity: EvidenceSensitivity;
  collectedAt?: ISODateTimeString;
  collectedByAgentId?: string;
  hash?: string;
  limitations?: string[];
};

export type EvidenceBundle = {
  caseId: string;
  evidence: EvidenceReference[];
};
