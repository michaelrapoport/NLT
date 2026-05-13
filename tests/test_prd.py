from nlt.prd import parse_prd


def test_parse_prd_extracts_features_with_priority_and_criteria():
    document = parse_prd(
        """
# Product

## Feature: User onboarding
Priority: high

Users can create an account.

Acceptance Criteria:
- [ ] New users can register with email.
- [x] Returning users can sign in.

## Requirement: Reporting dashboard
Prio: Medium

Leaders can see weekly progress.
- This bullet stays in the description unless under acceptance criteria.
""",
        source="test-prd.md",
    )

    assert document.source == "test-prd.md"
    assert len(document.features) == 2
    assert document.features[0].slug == "user-onboarding"
    assert document.features[0].priority == "high"
    assert document.features[0].description == "Users can create an account."
    assert [criterion.text for criterion in document.features[0].acceptance_criteria] == [
        "New users can register with email.",
        "Returning users can sign in.",
    ]
    assert document.features[0].acceptance_criteria[1].completed is True
    assert document.features[1].title == "Reporting dashboard"
    assert document.features[1].priority == "medium"


def test_parse_prd_supports_plain_acceptance_bullets():
    document = parse_prd(
        """
### Epic: Notifications

Acceptance Criteria
- Email notifications are sent within one minute.
* Failed notification attempts are visible to support.
"""
    )

    assert document.features[0].slug == "notifications"
    assert [criterion.text for criterion in document.features[0].acceptance_criteria] == [
        "Email notifications are sent within one minute.",
        "Failed notification attempts are visible to support.",
    ]


def test_parse_prd_returns_empty_backlog_when_no_feature_sections_exist():
    document = parse_prd("# Vision\n\nThis is an overview only.")

    assert document.features == ()


def test_parse_prd_ignores_headings_inside_fenced_code_blocks():
    document = parse_prd(
        """
## Feature: Real feature

The parser should ignore example Markdown headings in code fences.

```markdown
## Feature: Example only
Priority: low
```
"""
    )

    assert [feature.title for feature in document.features] == ["Real feature"]
    assert "Example only" not in document.features[0].description
