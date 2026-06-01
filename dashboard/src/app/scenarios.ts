export interface ScenarioDescriptor {
  key: string;
  label: string;
  description: string;
}

const STATE_ORDER = [
  'new',
  'active',
  'stalled',
  'conflictive',
  'convergent',
  'off_topic',
  'dominated',
  'shallow_discourse',
] as const;

const STATE_DESCRIPTIONS: Record<string, string> = {
  new: 'Thread just started and has not developed a discussion yet.',
  active: 'Healthy back-and-forth with current participation.',
  stalled: 'Discussion has slowed down or stopped progressing.',
  conflictive: 'Tone is escalating or becoming adversarial.',
  convergent: 'Participants are aligning toward a shared conclusion.',
  off_topic: 'The thread drifted away from the intended academic focus.',
  dominated: 'A small number of voices are crowding out the discussion.',
  shallow_discourse: 'Participation exists, but the exchange lacks depth.',
};

export function formatScenarioLabel(value: string): string {
  return value.replaceAll('_', ' ');
}

function compareScenarioKeys(left: string, right: string): number {
  const leftIndex = STATE_ORDER.indexOf(left as (typeof STATE_ORDER)[number]);
  const rightIndex = STATE_ORDER.indexOf(right as (typeof STATE_ORDER)[number]);

  if (leftIndex === -1 && rightIndex === -1) {
    return left.localeCompare(right);
  }

  if (leftIndex === -1) {
    return 1;
  }

  if (rightIndex === -1) {
    return -1;
  }

  return leftIndex - rightIndex;
}

export function getScenarioDescriptors(keys: string[]): ScenarioDescriptor[] {
  return Array.from(new Set(keys))
    .sort(compareScenarioKeys)
    .map((key) => ({
      key,
      label: formatScenarioLabel(key),
      description:
        STATE_DESCRIPTIONS[key] ?? 'Observed scenario in this evaluation run.',
    }));
}