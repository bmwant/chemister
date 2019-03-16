from notebooks.cardrive.carmax_q_learning import Agent


def test_to_state_conversion():
    assert Agent.to_state(step=0, tank=10) == 1
    assert Agent.to_state(step=1, tank=20) == 9
    assert Agent.to_state(step=2, tank=40) == 18
    assert Agent.to_state(step=4, tank=10) == 29
    assert Agent.to_state(step=4, tank=60) == 34
    assert Agent.to_state(step=5, tank=30) == 38
    assert Agent.to_state(step=6, tank=0) == 42
    assert Agent.to_state(step=6, tank=50) == 47
    assert Agent.to_state(step=8, tank=60) == 62
    assert Agent.to_state(step=9, tank=60) == 69


def test_from_state_conversion():
    assert Agent.from_state(0) == (0, 0)
    assert Agent.from_state(8) == (1, 10)
    assert Agent.from_state(19) == (2, 50)
    assert Agent.from_state(30) == (4, 20)
    assert Agent.from_state(33) == (4, 50)
    assert Agent.from_state(39) == (5, 40)
    assert Agent.from_state(43) == (6, 10)
    assert Agent.from_state(48) == (6, 60)
    assert Agent.from_state(61) == (8, 50)
    assert Agent.from_state(68) == (9, 50)


def test_get_available_actions():
    assert Agent.get_available_actions(62) == [3, 4, 5, 6]
    assert Agent.get_available_actions(61) == [2, 3, 4, 5, 6]
