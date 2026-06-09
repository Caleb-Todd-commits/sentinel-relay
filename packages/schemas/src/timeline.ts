import type { EvidenceId, ISODateTimeString, MessageId } from "./primitives";

export type TimelineEvent = {
  id: string;
  timestamp: ISODateTimeString;
  title: string;
  summary: string;
  evidenceIds: EvidenceId[];
  sourceMessageId?: MessageId;
  actorAgentId?: string;
  sortOrder?: number;
};
