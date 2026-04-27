# Global Parent-State Obligations

- status: `INCOMPLETE_OPEN_OBLIGATIONS`
- open obligations: `2`
- coverage status: `UNIVERSAL_ENTRY_COVERAGE_ONLY`

This report is universal only for entry into parent states. Transition closure remains a mathematical obligation until every open row is closed.

## Obligations

- `even_descent`: `CLOSED_BY_ANCESTOR_DESCENT` - C(n)=n/2<n for even n>2
- `odd_parent_state_cover`: `CLOSED_BY_TRANSITION_TO_CLOSED_STATE` - Every odd n can be written uniquely as n=2^a*r-1 with a>=1 and r odd.
- `parent_state_transition_templates`: `UNKNOWN` - Current parent-state transition report is finite in a and finite in r-depth.
- `parametric_a_templates`: `NEEDS_SPLIT` - 3^a periodicity is verified at fixed 2-adic depth, but transition templates still need exact lifting.
