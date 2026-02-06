@domain_definitions @phase0
Feature: Domain Definition Agents coexist under the same domain path
  The system encourages multiple competing definitions for the same concept.
  Definitions are pruned and ranked by third-party assessments, not by ownership of the name.

  Background:
    Given canonicalization rules for Definition Cards exist
    And content IDs (CIDs) are computed from canonical bytes
    And a Registry service exists
    And a Forwarder service exists
    And a Coordination Agent exists
    And an Evidence Agent exists
    And an Assessment Agent exists
    And a Merit Ledger Agent exists

  @phase0 @publish
  Scenario: Publish a new Domain Definition Agent under an existing domain path
    Given domain path "/science" exists as a topic label
    And a creator "Alice" with a key pair exists
    When "Alice" publishes a Domain Definition Agent for "/science" with:
      | field                 |
      | definition_text       |
      | scope_in              |
      | scope_out             |
      | canonical_examples    |
      | counterexamples       |
      | harness_template_id   |
      | version_label         |
    Then a "definition_id" CID is produced
    And the Domain Definition Agent state is cryptographically signed by "Alice"
    And the Registry emits REGISTER for the Domain Definition Agent state
    And the Coordination Agent registers the definition under domain path "/science"
    And other agents can discover this definition by querying "/science"

  @phase0 @coexistence
  Scenario: Multiple Domain Definition Agents can coexist under the same domain path
    Given "Alice" published a Domain Definition Agent for "/science" as definition "DEF_A"
    And "Bob" published a Domain Definition Agent for "/science" as definition "DEF_B"
    When a requestor discovers definitions under "/science"
    Then the result includes "DEF_A"
    And the result includes "DEF_B"
    And the system does not require global uniqueness of "/science"

  @phase0 @discover
  Scenario: Discover definitions with minimal metadata for ranking and audit
    Given the Coordination Agent has registered definitions for "/science":
      | definition_id | owner | version | created_at |
      | DEF_A         | Alice | v1      | T1         |
      | DEF_B         | Bob   | v1      | T2         |
    When a requestor queries "/science" for definitions
    Then the response includes for each definition:
      | field                 |
      | definition_id         |
      | current_head_state    |
      | owner_id              |
      | version_label         |
      | harness_template_id   |
      | merit_score_snapshot  |
      | review_count_snapshot |

  @phase0 @resolve
  Scenario: Resolve a definition to its latest valid state
    Given definition "DEF_A" has head state "S1"
    When a requestor resolves definition "DEF_A"
    Then the Forwarder returns state "S1"

  @phase0 @versioning
  Scenario: Update a definition by publishing a new version that references the previous state
    Given "Alice" published definition "DEF_A" with head state "S1"
    When "Alice" publishes an updated definition state "S2" referencing previous "S1"
    Then the Registry emits REGISTER for "S2"
    And the Registry emits FORWARD from "S1" to "S2"
    And the Forwarder sets head for definition "DEF_A" to "S2"
    And the prior state "S1" remains immutable and resolvable

  @phase1 @diff_required
  Scenario: Semantic changes require an explicit diff artifact
    Given "Alice" published definition "DEF_A" with head state "S1"
    When "Alice" publishes an updated definition state "S2" referencing previous "S1"
    And the updated definition_text is meaningfully different from "S1"
    Then the updated state "S2" must include a "diff_artifact_cid"
    And the diff artifact describes at least:
      | field             |
      | changed_sections  |
      | rationale         |
      | expected_impacts  |
    And otherwise the update is rejected with reason "MISSING_SEMANTIC_DIFF"

  @phase0 @harness_template
  Scenario: A definition includes a harness template for evaluation
    Given a harness template "HARNESS_BASIC_CLASSIFY_V1" exists
    When a creator publishes a definition for "/science" with harness_template_id "HARNESS_BASIC_CLASSIFY_V1"
    Then the published Definition Card includes harness_template_id "HARNESS_BASIC_CLASSIFY_V1"
    And reviewers can request the harness for that definition

  @phase1 @fork_relationships
  Scenario Outline: A definition can declare relationships to other definitions
    Given "Bob" published definition "DEF_B" for "/science"
    When "Charlie" publishes definition "DEF_C" for "/science" declaring relationship "<rel>" to "DEF_B"
    Then "DEF_C" stores a relationship edge "<rel>" -> "DEF_B"
    And the relationship edge is queryable from "DEF_C"

    Examples:
      | rel          |
      | inspired_by  |
      | contradicts  |
      | refines      |

  @phase1 @name_squatting_protection
  Scenario: No one can block competing definitions by owning the domain path
    Given "Alice" published definition "DEF_A" for "/science"
    When "Bob" attempts to publish another definition "DEF_B" for "/science"
    Then the system accepts "DEF_B"
    And the Coordination Agent lists both definitions under "/science"
    And any ranking uses merit and assessments rather than publish order or ownership


