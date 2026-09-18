# Experiments directory

Each experiment is identified by date of design and/or submission and a brief identifier name.

## Experiments

### Initial exploratory experiments

- 2026-09-10-temporal-change-parasites
  - Initial exploratory experiment with host-parasite coevolution in temporally changing environment.
  - Flat task reward structure.
  - Health interaction mode
- 2026-09-17-temporal-change-mutualists
  - Initial exploratory experiment with host-parasite coevolution in temporally changing environment.
  - Differential task reward environment.
  - Health interaction mode
  - TAKEAWAYS:
    - Hosts fail to evolve complex tasks in all fluctuating environments.
    - Environment too challenging?
- 2026-09-17-temporal-change-evo-interaction
  - Initial exploratory experiment with host-endosymbiont coevolution where endosymbionts can evolve along the spectrum from mutualism to parasitism.
  - Differential task reward environment (produced the most interesting results from similar experiments for ALife 2026 paper).
  - Health interaction mode
- 2026-09-17-spatial-parasites
  - Initial exploratory experiment with host-parasite coevolution across different lattice configurations.
  - Flat task reward environment.
  - Health interaction mode
- 2026-09-17-spatial-mutualists
  - Initial exploratory experiment with host-mutualist coevolution across different lattice configurations.
  - Differential task reward environment.
  - Health interaction mode
- 2026-09-17-spatial-evo-interaction
  - Initial exploratory experiment with host-endosymbiont coevolution where endosymbionts can evolve along the spectrum from mutualism to parasitism.
  - Differential reward environment.
  - Health interaction mode

Changes based on initial experiments + summer student runs:

Temporally changing environment runs:

- Need longer environmental change intervals
- Allow for extinctions with host max age?
- Another strategy would be to setup environment in similar way to Avida

Spatially structured environment runs:

- Host-parasite coevolution:
  - More constraining spatial structures make it harder for parasites to track their hosts.
    - Parasites are less successful (thus complexity is reduced) in populations constrained more by their spatial structure. E.g., 1x10000 vs 100x100
- Host-mutualist coevolution:
  - More constraining spatial structures break down constraint.
  - A few hypotheses: weaker selection pressure on host-mutualist pairs, means it's potentially more likely that a host that doesn't match with its symbiont will survive. I.e., in well-mixed, it is more likely to get replaced by a functional pairing before it gets to reproduce. This might give the host time to get to more complex tasks.
    - Spatial constraint makes horizontal transmission less effective. So, mutualists also have fewer opportunities to find a host that matches with them, further decreasing evolutionary engagement.