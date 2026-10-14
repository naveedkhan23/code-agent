from pathlib import Path

from code_agent.preprocess import build_structured_input, parse_diagram

EX = Path(__file__).parent.parent / "examples"


def load():
    return build_structured_input((EX / "Architecture_Documentation.md").read_text(encoding="utf-8"),
                                  (EX / "Architecture_View.md").read_text(encoding="utf-8"))


def test_documentation_sections_and_requirements():
    d = load()["documentation"]
    assert d["title"].startswith("Tetris")
    assert d["section_count"] >= 4
    assert any("seven standard tetrominoes" in r for r in d["requirements"])
    assert "python" in d["tech_mentions"] and "tkinter" in d["tech_mentions"]
    arch = next(s for s in d["sections"] if s["title"] == "3. Architecture")
    assert arch["tables"] and arch["tables"][0][0] == ["Component", "Responsibility"]


def test_class_diagram_parsed():
    v = load()["views"]
    cls = next(x for x in v["views"] if x["parsed"]["type"] == "class")["parsed"]
    assert set(cls["classes"]) >= {"Tetromino", "GameEngine", "GameController", "GameWindow", "HighScoreStore"}
    assert "+hard_drop(): int" in cls["classes"]["GameEngine"]["members"]
    rel = {(r["from"], r["to"], r["arrow"]) for r in cls["relations"]}
    assert ("GameController", "GameEngine", "-->") in rel
    assert ("GameEngine", "Tetromino", "*--") in rel


def test_sequence_and_state_diagrams():
    v = load()["views"]
    assert v["types"] == ["class", "sequence", "state"]
    seq = next(x for x in v["views"] if x["parsed"]["type"] == "sequence")["parsed"]
    assert seq["participants"] == ["GameController", "GameEngine", "GameWindow"]
    assert [m["message"] for m in seq["messages"]][0] == "move(0, 1)"
    st = next(x for x in v["views"] if x["parsed"]["type"] == "state")["parsed"]
    assert {"from": "Running", "to": "Paused", "label": "press P"} in st["edges"]


def test_mermaid_class_and_flowchart():
    p = parse_diagram("mermaid", "classDiagram\nclass A\nclass B\nA <|-- B : extends")
    assert p["type"] == "class" and p["relations"][0]["label"] == "extends"
    f = parse_diagram("mermaid", "flowchart TD\n A[Start] --> B{Ok?}\n B -->|yes| C[Done]")
    assert f["type"] == "flowchart" and len(f["edges"]) == 2


def test_no_fences_falls_back_to_whole_file():
    v = build_structured_input("# T", "class A\nclass B\nA --> B")["views"]
    assert v["view_count"] == 1 and v["views"][0]["parsed"]["type"] == "class"


def test_space_fractions_view_types():
    d = EX / "space_fractions"
    r = build_structured_input((d / "Architecture_Documentation.md").read_text(encoding="utf-8"),
                               (d / "Architecture_View.md").read_text(encoding="utf-8"))
    views = {v["parsed"]["name"]: v for v in r["views"]["views"]}
    types = {n: v["parsed"]["type"] for n, v in views.items()}
    assert types == {"UseCaseDiagram": "usecase", "ClassDiagram": "class", "ObjectDiagram": "object",
                     "StateDiagram": "state", "ActivityDiagram": "activity", "SequenceDiagram1": "sequence",
                     "SequenceDiagram2": "sequence", "CollaborationDiagram2": "collaboration",
                     "PackageDiagram": "package", "ComponentDiagram": "component",
                     "DeploymentDiagram": "deployment", "ContainerDiagram": "container"}
    uc = views["UseCaseDiagram"]["parsed"]
    assert {"from": "EndUser", "to": "PlayGame", "label": ""} in uc["edges"]
    assert any(e["kind"] == "usecase" and e["alias"] == "PlayGame" for e in uc["elements"])
    assert views["UseCaseDiagram"]["title"].startswith("1. UseCase")
    cls = views["ClassDiagram"]["parsed"]
    assert set(cls["classes"]) == {"Game", "Question", "User", "Admin"} and len(cls["relations"]) == 3
    st = views["StateDiagram"]["parsed"]
    assert {"from": "[*]", "to": "Playing", "label": ""} in st["edges"]
    assert views["SequenceDiagram1"]["parsed"]["messages"][0]["message"] == "play()"
    assert views["CollaborationDiagram2"]["parsed"]["notes"] == ["Scenario: Update Questions"]
    assert views["ActivityDiagram"]["parsed"]["steps"][0] == "start"
    pk = views["PackageDiagram"]["parsed"]
    assert any(e.get("parent") == "Game" and e["name"] == "Question" for e in pk["elements"])
    assert len(views["DeploymentDiagram"]["parsed"]["edges"]) == 3


def test_space_fractions_documentation():
    d = EX / "space_fractions"
    doc = build_structured_input((d / "Architecture_Documentation.md").read_text(encoding="utf-8"), "")["documentation"]
    assert doc["requirement_ids"] == ["ASR-1", "FR-1", "NFR-1"]
    assert doc["traceability"][0]["Component(s)"] == "GameComponent"
    d_sec = next(s for s in doc["sections"] if s["title"] == "Data model / schema")
    assert d_sec["code_blocks"][0]["lang"] == "sql" and "CREATE TABLE games" in d_sec["code_blocks"][0]["code"]
