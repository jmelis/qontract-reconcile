import semver

import reconcile.openshift_resources_base as orb

QONTRACT_INTEGRATION = 'openshift-vault-secrets'
QONTRACT_INTEGRATION_VERSION = semver.format_version(1, 9, 3)


def run(dry_run, thread_pool_size=10, internal=None,
        use_jump_host=True, defer=None):
    providers = ['vault-secret']
    orb.QONTRACT_INTEGRATION = QONTRACT_INTEGRATION
    orb.QONTRACT_INTEGRATION_VERSION = QONTRACT_INTEGRATION_VERSION

    orb.run(dry_run=dry_run,
            thread_pool_size=thread_pool_size,
            internal=internal,
            use_jump_host=use_jump_host,
            providers=providers)
