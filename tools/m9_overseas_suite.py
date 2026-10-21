"""Same native resolution gate with the immutable Overseas profile."""
import campaign_suite as campaign
import m9_resolution_suite as base


def fixture(token, fingerprint):
    start, finish, instant, cases = base.fixture(token, fingerprint)
    return start.replace('name = bfl_profile value = 1', 'name = bfl_profile value = 2'), finish, instant, cases


if __name__ == '__main__':
    campaign.fixture = fixture
    campaign.reload_fixture = base.reload_fixture
    campaign.prepare = base.prepare
    campaign.main()