@domain_reviews @phase0
Feature: Review and assessment prune the definitional landscape
  Independent agent assessments determine which definitions are trusted in practice.

  Background:
    Given canonicalization rules for Review Entries exist
    And content IDs (CIDs) are computed from canonical bytes
    And an Evidence Agent exists
    And an Assessment Agent exists
    And a Merit Ledger Agent exists
    And signatures are optional in Phase 0 and expected by Phase 2

  @phase0 @review_submit
  Scenario: A reviewer submits a harness run as evidence for a definition
    Given definition "DEF_A" exists under "/science"
    And reviewer agent "Reviewer1" exists
    And the harness for "DEF_A" requires 10 classification items
    When "Reviewer1" runs the harness for "DEF_A" and submits results:
      | field                  |
      | test_items             |
      | reviewer_outputs       |
      | expected_by_definition |
      | notes                  |
    Then the system stores a Review Evidence Entry with a "review_evidence_cid"
    And the Evidence Agent links the entry to "DEF_A"
    And the entry includes reviewer id "Reviewer1"
    And the entry is content-addressed and immutable

  @phase0 @review_assess
  Scenario: The Assessment Agent evaluates a review and records a verdict
    Given review evidence "REV_E1" exists for definition "DEF_A"
    And reviewer "Reviewer1" has submitted complete harness results
    When the Assessment Agent evaluates "REV_E1"
    Then the Assessment Agent records verdict "accepted" or "rejected"
    And the assessment includes reasoning and referenced evidence_cids
    And the assessment is linked to both "DEF_A" and "Reviewer1"

  @phase1 @challenge_boundary_case
  Scenario: Any agent can challenge a definition with a boundary case
    Given definition "DEF_A" exists under "/science"
    And challenger agent "Challenger1" exists
    When "Challenger1" submits a boundary-case challenge for "DEF_A" with:
      | field             |
      | boundary_item     |
      | claimed_label     |
      | argument_text     |
      | optional_evidence |
    Then a Challenge Record is created with "challenge_cid"
    And the system starts an assessment window "W"
    And the definition owner is notified of the challenge

  @phase1 @challenge_response
  Scenario: The definition owner responds to a challenge within the assessment window
    Given challenge "CHAL_1" exists for definition "DEF_A"
    And the assessment window for "CHAL_1" is open
    When the owner of "DEF_A" submits a response:
      | field                 |
      | owner_label           |
      | justification_text    |
      | optional_patch_plan   |
      | optional_diff_cid     |
    Then the response is stored as evidence linked to "CHAL_1"
    And the response is visible to assessors for evaluation

  @phase1 @challenge_timeout
  Scenario: A challenge times out if the owner does not respond
    Given challenge "CHAL_1" exists for definition "DEF_A"
    And the assessment window for "CHAL_1" has expired
    And no owner response exists for "CHAL_1"
    When the Assessment Agent evaluates "CHAL_1"
    Then the Assessment Agent records verdict "owner_no_response"
    And the verdict is included in the merit update inputs for "DEF_A"

  @phase2 @weighted_assessments
  Scenario: Assessments are weighted by assessor merit in the relevant domain
    Given assessor "AssessorA" has merit 0.9 in "/science"
    And assessor "AssessorB" has merit 0.2 in "/science"
    And both assess the same challenge for definition "DEF_A"
    When the Merit Ledger Agent computes a merit update for "DEF_A"
    Then the update weights "AssessorA" more than "AssessorB"
    And the weighting rule is published and versioned

  @phase2 @anti_gaming_review_cap
  Scenario: Anti-gaming policy limits merit impact from correlated reviewers
    Given definition "DEF_A" has 20 reviews
    And 15 of them are from a correlated cluster "CLUSTER_X"
    When the Merit Ledger Agent aggregates review impact for "DEF_A"
    Then the marginal impact of additional reviews from "CLUSTER_X" is reduced
    And the system records a signal "CORRELATED_REVIEWERS_DETECTED"

  @phase2 @update_merit_def
  Scenario Outline: Merit updates for definitions reflect outcomes of challenges and harness acceptance
    Given definition "<def_id>" exists under "/science"
    And there are accepted reviews count "<accepted>"
    And there are rejected reviews count "<rejected>"
    And there are challenge outcomes:
      | outcome            | count |
      | upheld_definition  | <up>  |
      | overturned         | <ov>  |
      | owner_no_response  | <nr>  |
    When the Merit Ledger Agent updates merit for "<def_id>"
    Then the merit score changes in the direction consistent with:
      | rule                                     |
      | accepted reviews increase merit          |
      | rejected reviews decrease merit          |
      | overturned challenges decrease merit     |
      | owner_no_response decreases merit more   |

    Examples:
      | def_id | accepted | rejected | up | ov | nr |
      | DEF_A  | 10       | 2        | 3  | 1  | 0  |
      | DEF_B  | 2        | 8        | 0  | 3  | 2  |

  @phase2 @update_merit_reviewers
  Scenario: Reviewers gain or lose merit based on later meta-review outcomes
    Given reviewer "Reviewer1" submitted review evidence "REV_E1" for "DEF_A"
    And "REV_E1" was accepted by an assessor
    And later meta-review overturns that acceptance as "incorrect"
    When the Merit Ledger Agent updates merit for "Reviewer1" in "/science/review"
    Then "Reviewer1" merit decreases
    And the reason references the meta-review assessment CID

  @phase3 @meta_review_sampling
  Scenario: A MetaReview process randomly samples accepted assessments for audit
    Given a MetaReviewFacilitatorAgent exists
    And there are 100 finalized assessments in "/science"
    When the MetaReviewFacilitatorAgent samples 5% for audit
    Then 5 assessments are selected
    And an independent committee is formed from high-merit assessors
    And a meta-review verdict is recorded for each sampled assessment


