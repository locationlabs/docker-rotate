from docker import Client
from mock import create_autospec

from dockerrotate.containers import determine_containers_to_remove
from dockerrotate.main import parse_arguments
from utils import created_container_entry, exited_container_entry, \
                  dead_container_entry, running_container_entry, mins_ago, \
                  containers_result


IID = "sha256:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb01"

CID1 = "sha256:cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc01"
CID2 = "sha256:cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc02"
CID3 = "sha256:cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc03"
CID4 = "sha256:cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc04"
CID5 = "sha256:cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc05"
CID6 = "sha256:cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc06"


def _assert_ids(containers, *container_ids):
    assert set(container["Id"] for container in containers) == set(container_ids)

    # make sure there aren't repeats in the list to delete, too.
    assert len(containers) == len(container_ids)


def _mock_containers(containers, args):
    mock_client = create_autospec(Client)
    mock_client.containers.return_value = containers_result(containers)
    lookup = {container["Id"]: container for container in containers}

    mock_client.inspect_container.side_effect = lambda container_id: lookup[container_id]
    args.client = mock_client


def test_created():
    containers = [
        created_container_entry(CID1, IID, mins_ago(2465)),
        created_container_entry(CID2, IID, mins_ago(61)),
        created_container_entry(CID3, IID, mins_ago(25)),
        running_container_entry(CID4, IID, mins_ago(2465)),
        exited_container_entry(CID5, IID, mins_ago(2001)),
        dead_container_entry(CID6, IID, mins_ago(2011))
    ]
    args = parse_arguments(['containers', '--created', '1h'])
    _mock_containers(containers, args)
    result = determine_containers_to_remove(args)
    _assert_ids(result, CID1, CID2)


def test_created_zero_timestamp():
    containers = [
        created_container_entry(CID1, IID, mins_ago(2465)),
        created_container_entry(CID2, IID, mins_ago(61)),
        created_container_entry(CID3, IID, mins_ago(25)),
        running_container_entry(CID4, IID, mins_ago(2465)),
        exited_container_entry(CID5, IID, mins_ago(2001)),
        dead_container_entry(CID6, IID, mins_ago(2011))
    ]
    args = parse_arguments(['containers', '--created', '0'])
    _mock_containers(containers, args)
    result = determine_containers_to_remove(args)
    _assert_ids(result, CID1, CID2, CID3)


def test_exited():
    containers = [
        exited_container_entry(CID1, IID, mins_ago(2465)),
        exited_container_entry(CID2, IID, mins_ago(61)),
        exited_container_entry(CID3, IID, mins_ago(25)),
        running_container_entry(CID4, IID, mins_ago(2465)),
        created_container_entry(CID5, IID, mins_ago(2001)),
        dead_container_entry(CID6, IID, mins_ago(2011))
    ]
    args = parse_arguments(['containers', '--exited', '1h'])
    _mock_containers(containers, args)
    result = determine_containers_to_remove(args)
    _assert_ids(result, CID1, CID2)


def test_dead():
    containers = [
        dead_container_entry(CID1, IID, mins_ago(2465)),
        dead_container_entry(CID2, IID, mins_ago(61)),
        dead_container_entry(CID3, IID, mins_ago(25)),
        running_container_entry(CID4, IID, mins_ago(2465)),
        created_container_entry(CID5, IID, mins_ago(2001)),
        exited_container_entry(CID6, IID, mins_ago(2011))
    ]
    args = parse_arguments(['containers', '--dead', '1h'])
    _mock_containers(containers, args)
    result = determine_containers_to_remove(args)
    _assert_ids(result, CID1, CID2)
