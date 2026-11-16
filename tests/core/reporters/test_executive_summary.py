from core.reporters.sections.executive_summary import ExecutiveSummarySection


def _render(data):
    sec = ExecutiveSummarySection.__new__(ExecutiveSummarySection)
    sec.analysis_data = data
    return sec.render()


def test_counts_are_articles_reviewed_not_threats():
    out = _render({"categorized_counts": {"telecom": 9, "general": 27},
                   "reddit_community_summary": "x", "reddit_posts_analyzed": 5})
    assert "**9** telecom fraud articles reviewed" in out
    assert "**27** general security articles reviewed" in out
    assert "**5** Reddit posts analyzed" in out
    assert "threats** identified" not in out


def test_singular_forms():
    out = _render({"categorized_counts": {"telecom": 1, "general": 0},
                   "reddit_community_summary": "x", "reddit_posts_analyzed": 1})
    assert "**1** telecom fraud article reviewed" in out
    assert "**1** Reddit post analyzed" in out