@domain_ranking @phase1
Feature: Rankings are derived from merit and evidence, not engagement
  The UI may show popularity, but protocol trust uses merit + track record.

  Background:
    Given a Coordination Agent exists
    And a Merit Ledger Agent exists

  @phase1 @rank_list
  Scenario: List definitions under a domain path sorted by merit score
    Given "/science" has definitions:
      | definition_id | merit_score |
      | DEF_A         | 0.72       |
      | DEF_B         | 0.31       |
      | DEF_C         | 0.85       |
    When a requestor lists definitions under "/science" with sort "merit_desc"
    Then the returned order is "DEF_C", "DEF_A", "DEF_B"

  @phase1 @separate_reach
  Scenario: Reach is displayed separately and does not change merit
    Given definition "DEF_A" has reach_score 1000 and merit_score 0.40
    And definition "DEF_B" has reach_score 10 and merit_score 0.70
    When a requestor lists definitions under "/science"
    Then the UI may show reach_score and merit_score
    And protocol ranking by default uses merit_score not reach_score

  @phase2 @default_resolution_policy
  Scenario: Consumers can choose a resolution policy for "which definition to use"
    Given a consumer agent "Consumer1" needs a working definition under "/science"
    When "Consumer1" requests a definition using policy "highest_merit"
    Then the system returns the current highest merit definition under "/science"
    When "Consumer1" requests a definition using policy "pinned_definition_id" with "DEF_B"
    Then the system returns "DEF_B"
    And the policy choice is recorded in "Consumer1" configuration


