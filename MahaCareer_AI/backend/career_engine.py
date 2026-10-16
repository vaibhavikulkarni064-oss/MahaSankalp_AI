"""Transparent rule-based scoring. NOT machine learning.
Each career has keywords. A keyword found in an answer earns the field's weight in points.
Score = 100 * points / (points + 6), capped at 95, so scores show relative fit, never certainty."""
WEIGHTS = {"interests": 3, "existing_skills": 2, "career_goals": 2, "favourite_subjects": 1,
           "industries": 1, "desired_skills": 1, "field_of_study": 1}
DISCLAIMER = ("These are preliminary suggestions based only on what you entered. They are not a final decision, "
              "and do not predict jobs, salaries, admissions or success. Talk to teachers, mentors and counsellors too.")

def _text(a, f):
    v = a.get(f) or ""
    return (" ".join(v) if isinstance(v, list) else v).lower()

def score_career(a, c):
    pts, hits = 0, []
    for f, w in WEIGHTS.items():
        t = _text(a, f)
        for kw in c["keywords"]:
            if kw.lower() in t:
                pts += w; hits.append((f, kw))
    return pts, hits

def completeness(a):
    checks = [a.get("favourite_subjects"), a.get("interests"), a.get("existing_skills"), a.get("desired_skills"),
              a.get("industries"), len(a.get("career_goals", "")) >= 40, a.get("experience"), a.get("field_of_study"), a.get("work_style")]
    return round(100 * sum(1 for x in checks if x) / len(checks))

def analyze(a, catalogue):
    scored = [(*score_career(a, c)[:1], c, score_career(a, c)[1]) for c in catalogue]
    scored.sort(key=lambda x: (-x[0], x[1]["id"]))
    def s(p): return min(95, round(100 * p / (p + 6))) if p else 0
    def why(c, hits):
        if not hits:
            return f"None of your answers matched {c['career_name']} keywords, so this is only a starting point to explore."
        fields = sorted({f.replace("_", " ") for f, _ in hits})
        kws = sorted({k for _, k in hits})
        return f"Matched on {', '.join(fields)} (keywords: {', '.join(kws)}). {c['description']}"
    top_pts, top, hits = scored[0]
    have = _text(a, "existing_skills") + " " + _text(a, "experience")
    strengths = [k for k in top["required_skills"] if k.lower() in have]
    improve = [k for k in top["required_skills"] if k not in strengths][:5]
    t = top["recommended_learning_topics"]
    weeks = [("Week 1 - Foundations", t[0]), ("Week 2 - Core skills", t[1]), ("Week 3 - Practice", t[2]),
             ("Week 4 - Build and review", "Build: " + top["project_ideas"][0])]
    roadmap = [{"week": w, "focus": f, "tasks": [f"Study 45-60 minutes a day on: {f}.", "Write 3 short notes on what you learned.", "Finish one small practice exercise."]} for w, f in weeks]
    return {
        "name": a["name"],
        "recommended": {"career": top["career_name"], "score": s(top_pts), "explanation": why(top, hits),
            "strengths": strengths, "skills_to_improve": improve, "topics": t, "projects": top["project_ideas"],
            "education": top["education_guidance"]},
        "alternatives": [{"career": c["career_name"], "score": s(p), "explanation": why(c, h)} for p, c, h in scored[1:4]],
        "roadmap": roadmap,
        "next_steps": ["Try the week-1 tasks and see whether you enjoy them.", "Talk to someone working in this field.",
                       "Re-take the assessment after a month as your interests change."] +
                      (["Add more interests and skills to get a more meaningful result."] if top_pts == 0 else []),
        "completeness": completeness(a),
        "score_note": "Suitability score = how closely your answers match this career's keywords (relative, not a prediction). Profile completeness = how much of the form you filled in.",
        "disclaimer": DISCLAIMER,
    }
