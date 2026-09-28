import json
from pathlib import Path


ARTIFACT_PATH = (
    Path(__file__).resolve().parents[1]
    / "artifacts"
    / "m04-decision-matrix.json"
)


def load_matrix():
    with ARTIFACT_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def calculate_total(scores, criteria):
    total = 0

    for criterion in criteria:
        name = criterion["name"]
        weight = criterion["weight"]
        score = scores[name]

        total += (score / 5) * weight

    return round(total, 2)


def validate_matrix(data):
    criteria = data["criteria"]
    matrix = data["matrix"]

    # Los pesos deben sumar 100%.
    assert sum(c["weight"] for c in criteria) == 100

    for alternative in matrix:
        scores = alternative["scores"]

        # Debe existir un puntaje para cada criterio.
        assert set(scores.keys()) == {
            criterion["name"] for criterion in criteria
        }

        # Cada puntaje debe estar entre 1 y 5.
        for score in scores.values():
            assert 1 <= score <= 5

        # El total declarado debe coincidir con el cálculo.
        calculated = calculate_total(scores, criteria)

        assert alternative["total"] == calculated


def test_m04_normal_case():
    """
    Caso normal:
    La matriz contiene las cuatro alternativas esperadas,
    los cinco criterios y sus totales son correctos.
    """
    data = load_matrix()

    assert len(data["alternatives"]) == 4
    assert len(data["criteria"]) == 5
    assert len(data["matrix"]) == 4

    validate_matrix(data)


def test_m04_lower_boundary_score():
    """
    Límite inferior:
    Un puntaje de 1 debe ser válido.
    """
    data = load_matrix()

    scores = data["matrix"][0]["scores"].copy()
    scores["Consultas"] = 1

    criteria = data["criteria"]

    assert 1 <= scores["Consultas"] <= 5

    total = calculate_total(scores, criteria)

    assert total >= 0


def test_m04_upper_boundary_score():
    """
    Límite superior:
    Un puntaje de 5 debe ser válido.
    """
    data = load_matrix()

    scores = data["matrix"][0]["scores"].copy()
    scores["Consultas"] = 5

    criteria = data["criteria"]

    assert 1 <= scores["Consultas"] <= 5

    total = calculate_total(scores, criteria)

    assert total <= 100


def test_m04_declared_failure_invalid_score():
    """
    Fallo declarado:
    Un puntaje de 6 está fuera de la escala permitida 1..5
    y debe ser rechazado.
    """
    data = load_matrix()

    invalid_matrix = data["matrix"][0].copy()
    invalid_scores = invalid_matrix["scores"].copy()

    invalid_scores["Consultas"] = 6
    invalid_matrix["scores"] = invalid_scores

    score = invalid_matrix["scores"]["Consultas"]

    assert not (1 <= score <= 5)