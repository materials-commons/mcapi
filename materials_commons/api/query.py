PROCESS_FIELD = 1
SAMPLE_FIELD = 2
PROCESS_ATTR_FIELD = 3
SAMPLE_ATTR_FIELD = 4

OP_EQ = "="
OP_NEQ = "<>"
OP_LT = "<"
OP_LTEQ = "<="
OP_GT = ">"
OP_GTEQ = ">="


def q_and(left, right):
    return {
        "and": 1,
        "left": left,
        "right": right
    }


def q_or(left, right):
    return {
        "or": 1,
        "left": left,
        "right": right
    }


def q_sample_match(field, value, operation):
    return q_match(field, SAMPLE_FIELD, value, operation)


def q_sample_attr_match(field, value, operation):
    return q_match(field, SAMPLE_ATTR_FIELD, value, operation)


def q_process_match(field, value, operation):
    return q_match(field, PROCESS_FIELD, value, operation)


def q_process_attr_match(field, value, operation):
    return q_match(field, PROCESS_ATTR_FIELD, value, operation)


def q_match(field, field_type, value, operation):
    return {
        "field_name": field,
        "field_type": field_type,
        "value": value,
        "operation": operation
    }


def get_query_results(project_id, query):
    return [], []


q = q_and(
    left=q_and(
        left=q_process_attr_match("voltage", 5, OP_GTEQ),
        right=q_process_attr_match("magnification", "5x", OP_EQ)
    ),
    right=q_or(
        left=q_process_match("name", "SEM", OP_EQ),
        right=q_process_match("name", "EBSD", OP_EQ)
    )
)


results = get_query_results(77, q)