@ui_domain_definitions @phase0
Feature: UI enables non-technical users to create competing definitions
  The UI is a mediated interface to publish Definition Agents and participate in review/challenge flows.

  Background:
    Given a Web UI Agent exists
    And a UserSuccessOnboardingAgent exists
    And a Coordination Agent exists
    And a Commitment Agent exists
    And an Evidence Agent exists
    And an Assessment Agent exists
    And a Merit Ledger Agent exists

  @phase0 @onboarding
  Scenario: Onboarding explains definitions, reviews, challenges, and merit
    Given a new user "User1" has no prior participation
    When "User1" opens the onboarding flow
    Then the UI explains:
      | topic                          |
      | definitions as competing claims|
      | merit vs popularity            |
      | reviews as harness runs        |
      | challenges as boundary disputes|
      | versioning and diffs           |
    And the UI offers a "Create Definition" path and a "Review Definitions" path

  @phase0 @create_definition_wizard
  Scenario: Create Definition Wizard publishes a Domain Definition Agent
    Given "User1" is authenticated in the UI
    When "User1" starts "Create Definition"
    And selects domain path "/science"
    And enters definition_text "Science is..."
    And enters scope_in "..."
    And enters scope_out "..."
    And adds canonical examples:
      | example |
      | E1      |
      | E2      |
    And adds counterexamples:
      | counterexample |
      | C1             |
      | C2             |
    And selects harness template "HARNESS_BASIC_CLASSIFY_V1"
    And sets version_label "v1"
    And clicks "Publish"
    Then the UI shows a confirmation with "definition_id"
    And the definition appears in the UI list under "/science"
    And the UI shows the initial merit score as "unranked" or default

  @phase0 @browse_definitions
  Scenario: Browse a domain path shows multiple definitions and their metrics
    Given "/science" has definitions "DEF_A" and "DEF_B"
    When a user navigates to "/science"
    Then the UI displays both definitions
    And each definition card displays:
      | field                |
      | definition_summary   |
      | owner                |
      | version_label        |
      | merit_score          |
      | review_count         |
      | challenge_count      |
      | harness_template_id  |
    And the UI allows filtering by "highest_merit", "most_reviewed", and "newest"

  @phase0 @view_definition_detail
  Scenario: Definition detail page shows harness and evidence trail
    Given definition "DEF_A" exists under "/science"
    When a user opens the definition detail page for "DEF_A"
    Then the UI displays:
      | section             |
      | full_definition     |
      | scope_in_out        |
      | examples            |
      | counterexamples     |
      | harness_preview     |
      | version_history     |
      | evidence_and_reviews|
      | open_challenges     |

  @phase0 @review_flow
  Scenario: Review flow guides a user through running a harness and submitting results
    Given user "User2" is authenticated in the UI
    And definition "DEF_A" has harness template "HARNESS_BASIC_CLASSIFY_V1"
    When "User2" clicks "Review this definition"
    Then the UI presents 10 harness items one by one
    When "User2" submits the completed harness
    Then the UI creates a Review Evidence Entry and shows "review_evidence_cid"
    And the UI indicates the review is pending assessment

  @phase1 @challenge_flow
  Scenario: Challenge flow lets a user submit a boundary case
    Given user "User3" is authenticated in the UI
    And definition "DEF_A" exists
    When "User3" clicks "Challenge"
    And submits a boundary_item "B1"
    And selects claimed_label "out"
    And enters argument_text "Because..."
    And clicks "Submit challenge"
    Then the UI shows "challenge_cid"
    And the UI shows the assessment window countdown
    And the UI shows the challenge as "Open"

  @phase1 @owner_response_flow
  Scenario: Definition owner responds with clarification or a planned revision
    Given user "OwnerA" owns definition "DEF_A"
    And challenge "CHAL_1" is open for "DEF_A"
    When "OwnerA" opens "CHAL_1"
    Then the UI provides response options:
      | option               |
      | accept_challenge     |
      | reject_challenge     |
      | clarify_definition   |
      | propose_revision     |
    When "OwnerA" submits a response with justification_text
    Then the UI records the response and marks "CHAL_1" as "Awaiting assessment"

  @phase1 @version_update_wizard
  Scenario: Update Definition Wizard requires a diff when semantics change
    Given user "OwnerA" owns definition "DEF_A" with version "v1"
    When "OwnerA" starts "Update Definition"
    And edits the definition_text
    Then the UI requires a "What changed and why?" diff form
    When "OwnerA" submits the update with a diff
    Then the UI publishes a new version "v2" referencing "v1"
    And the UI shows the version history with a link to the diff artifact

  @phase1 @merit_display
  Scenario: UI clearly separates merit from popularity
    Given definition "DEF_A" has merit_score 0.42 and reach_score 1200
    When a user views "DEF_A"
    Then the UI displays merit_score and reach_score separately
    And the UI labels merit_score as "Protocol trust signal"
    And the UI labels reach_score as "Attention signal"
    And the UI does not default-sort by reach_score

  @phase2 @anti_slop_ui_guardrail
  Scenario: UI nudges users toward tests and evidence over commentary
    Given a user is viewing a definition detail page
    When the user attempts to post an unstructured comment
    Then the UI suggests structured alternatives:
      | alternative             |
      | run_a_review_harness    |
      | submit_a_boundary_case  |
      | propose_a_revision_diff |
    And the UI allows unstructured comments only in a clearly separated "discussion" tab


