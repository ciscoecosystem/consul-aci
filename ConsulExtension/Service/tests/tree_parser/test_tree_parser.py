import pytest
import json
from Service import tree_parser


'''
Case1: Dangeling node
Case2: All the data having ipv6 addresses
Case3: Service with different ip as that of Node which mappes to Some EP
Case4: Service with different ip as that of Node which DOES NOT map to any EP
Case5: Service with no ip
Case6: All above combinations
'''
cases = [
    "dangling",
    "ipv6",
    "service_to_ep",
    "service_to_none",
    "service_without_ip",
    "random_combination"
]


def get_data(in_out, case):
    with open('./tests/tree_parser/data/{}/{}.json'.format(in_out, case), 'r') as f:
        return json.load(f)


checks = [
    [
        {
            "passing": 1,
            "warning": 2,
            "failing": 2
        },
        {
            "passing": 5,
            "warning": 9,
            "failing": 4
        }
    ],
    [
        {
            "passing": 1,
            "warning": 2,
        },
        {
            "passing": 4,
            "warning": 3,
        }
    ],
    [
        {
            "warning": 3,
        },
        {
            "warning": 2,
        }
    ],
    [
        {
            "warning": 7,
        },
        {
            "passing": 2,
        }
    ],
    [
        {
        },
        {
        }
    ],
    [
        {
            "passing": 0,
            "warning": 0,
            "failing": 0
        },
        {
        }
    ]
]


@pytest.mark.parametrize("case", cases)
def test_consul_tree_dict(case):
    input_data = get_data('input', case)
    original_output = get_data('output', case)
    response = tree_parser.consul_tree_dict(input_data)

    for each in original_output:
        assert each in response


@pytest.mark.parametrize("check", checks)
def test_add_checks(check):
    base_checks, new_checks = check
    passing = base_checks.get('passing', 0) \
        + new_checks.get('passing', 0)
    warning = base_checks.get('warning', 0) \
        + new_checks.get('warning', 0)
    failing = base_checks.get('failing', 0) \
        + new_checks.get('failing', 0)

    response = tree_parser.add_checks(base_checks, new_checks)

    assert response.get('passing', 0) == passing
    assert response.get('warning', 0) == warning
    assert response.get('failing', 0) == failing
