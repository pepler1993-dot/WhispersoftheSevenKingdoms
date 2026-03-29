# Audio v2 – A/B Test Matrix

## Purpose
Define the test matrix for evaluating sleep audio quality improvements introduced in Audio v2.

## Test Dimensions

### 1. Clip Duration
| Variant | Clip Length | Notes |
|---------|-----------|-------|
| A (baseline) | 30s | Previous default, safe for 4GB VRAM |
| B (new) | 47s | Max supported by Stable Audio Open |

**Hypothesis:** Longer clips produce smoother transitions and more coherent musical phrases, reducing listener disruption at stitch points.

### 2. Unique Material Duration
| Variant | Unique Material | Loop Target | Ratio |
|---------|----------------|-------------|-------|
| A (baseline) | ~3-20 min | 3h | 9-60× |
| B (new) | ~60 min | 3h | 3× |

**Hypothesis:** More unique material reduces listener fatigue from repetition, especially for multi-hour sleep sessions.

### 3. Post-Processing Preset
| Variant | Preset | Key Differences |
|---------|--------|----------------|
| A (baseline) | `ambient` | Bass boost, aggressive EQ, stronger reverb, -16 LUFS |
| B (new) | `sleep` | Gentle highpass, minimal EQ, light reverb, -18 LUFS, LRA 14 |

**Hypothesis:** Sleep preset reduces "mumpf" (low-end muddiness), creates more headroom, and avoids processing artifacts that can cause micro-arousals.

### 4. Clip-Role System
| Variant | Approach | Roles |
|---------|---------|-------|
| A (baseline) | All clips equal, same prompt modifier | N/A |
| B (new) | Role-based distribution | foundation (50%), texture (25%), breathing_space (15%), motif (10%) |

**Hypothesis:** Differentiated clip roles create natural dynamics with intentional breathing room, reducing monotony while avoiding jarring transitions.

### 5. Stitching Order
| Variant | Order | Method |
|---------|-------|--------|
| A (baseline) | Sequential (prompt order) | Clips stitched in generation order |
| B (new) | Similarity-sorted | Greedy nearest-neighbour by RMS loudness |

**Hypothesis:** Loudness-similar adjacent clips produce smoother crossfades and fewer jarring volume jumps.

### 6. Sleep-First Prompts
| Variant | Prompt Architecture | Components |
|---------|-------------------|-----------|
| A (baseline) | Raw variant prompts | Single prompt string |
| B (new) | base_dna + prompt + role_modifier + negative | Layered prompt assembly |

**Hypothesis:** Consistent base DNA across all clips of a house ensures tonal cohesion. Explicit negative prompts reduce unwanted elements (drums, vocals, etc.).

## Test Protocol

### Phase 1: Internal Review (1 week)
1. Generate one track per house using **both** A and B configurations
2. Blind-listen comparison by team (min 3 listeners)
3. Rate on: coherence, sleepiness, loop-detectability, overall quality
4. Score 1-10 per dimension

### Phase 2: Community A/B (2 weeks)
1. Upload both versions to YouTube (unlisted)
2. Share with test group (n≥20)
3. Collect: time-to-sleep (self-reported), wake-ups, preference
4. Use Google Form for structured feedback

### Phase 3: Public Release
1. Apply winning configuration to all houses
2. Generate full library with final settings
3. Monitor YouTube analytics: watch time, retention curves, comments

## Evaluation Criteria

| Criterion | Weight | Measurement |
|-----------|--------|-------------|
| Sleep onset time | 30% | Self-reported minutes to fall asleep |
| Night wakeups | 25% | Self-reported disruptions |
| Loop detectability | 20% | "Could you tell when it looped?" |
| Audio quality | 15% | Subjective quality rating 1-10 |
| Listener preference | 10% | A vs B preference |

## Success Metrics
- **Primary:** B variant reduces self-reported sleep onset by ≥15%
- **Secondary:** Loop detection rate drops below 20%
- **Guard rail:** Audio quality rating ≥7/10 (no regression)

## Houses for Initial Test
Priority order (by audience size):
1. Stark (Winterfell) – largest audience
2. Targaryen (Dragonstone) – second largest
3. Lannister (Casterly Rock) – diverse variants
4. The Wall – extreme dark ambient (edge case)

## Configuration Snapshots

### Baseline (A)
```json
{
  "clip_seconds": 30,
  "minutes": 20,
  "preset": "ambient",
  "clip_roles": false,
  "similarity_stitch": false,
  "base_dna": null,
  "negative_prompt": null
}
```

### Audio v2 (B)
```json
{
  "clip_seconds": 47,
  "unique_minutes": 60,
  "preset": "sleep",
  "clip_roles": true,
  "similarity_stitch": true,
  "base_dna": "<house-specific>",
  "negative_prompt": "<house-specific>"
}
```