@ui_club_modes @phase0
Feature: UI supports Promise Keeper Club participation modes
  Non-technical users can participate as definers, reviewers, or challengers.

  Background:
    Given a Web UI Agent exists
    And a UserSuccessOnboardingAgent exists

  @phase0 @role_select
  Scenario: User chooses a participation role
    Given a new user "User1" is authenticated
    When "User1" opens the club home page
    Then the UI offers roles:
      | role       |
      | Definer    |
      | Reviewer   |
      | Challenger |
    And the UI explains what each role does and how merit is earned or risked

  @phase0 @definer_mode
  Scenario: Definer mode emphasizes clarity, examples, and harness completeness
    Given "User1" selected role "Definer"
    When "User1" begins creating a definition
    Then the UI enforces minimum completeness:
      | requirement                 |
      | at_least_3_examples          |
      | at_least_3_counterexamples   |
      | harness_selected             |
      | scope_in_and_scope_out        |
    And the UI warns if the definition is too vague with reason "LOW_TESTABILITY"

  @phase0 @reviewer_mode
  Scenario: Reviewer mode shows pending reviews and suggests high-impact work
    Given "User2" selected role "Reviewer"
    And there are definitions with low review_count under "/science"
    When "User2" opens the review dashboard
    Then the UI recommends definitions with:
      | heuristic             |
      | low_review_count      |
      | high_usage_by_consumers|
      | recent_semantic_change |

  @phase0 @challenger_mode
  Scenario: Challenger mode guides toward boundary cases with evidence
    Given "User3" selected role "Challenger"
    When "User3" starts a challenge
    Then the UI prompts for:
      | prompt                |
      | boundary_item         |
      | why_it_is_boundary    |
      | what_outcome_matters  |
      | optional_evidence     |
    And the UI refuses empty challenges with reason "MISSING_ARGUMENT"

  @phase1 @notifications
  Scenario: UI notifications keep the challenge/review loop moving
    Given a user owns definition "DEF_A"
    And a new challenge "CHAL_1" is filed against "DEF_A"
    When the system records "CHAL_1"
    Then the UI notifies the owner with:
      | field            |
      | challenge_link   |
      | deadline         |
      | required_action  |
    And the UI notifies interested reviewers subscribed to "/science"


@ui_accessibility @phase0
Feature: UI is accessible and minimizes technical complexity
  The UI should support non-technical users while preserving protocol integrity.

  @phase0 @no_crypto_expertise_required
  Scenario: The UI manages keys without exposing cryptographic details by default
    Given user "User1" has no technical background
    When "User1" creates an account
    Then the UI generates and stores keys securely
    And the UI offers an export/recovery option
    And the UI does not require the user to understand signatures

  @phase1 @advanced_view
  Scenario: Advanced users can inspect CIDs, signatures, and evidence links
    Given user "PowerUser1" enabled "Advanced mode"
    When "PowerUser1" views definition "DEF_A"
    Then the UI displays:
      | field           |
      | definition_id   |
      | head_state_cid  |
      | signature       |
      | evidence_cids   |
      | assessment_cids |



###
# let's look at this from the POV of a participant in a new form of collective intelligence.  someone who is often online debating terms like 'the metacrisis' and so on finally has a way to simply given this term a definition and see how it will be assessed by others - which specific promises it keeps or breaks
###

# Got it — shift from “protocol mechanics” to what it feels like to participate in a collective intelligence where definitions are testable promises.

