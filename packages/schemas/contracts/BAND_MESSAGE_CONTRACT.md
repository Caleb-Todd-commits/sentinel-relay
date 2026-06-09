# Band Message Contract

Every message sent through Band for Sentinel Relay should be wrapped in a `BandEnvelope` and contain an `AgentMessage` payload.

## Envelope

Required fields:

- `schemaVersion`
- `envelopeType`: always `sentinel_relay.agent_message`
- `caseId`
- `roomId`
- `senderAgentId`
- `messageId`
- `sentAt`
- `traceId`
- `payload`

## Payload

The `payload` must be an `AgentMessage`.

Required fields:

- `id`
- `schemaVersion`
- `caseId`
- `roomId`
- `sequence`
- `agentId`
- `agentName`
- `type`
- `title`
- `summary`
- `confidence`
- `severity`
- `evidenceIds`
- `createdAt`
- `visibility`

## Rule for judging

The demo should show the message `type`, `agentName`, `summary`, `evidenceIds`, `confidence`, `decisionImpact`, and `nextAction`. Those fields make Band's coordination visible.
