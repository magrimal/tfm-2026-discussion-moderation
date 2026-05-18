import { ExperimentRun } from '../types';

export const mockExperimentRun: ExperimentRun = {
  run_id: 'run_2026-04-26',
  run_name: '2026-04-26 — all 10 local',
  timestamp: '2026-04-26T14:30:00Z',
  status: 'unstable',
  run_kind: 'evaluation',
  models: {
    'claude-opus-4-7': {
      model_name: 'claude-opus-4-7',
      family: 'Claude',
      size: 'Large',
      completion_count: 6,
      total_threads: 6,
      classification_correct: 6,
      intervention_correct: 4,
      avg_duration: 2340,
      error_count: 0,
      threads: {
        new: {
          thread_key: 'new',
          thread_title: 'Introduction to machine learning',
          expected_state: 'new',
          classification: {
            state: 'new',
            trajectory: 'forming',
            participation_balance: 'unbalanced',
            discourse_quality: 'exploratory',
            inquiry_phase: 'triggering',
            reasoning: 'Thread has just started with minimal participation. Only 2 posts present, both from the same user introducing a topic. No discussion has developed yet.',
            confidence: 0.95
          },
          intervention: {
            decision: 'no_intervention',
            reasoning: 'Thread is too new to assess trajectory. Allow natural development before intervening.',
            confidence: 0.88
          },
          duration_ms: 2100,
          logfuse_url: 'https://logfuse.io/runs/2026-04-26/claude-opus-4-7/thread_001'
        },
        active: {
          thread_key: 'active',
          thread_title: 'Neural network architectures',
          expected_state: 'active',
          classification: {
            state: 'active',
            trajectory: 'productive',
            participation_balance: 'balanced',
            discourse_quality: 'constructive',
            inquiry_phase: 'exploration',
            reasoning: 'Multiple participants actively exchanging ideas. Good back-and-forth with substantive contributions. Discussion is progressing naturally.',
            confidence: 0.92
          },
          intervention: {
            decision: 'no_intervention',
            reasoning: 'Discussion is healthy and productive. No facilitation needed.',
            confidence: 0.91
          },
          duration_ms: 2200
        },
        stalled: {
          thread_key: 'stalled',
          thread_title: 'Open source licensing',
          expected_state: 'stalled',
          classification: {
            state: 'stalled',
            trajectory: 'declining',
            participation_balance: 'unbalanced',
            discourse_quality: 'surface-level',
            inquiry_phase: 'resolution',
            reasoning: 'Discussion has slowed significantly. Last post was 3 days ago. Previous exchanges were brief and did not develop depth.',
            confidence: 0.89
          },
          intervention: {
            decision: 'intervene',
            role: 'provocateur',
            technique: 'challenging_question',
            post_to_thread: true,
            reasoning: 'Thread needs stimulus to reignite discussion. A provocative question about edge cases in licensing could revive engagement.',
            confidence: 0.82
          },
          role_reasoning: 'Provocateur role chosen to challenge assumptions and spark renewed debate on licensing complexities.',
          role_confidence: 0.85,
          response: {
            text: 'I notice the discussion has focused on GPL vs MIT, but what about the practical implications when your code becomes a dependency in a commercial SaaS product? How do you navigate the viral nature of copyleft licenses in that context?',
            reasoning: 'Question targets a real-world scenario that licensing discussions often overlook, designed to prompt deeper analysis.',
            confidence: 0.84
          },
          duration_ms: 2500,
          logfuse_url: 'https://logfuse.io/runs/2026-04-26/claude-opus-4-7/thread_003'
        },
        conflictive: {
          thread_key: 'conflictive',
          thread_title: 'Regulation of AI in the EU',
          expected_state: 'conflictive',
          classification: {
            state: 'conflictive',
            trajectory: 'diverging',
            participation_balance: 'polarized',
            discourse_quality: 'argumentative',
            inquiry_phase: 'exploration',
            reasoning: 'Sharp disagreement between participants with entrenched positions. Tone has become defensive. Participants are talking past each other rather than engaging with arguments.',
            confidence: 0.94
          },
          intervention: {
            decision: 'intervene',
            role: 'mediator',
            technique: 'reframing',
            post_to_thread: true,
            reasoning: 'Conflict is unproductive and escalating. Mediator intervention needed to redirect toward common ground and constructive dialogue.',
            confidence: 0.90
          },
          role_reasoning: 'Mediator role appropriate for de-escalating tension and refocusing on shared understanding.',
          role_confidence: 0.89,
          response: {
            text: 'I see strong perspectives on both sides here. Let me try to reframe: Both of you seem concerned about innovation—one worried regulation will stifle it, the other that lack of regulation will create harm that undermines public trust. Could we explore what minimal regulatory framework might protect both values?',
            reasoning: 'Acknowledges both positions, identifies shared concern, proposes constructive path forward.',
            confidence: 0.87
          },
          duration_ms: 2800,
          logfuse_url: 'https://logfuse.io/runs/2026-04-26/claude-opus-4-7/thread_004'
        },
        convergent: {
          thread_key: 'convergent',
          thread_title: 'Data preprocessing best practices',
          expected_state: 'convergent',
          classification: {
            state: 'convergent',
            trajectory: 'converging',
            participation_balance: 'balanced',
            discourse_quality: 'synthesizing',
            inquiry_phase: 'integration',
            reasoning: 'Participants are building on each other\'s ideas and reaching consensus. Multiple users have acknowledged points made by others and integrated them into their thinking.',
            confidence: 0.90
          },
          intervention: {
            decision: 'intervene',
            role: 'synthesizer',
            technique: 'summary',
            post_to_thread: false,
            reasoning: 'Group has made significant progress toward shared understanding. A synthesis would help consolidate learning, but posting publicly might disrupt natural conclusion.',
            confidence: 0.79
          },
          role_reasoning: 'Synthesizer role fits the convergent state—help crystallize the emerging consensus.',
          role_confidence: 0.81,
          response: {
            text: 'The group has converged on a solid framework: (1) handle missing values based on mechanism (MCAR/MAR/MNAR), (2) normalize features appropriate to algorithm choice, (3) preserve validation set preprocessing separately. This synthesizes the key insights from the discussion.',
            reasoning: 'Captures the three main points of consensus that emerged across multiple posts.',
            confidence: 0.80
          },
          duration_ms: 2400,
          logfuse_url: 'https://logfuse.io/runs/2026-04-26/claude-opus-4-7/thread_005'
        },
        off_topic: {
          thread_key: 'off_topic',
          thread_title: 'Weekend plans and course deadlines',
          expected_state: 'off_topic',
          classification: {
            state: 'off_topic',
            trajectory: 'diverging',
            participation_balance: 'balanced',
            discourse_quality: 'social',
            inquiry_phase: 'none',
            reasoning: 'Discussion has drifted entirely from academic content to personal social exchanges. No connection to course learning objectives.',
            confidence: 0.96
          },
          intervention: {
            decision: 'intervene',
            role: 'guide',
            technique: 'redirect',
            post_to_thread: true,
            reasoning: 'Thread has lost academic focus. Gentle redirect needed to bring discussion back to course content.',
            confidence: 0.86
          },
          role_reasoning: 'Guide role appropriate for gentle steering back toward learning objectives without being punitive.',
          role_confidence: 0.84,
          response: {
            text: 'I appreciate the group camaraderie! Since we\'re thinking about deadlines, this might be a good time to connect weekend planning with the upcoming project. Has anyone started exploring the dataset options?',
            reasoning: 'Acknowledges the social exchange positively while creating natural bridge back to academic work.',
            confidence: 0.83
          },
          duration_ms: 2200,
          logfuse_url: 'https://logfuse.io/runs/2026-04-26/claude-opus-4-7/thread_006'
        }
      }
    },
    'claude-sonnet-4-6': {
      model_name: 'claude-sonnet-4-6',
      family: 'Claude',
      size: 'Medium',
      completion_count: 6,
      total_threads: 6,
      classification_correct: 5,
      intervention_correct: 3,
      avg_duration: 1820,
      error_count: 0,
      threads: {
        new: {
          thread_key: 'new',
          thread_title: 'Introduction to machine learning',
          expected_state: 'new',
          classification: {
            state: 'new',
            trajectory: 'forming',
            participation_balance: 'unbalanced',
            discourse_quality: 'exploratory',
            inquiry_phase: 'triggering',
            reasoning: 'Very early stage thread with limited activity. Initial post introducing topic without developed discussion.',
            confidence: 0.91
          },
          intervention: {
            decision: 'no_intervention',
            reasoning: 'Too early to intervene. Thread needs time to develop organically.',
            confidence: 0.85
          },
          duration_ms: 1650,
          logfuse_url: 'https://logfuse.io/runs/2026-04-26/claude-sonnet-4-6/thread_001'
        },
        active: {
          thread_key: 'active',
          thread_title: 'Neural network architectures',
          expected_state: 'active',
          classification: {
            state: 'stalled',
            trajectory: 'productive',
            participation_balance: 'balanced',
            discourse_quality: 'constructive',
            inquiry_phase: 'exploration',
            reasoning: 'Good engagement but recent activity has slowed. Last meaningful post was 18 hours ago.',
            confidence: 0.74
          },
          intervention: {
            decision: 'no_intervention',
            reasoning: 'Discussion quality is still high. The slowdown may be natural pacing.',
            confidence: 0.80
          },
          duration_ms: 1900,
          logfuse_url: 'https://logfuse.io/runs/2026-04-26/claude-sonnet-4-6/thread_002'
        },
        stalled: {
          thread_key: 'stalled',
          thread_title: 'Open source licensing',
          expected_state: 'stalled',
          classification: {
            state: 'stalled',
            trajectory: 'declining',
            participation_balance: 'unbalanced',
            discourse_quality: 'surface-level',
            inquiry_phase: 'exploration',
            reasoning: 'Discussion has lost momentum with no recent activity. Previous posts lacked depth.',
            confidence: 0.87
          },
          intervention: {
            decision: 'intervene',
            role: 'guide',
            technique: 'probing_question',
            post_to_thread: true,
            reasoning: 'Thread needs facilitation to deepen engagement and restart conversation.',
            confidence: 0.78
          },
          role_reasoning: 'Guide role selected to ask probing questions that promote deeper thinking.',
          role_confidence: 0.76,
          response: {
            text: 'Let\'s dig deeper into this licensing question. Can someone share a specific scenario where you had to choose between licenses and what factors influenced your decision?',
            reasoning: 'Concrete scenario request encourages substantive contributions.',
            confidence: 0.77
          },
          duration_ms: 2100,
          logfuse_url: 'https://logfuse.io/runs/2026-04-26/claude-sonnet-4-6/thread_003'
        },
        conflictive: {
          thread_key: 'conflictive',
          thread_title: 'Regulation of AI in the EU',
          expected_state: 'conflictive',
          classification: {
            state: 'conflictive',
            trajectory: 'diverging',
            participation_balance: 'polarized',
            discourse_quality: 'argumentative',
            inquiry_phase: 'exploration',
            reasoning: 'Clear conflict with participants in opposition. Emotional language and defensive posturing present.',
            confidence: 0.90
          },
          intervention: {
            decision: 'intervene',
            role: 'mediator',
            technique: 'acknowledgment',
            post_to_thread: true,
            reasoning: 'Mediation needed to reduce tension and find productive path forward.',
            confidence: 0.84
          },
          role_reasoning: 'Mediator can help acknowledge different perspectives and reduce defensiveness.',
          role_confidence: 0.82,
          response: {
            text: 'Both perspectives raise important points about innovation and safety. What if we listed the specific harms each of you is trying to prevent? That might reveal common ground.',
            reasoning: 'Focuses on shared goal of harm prevention to bridge divide.',
            confidence: 0.81
          },
          duration_ms: 2300,
          logfuse_url: 'https://logfuse.io/runs/2026-04-26/claude-sonnet-4-6/thread_004'
        },
        convergent: {
          thread_key: 'convergent',
          thread_title: 'Data preprocessing best practices',
          expected_state: 'convergent',
          classification: {
            state: 'convergent',
            trajectory: 'converging',
            participation_balance: 'balanced',
            discourse_quality: 'synthesizing',
            inquiry_phase: 'integration',
            reasoning: 'Strong agreement developing among participants. Ideas being built upon and integrated.',
            confidence: 0.88
          },
          intervention: {
            decision: 'no_intervention',
            reasoning: 'Discussion is progressing well toward consensus. No facilitation needed.',
            confidence: 0.83
          },
          duration_ms: 1700,
          logfuse_url: 'https://logfuse.io/runs/2026-04-26/claude-sonnet-4-6/thread_005'
        },
        off_topic: {
          thread_key: 'off_topic',
          thread_title: 'Weekend plans and course deadlines',
          expected_state: 'off_topic',
          classification: {
            state: 'off_topic',
            trajectory: 'diverging',
            participation_balance: 'balanced',
            discourse_quality: 'social',
            inquiry_phase: 'none',
            reasoning: 'Content is entirely social with no academic value. Participants discussing personal matters.',
            confidence: 0.93
          },
          intervention: {
            decision: 'intervene',
            role: 'guide',
            technique: 'redirect',
            post_to_thread: true,
            reasoning: 'Need to steer conversation back to academic topics.',
            confidence: 0.81
          },
          role_reasoning: 'Guide role fits the need for gentle redirection.',
          role_confidence: 0.79,
          response: {
            text: 'Great to see everyone connecting! When you have a moment, I\'d love to hear your thoughts on the preprocessing techniques we\'ve been discussing in class.',
            reasoning: 'Friendly acknowledgment followed by redirect to course content.',
            confidence: 0.78
          },
          duration_ms: 1850,
          logfuse_url: 'https://logfuse.io/runs/2026-04-26/claude-sonnet-4-6/thread_006'
        }
      }
    },
    'gpt-4-turbo': {
      model_name: 'gpt-4-turbo',
      family: 'GPT-4',
      size: 'Large',
      completion_count: 5,
      total_threads: 6,
      classification_correct: 4,
      intervention_correct: 2,
      avg_duration: 1950,
      error_count: 1,
      threads: {
        new: {
          thread_key: 'new',
          thread_title: 'Introduction to machine learning',
          expected_state: 'new',
          classification: {
            state: 'new',
            trajectory: 'forming',
            participation_balance: 'unbalanced',
            discourse_quality: 'exploratory',
            inquiry_phase: 'triggering',
            reasoning: 'Thread is in early stages with minimal participation.',
            confidence: 0.89
          },
          intervention: {
            decision: 'no_intervention',
            reasoning: 'Allow thread to develop naturally before assessing need for intervention.',
            confidence: 0.82
          },
          duration_ms: 1800,
          logfuse_url: 'https://logfuse.io/runs/2026-04-26/gpt-4-turbo/thread_001'
        },
        active: {
          thread_key: 'active',
          thread_title: 'Neural network architectures',
          expected_state: 'active',
          classification: {
            state: 'active',
            trajectory: 'productive',
            participation_balance: 'balanced',
            discourse_quality: 'constructive',
            inquiry_phase: 'exploration',
            reasoning: 'Healthy discussion with multiple engaged participants exchanging substantive ideas.',
            confidence: 0.86
          },
          intervention: {
            decision: 'intervene',
            role: 'expert',
            technique: 'clarification',
            post_to_thread: true,
            reasoning: 'Some technical misconceptions present that could be addressed.',
            confidence: 0.71
          },
          role_reasoning: 'Expert role can provide technical clarification.',
          role_confidence: 0.73,
          response: {
            text: 'Just to clarify on the backpropagation discussion—the vanishing gradient problem affects deep networks primarily with sigmoid/tanh activations, which is why ReLU became popular.',
            reasoning: 'Corrects technical misunderstanding mentioned in thread.',
            confidence: 0.72
          },
          duration_ms: 2200,
          logfuse_url: 'https://logfuse.io/runs/2026-04-26/gpt-4-turbo/thread_002'
        },
        stalled: {
          thread_key: 'stalled',
          thread_title: 'Open source licensing',
          expected_state: 'stalled',
          classification: {
            state: 'active',
            trajectory: 'forming',
            participation_balance: 'balanced',
            discourse_quality: 'exploratory',
            inquiry_phase: 'exploration',
            reasoning: 'Discussion shows engagement across participants with exploratory questions being asked.',
            confidence: 0.68
          },
          intervention: {
            decision: 'no_intervention',
            reasoning: 'Thread appears healthy and developing naturally.',
            confidence: 0.75
          },
          duration_ms: 1750,
          logfuse_url: 'https://logfuse.io/runs/2026-04-26/gpt-4-turbo/thread_003'
        },
        conflictive: {
          thread_key: 'conflictive',
          thread_title: 'Regulation of AI in the EU',
          expected_state: 'conflictive',
          classification: {
            state: 'conflictive',
            trajectory: 'diverging',
            participation_balance: 'polarized',
            discourse_quality: 'argumentative',
            inquiry_phase: 'exploration',
            reasoning: 'Clear disagreement with participants taking opposing stances. Discussion has become heated.',
            confidence: 0.92
          },
          intervention: {
            decision: 'intervene',
            role: 'mediator',
            technique: 'perspective_taking',
            post_to_thread: true,
            reasoning: 'Conflict requires mediation to prevent further escalation.',
            confidence: 0.87
          },
          role_reasoning: 'Mediator role needed to facilitate mutual understanding.',
          role_confidence: 0.85,
          response: {
            text: 'I\'m noticing strong views on both sides. Could each of you articulate what you see as the strongest point in the other\'s argument?',
            reasoning: 'Perspective-taking exercise to promote empathy and reduce polarization.',
            confidence: 0.83
          },
          duration_ms: 2400,
          logfuse_url: 'https://logfuse.io/runs/2026-04-26/gpt-4-turbo/thread_004'
        },
        convergent: {
          thread_key: 'convergent',
          thread_title: 'Data preprocessing best practices',
          expected_state: 'convergent',
          classification: {
            state: 'convergent',
            trajectory: 'converging',
            participation_balance: 'balanced',
            discourse_quality: 'synthesizing',
            inquiry_phase: 'integration',
            reasoning: 'Participants building consensus and integrating ideas effectively.',
            confidence: 0.84
          },
          intervention: {
            decision: 'no_intervention',
            reasoning: 'Discussion is productively converging without need for facilitation.',
            confidence: 0.80
          },
          duration_ms: 1850,
          logfuse_url: 'https://logfuse.io/runs/2026-04-26/gpt-4-turbo/thread_005'
        },
        off_topic: {
          thread_key: 'off_topic',
          thread_title: 'Weekend plans and course deadlines',
          expected_state: 'off_topic',
          error: 'APIError: Rate limit exceeded',
          duration_ms: 0,
          logfuse_url: 'https://logfuse.io/runs/2026-04-26/gpt-4-turbo/thread_006'
        }
      }
    }
  }
};

export const mockHistoricalRuns: ExperimentRun[] = [
  mockExperimentRun,
  {
    ...mockExperimentRun,
    run_id: 'run_2026-05-03',
    run_name: '2026-05-03 — local tool output',
    timestamp: '2026-05-03T18:13:00Z',
    status: 'failed',
  },
  {
    ...mockExperimentRun,
    run_id: 'run_2026-05-05',
    run_name: '2026-05-05 — baseline smoke run',
    timestamp: '2026-05-05T09:20:00Z',
    status: 'passed',
  },
  {
    ...mockExperimentRun,
    run_id: 'run_2026-05-05_live',
    run_name: '2026-05-05 — active verification',
    timestamp: '2026-05-05T11:42:00Z',
    status: 'running',
  },
];

export const threadScenarios = [
  { key: 'new', title: 'Introduction to machine learning' },
  { key: 'active', title: 'Neural network architectures' },
  { key: 'stalled', title: 'Open source licensing' },
  { key: 'conflictive', title: 'Regulation of AI in the EU' },
  { key: 'convergent', title: 'Data preprocessing best practices' },
  { key: 'off_topic', title: 'Weekend plans and course deadlines' }
];