Here’s a clean way to frame it:

The core move

A “definition” isn’t just text. It’s a bundle of promises about how the term will behave in discourse and prediction.

So instead of:

“The metacrisis is a civilizational phase shift caused by complexity.”

You publish something like:

A Definition Card for “metacrisis”

Term: metacrisis

Definition (natural language): …

Scope: what it includes / excludes

Predictions / implications: what follows if the definition is true/useful

Operational hooks: what observations or patterns should show up

Failure modes: ways this definition could mislead

Assessment window: e.g., ongoing, with periodic review

Then the key: you explicitly promise properties of your definition.

What “kept” and “broken” mean for definitions

A definition can’t “deliver a package,” but it can keep or break promises like:

Promise types a definition can make

Coherence promise

“My definition is internally consistent and doesn’t contradict itself across examples.”

Broken if: it implies incompatible conclusions in two similar cases.

Boundary promise

“I can classify cases reliably: these are in, these are out.”

Broken if: assessors can generate counterexamples that force ad-hoc patches.

Compression promise

“This term reduces confusion vs alternatives; it’s shorter than the complexity it replaces.”

Broken if: it creates more ambiguity than it resolves.

Explanatory promise

“It explains a set of phenomena better than competing definitions.”

Broken if: it doesn’t add explanatory power beyond vibes.

Predictive promise

“If my definition is correct/useful, we should expect X patterns over Y time.”

Broken if: predictions repeatedly fail or are unfalsifiable.

Pragmatic / coordination promise

“Using this definition helps groups make better decisions / coordinate better.”

Broken if: it reliably causes worse choices or factional confusion.

Non-motte-and-bailey promise

“I won’t slide between a strong and weak meaning depending on pressure.”

Broken if: assessors can show you retreat to a trivial reading when challenged.

That’s how “kept/broken” becomes meaningful for definitions.

What it feels like as a participant

Imagine you’re that person debating “the metacrisis” online. The new move is:

Step 1: You publish your definition as an agent (or a definition-agent)

It has a stable ID and a name like:

/concepts/metacrisis/dj-v1

or /sensemaking/metacrisis/complexity-collapse-v3

You’re not claiming to be the metacrisis. You’re proposing one contender.

Step 2: Other people (and agents) assess it — but not as “agree/disagree”

They assess specific promises:

“Boundary promise: BROKEN — here are 3 cases that break your inclusion rule.”

“Compression promise: KEPT — clearer than ‘polycrisis’ in these contexts.”

“Predictive promise: INCONCLUSIVE — no testable commitments yet.”

So your definition develops a profile rather than a popularity score.

Step 3: The landscape prunes itself

Over time:

definitions that are consistently coherent + useful rise in merit

definitions that rely on vagueness lose merit

multiple definitions can coexist, each strong in different domains

So you get something like:

“Metacrisis (systems-theory sense)” = high merit in /governance, medium in /spirituality

“Metacrisis (integral sense)” = high merit in /personal-development, low in /policy

“Metacrisis (econ-material sense)” = high merit in /macro, low elsewhere

That’s healthy competition without forcing premature consensus.

The “aha”: you’re not debating a word, you’re competing on commitments

Most online debate is:

rhetorical dominance

tribal association

semantic drift

In your system, a definition wins by:

making clear commitments

surviving structured counterexamples

producing useful predictions / coordination gains

with assessors who also have skin in the game

What keeps it from becoming “humanslop”

The criticism you mentioned (“it’s just a human behind it”) matters only if the system rewards mere output.

To avoid that, you reward:

evidence-linked assessment

track-recorded assessors

stakes / accountability

meta-review

Then a human behind it is fine — because the collective intelligence isn’t “LLMs talking,” it’s a market of accountable claims.

If you want to sharpen this into protocol objects, the cleanest mapping is:

Definition Card = a special Promise Card type

Definition Promises = a standardized set of promise dimensions (coherence/boundary/compression/etc.)

Assessment Card = per-dimension verdicts + evidence links + stake

Merit = tracked per domain and per promise dimension

And if you want an even more “alive” experience: the UI can show your definition as a radar chart of promise-keeping over time, with drill-down to the exact assessment entries and counterexamples that moved it.
