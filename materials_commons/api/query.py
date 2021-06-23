PROCESS_FIELD = 1
SAMPLE_FIELD = 2
PROCESS_ATTR_FIELD = 3
SAMPLE_ATTR_FIELD = 4
PROCESS_FUNC = 5
SAMPLE_FUNC = 6

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


def q_sample_has_process(process):
    return q_sample_proc('has-process', process)


def q_sample_proc(proc, value):
    return q_match('', SAMPLE_FUNC, value, proc)


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
