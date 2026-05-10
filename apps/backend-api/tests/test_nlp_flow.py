from app.nlp.parser import infer_cohort_from_student_id, parse_command
from app.nlp.processor import CommandProcessor


def test_infer_cohort_from_student_id():
    assert infer_cohort_from_student_id("ITITWE22009") == "k22"
    assert infer_cohort_from_student_id("ITCSIU22001") == "k22"
    assert infer_cohort_from_student_id("ITITIU21123") == "k21"
    assert infer_cohort_from_student_id("ITDSIU22999") == "k22"


def test_course_query_it094_previous():
    parsed = parse_command("IT094IU cần học gì trước?", student_id="ITCSIU22001")
    result = CommandProcessor().process(parsed)

    assert result["intent"] == "ASK_COURSE_REQUIREMENTS"
    assert result["data"]["course_code"] == "IT094IU"
    assert result["data"]["previous"] == ["IT079IU"]
    assert result["reply"].startswith("Môn IT094IU")


def test_course_query_it159_previous():
    parsed = parse_command("IT159IU cần học gì trước?", student_id="ITCSIU22001")
    result = CommandProcessor().process(parsed)

    assert result["intent"] == "ASK_COURSE_REQUIREMENTS"
    assert result["data"]["course_code"] == "IT159IU"
    assert result["data"]["previous"] == ["IT153IU"]


def test_course_query_pe019_previous():
    parsed = parse_command("PE019IU cần học gì trước?", student_id="ITCSIU22001")
    result = CommandProcessor().process(parsed)

    assert result["intent"] == "ASK_COURSE_REQUIREMENTS"
    assert result["data"]["course_code"] == "PE019IU"
    assert result["data"]["previous"] == ["PE017IU"]


def test_course_query_it017_prerequisites():
    parsed = parse_command("IT017IU cần học gì trước?", student_id="ITCSIU22001")
    result = CommandProcessor().process(parsed)

    assert result["intent"] == "ASK_COURSE_REQUIREMENTS"
    assert result["data"]["course_code"] == "IT017IU"
    assert "IT013IU" in result["data"]["prerequisites"]


def test_course_query_it093_prerequisites():
    parsed = parse_command("IT093IU cần học gì trước?", student_id="ITCSIU22001")
    result = CommandProcessor().process(parsed)

    assert result["intent"] == "ASK_COURSE_REQUIREMENTS"
    assert result["data"]["course_code"] == "IT093IU"
    assert set(result["data"]["prerequisites"]) == {"IT079IU", "IT069IU"}
