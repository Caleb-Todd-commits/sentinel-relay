"use client";

import { useMemo, useState } from "react";
import { deriveWorkflowViewModel } from "./deriveWorkflowState";

const APPROVAL_DECISION_STEP = 8;

export function useMockIncidentWorkflow(initialStep = 0) {
  const [stepIndex, setStepIndex] = useState(initialStep);
  const viewModel = useMemo(() => deriveWorkflowViewModel(stepIndex), [stepIndex]);

  function start() {
    setStepIndex(1);
  }

  function advance() {
    setStepIndex((current: number) => {
      const state = deriveWorkflowViewModel(current);
      if (!state.canAdvance) return current;
      return Math.min(current + 1, state.totalSteps);
    });
  }

  function approveContainment() {
    setStepIndex((current: number) => Math.max(current, APPROVAL_DECISION_STEP));
  }

  function replay() {
    setStepIndex(0);
  }

  function completeDemo() {
    setStepIndex(deriveWorkflowViewModel(stepIndex).totalSteps);
  }

  function jumpToStep(nextStepIndex: number) {
    const totalSteps = deriveWorkflowViewModel(stepIndex).totalSteps;
    setStepIndex(Math.max(0, Math.min(nextStepIndex, totalSteps)));
  }

  return {
    ...viewModel,
    actions: {
      start,
      advance,
      approveContainment,
      replay,
      completeDemo,
      jumpToStep,
    },
  };
}
