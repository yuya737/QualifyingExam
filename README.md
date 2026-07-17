# Yuya's Qualifying Exam

**Supporting Analysis of Multifaceted Geospatial Data with Visual Analytics**

PhD Qualifying Exam dissertation proposal, UC Davis. The proposal advances visual
analytics as a tool for analyzing complex geospatial data across three facets of
complexity: (1) multivariate structure, (2) ensemble variability, and
(3) multimodality and predictive modeling.

## Chapters

- **HexTiles** (multivariate structure) — a domain-agnostic hexagonal-tiling
  encoding that combines semantic icons with hexagonal tessellation to render many
  variables and their interactions on a single map while preserving its spatial
  schema. Confronts the Modifiable Areal Unit Problem by surfacing within-tile
  variability through confidence encodings. Evaluated on California water management
  and Texas presidential-election data with a controlled user study and expert review.
- **ClimateSOM** (ensemble variability) — a visual analysis workflow that abstracts a
  spatiotemporal climate ensemble into a distribution over a self-organizing map,
  integrating large language models for bidirectional querying. Extended with an
  Earth Mover's Distance permutation test and a clustering-based decomposition to make
  claims about distributional shifts statistically grounded rather than merely apparent.
- **DELUGE** (multimodality and predictive modeling) — a multimodal model for daily,
  ~1 km insured pluvial flood-damage prediction across the highest-claim regions of
  CONUS. Routes AlphaEarth foundation-model embeddings and terrain descriptors through
  physics-shaped Value and Temporal Modulators, yielding interpretability by design.

## Ongoing and Future Research Plans

- A larger and more diverse user study to consolidate the HexTiles evaluation.
- A visual analytics system built on DELUGE for inspecting *why* a damage prediction
  is made and posing counterfactual what-if queries.
- A visual analytics system for understanding how trained models use the embeddings
  they draw from geospatial foundation models, grounding a model's reliance in
  human-understandable spatial concepts and surfacing the predictive structure it uses
  that no known concept explains.
- Completing the ClimateSOM extension and developing a workflow for the spatial
  co-occurrence of extreme climate events under a changing climate.

## Building

The main document is `kawakami_qe.tex`, with chapters under `tex/`. Build with:

```
make paper
```

This runs `pdflatex`, `bibtex`, and two more `pdflatex` passes to resolve
references. Use `make clean` to remove build artifacts.
