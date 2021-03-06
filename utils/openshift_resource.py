import copy
import hashlib
import json


class OpenshiftResource(object):
    def __init__(self, body, integration, integration_version):
        self.body = body
        self.integration = integration
        self.integration_version = integration_version

    @property
    def name(self):
        return self.body['metadata']['name']

    @property
    def kind(self):
        return self.body['kind']

    def verify_valid_k8s_object(self):
        self.name
        self.kind

    def has_qontract_annotations(self):
        try:
            annotations = self.body['metadata']['annotations']

            assert annotations['qontract.integration'] == self.integration
            assert annotations['qontract.integration_version'] == \
                self.integration_version
            assert annotations['qontract.sha256sum'] is not None
        except KeyError:
            return False
        except AssertionError:
            return False

        return True

    def annotate(self):
        """
        Creates a OpenshiftResource with the qontract annotations, and removes
        unneeded Openshift fields.

        Returns:
            openshift_resource: new OpenshiftResource object with
                annotations.
        """

        # calculate sha256sum of canonical body
        canonical_body = self.canonicalize(self.body)
        sha256sum = self.calculate_sha256sum(self.serialize(canonical_body))

        # create new body object
        body = copy.deepcopy(self.body)

        # create annotations if not present
        body['metadata'].setdefault('annotations', {})
        annotations = body['metadata']['annotations']

        # add qontract annotations
        annotations['qontract.integration'] = self.integration
        annotations['qontract.integration_version'] = \
            self.integration_version
        annotations['qontract.sha256sum'] = sha256sum

        return OpenshiftResource(body, self.integration,
                                 self.integration_version)

    def sha256sum(self):
        if self.has_qontract_annotations():
            body = self.body
        else:
            body = self.annotate().body

        annotations = body['metadata']['annotations']
        return annotations['qontract.sha256sum']

    def toJSON(self):
        return self.serialize(self.body)

    @staticmethod
    def canonicalize(body):
        body = copy.deepcopy(body)

        # create annotations if not present
        body['metadata'].setdefault('annotations', {})
        annotations = body['metadata']['annotations']

        # remove openshift specific params
        body['metadata'].pop('creationTimestamp', None)
        body['metadata'].pop('resourceVersion', None)
        body['metadata'].pop('selfLink', None)
        body['metadata'].pop('uid', None)
        body['metadata'].pop('namespace', None)
        annotations.pop('kubectl.kubernetes.io/last-applied-configuration',
                        None)

        # Default fields for specific resource types
        # ConfigMaps are by default Opaque
        if body['kind'] == 'ConfigMap' and body.get('type') == 'Opaque':
            body.pop('type')

        # remove qontract specific params
        annotations.pop('qontract.integration', None)
        annotations.pop('qontract.integration_version', None)
        annotations.pop('qontract.sha256sum', None)

        return body

    @staticmethod
    def serialize(body):
        return json.dumps(body, sort_keys=True)

    @staticmethod
    def calculate_sha256sum(body):
        m = hashlib.sha256()
        m.update(body.encode('utf-8'))
        return m.hexdigest()
